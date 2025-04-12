import argparse
import os
from util import docling


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Convert PDFs to Markdown using Docling."
    )
    parser.add_argument("input_path", help="Directory containing PDF files.")
    parser.add_argument(
        "output_path", help="Directory to save converted Markdown files."
    )
    parser.add_argument(
        "--mode",
        choices=["default", "ocr", "mac_ocr"],
        default="default",
        help="Conversion mode: 'default' (standard) or 'mac_ocr' (Mac OCR).",
    )

    args = parser.parse_args()

    # Ensure input path exists
    if not os.path.isdir(args.input_path):
        print(
            f"Error: Input path '{args.input_path}' is not a directory or does not exist."
        )
        return

    # Ensure output directory exists
    os.makedirs(args.output_path, exist_ok=True)

    # Initialize the converter with the selected mode
    converter = docling.PDFConverter(mode=args.mode)

    # Convert all PDFs in the input directory to Markdown in the output directory
    converter.convert_pdf(args.input_path, args.output_path)


if __name__ == "__main__":
    main()
