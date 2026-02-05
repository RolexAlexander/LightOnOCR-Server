import argparse
import json
from pathlib import Path


def _build_markdown_lines(data: dict) -> list[str]:
    markdown_lines: list[str] = []
    for item in data.get("result", {}).get("content", []):
        page_num = item.get("page", "N/A")
        text = str(item.get("text", "")).strip()
        markdown_lines.append(f"## Page {page_num}\n")
        markdown_lines.append(f"{text}\n\n")
    return markdown_lines


def convert_json_to_markdown(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    markdown_lines = _build_markdown_lines(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(markdown_lines), encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert OCR JSON output to a Markdown file."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the OCR JSON file (e.g., z.json).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Path to write the Markdown file. Defaults to <input>.md in the same folder.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    input_path: Path = args.input
    output_path: Path = args.output or input_path.with_suffix(".md")

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    convert_json_to_markdown(input_path, output_path)
    print(f"Markdown written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
