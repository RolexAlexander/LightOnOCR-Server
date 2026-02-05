import io
from typing import List

import torch
from PIL import Image
import pypdfium2 as pdfium

from transformers import (
    LightOnOcrForConditionalGeneration,
    LightOnOcrProcessor,
)

# ---------- Model bootstrap (loaded once per worker) ----------

DEVICE = (
    "mps" 
    if torch.backends.mps.is_available() 
    else "cuda" 
    if torch.cuda.is_available() 
    else "cpu"
)

DTYPE = torch.float32 if DEVICE == "mps" else torch.bfloat16

MODEL_ID = "lightonai/LightOnOCR-2-1B"

model = LightOnOcrForConditionalGeneration.from_pretrained(
    MODEL_ID, torch_dtype=DTYPE
).to(DEVICE)

processor = LightOnOcrProcessor.from_pretrained(MODEL_ID)


# ---------- Helpers ----------

def _pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
    """
    Convert PDF bytes to PIL images at ~200 DPI.
    """
    pdf = pdfium.PdfDocument(pdf_bytes)
    images = []

    scale = 200 / 72  # approx 2.78 (recommended)
    for page in pdf:
        pil_img = page.render(scale=scale).to_pil()
        images.append(pil_img)

    return images


def _ocr_image(image: Image.Image) -> str:
    """
    Run LightOnOCR on a single PIL image.
    """
    conversation = [
        {
            "role": "user",
            "content": [{"type": "image", "image": image}],
        }
    ]

    inputs = processor.apply_chat_template(
        conversation,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )

    inputs = {
        k: v.to(DEVICE, dtype=DTYPE) if v.is_floating_point() else v.to(DEVICE)
        for k, v in inputs.items()
    }

    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=2048)

    generated_ids = output_ids[0, inputs["input_ids"].shape[1] :]
    return processor.decode(generated_ids, skip_special_tokens=True)


# ---------- RQ Task (Consumer) ----------

def process_ocr(file_bytes: bytes):
    """
    RQ consumer entrypoint.
    Receives raw bytes from FastAPI producer.
    """
    try:
        # Detect file type
        if file_bytes[:4] == b"%PDF":
            images = _pdf_to_images(file_bytes)
        else:
            images = [Image.open(io.BytesIO(file_bytes)).convert("RGB")]

        results = []
        for idx, img in enumerate(images):
            text = _ocr_image(img)
            results.append(
                {
                    "page": idx + 1,
                    "text": text.strip(),
                }
            )

        return {
            "pages": len(results),
            "content": results,
        }

    except Exception as e:
        # RQ will retry automatically because you set Retry(...)
        raise RuntimeError(f"OCR failed: {e}")
