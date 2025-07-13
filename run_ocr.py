import argparse
import sys
from pathlib import Path
from typing import List

from edu.ocr import ocr_pdf


def find_pdfs_to_ocr(directory: Path) -> List[Path]:
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    all_pdfs = list(directory.rglob("*.pdf"))

    pdfs_to_ocr = []
    for pdf_file in all_pdfs:
        if pdf_file.stem.endswith("_OCR"):
            continue

        ocr_version = pdf_file.parent / f"{pdf_file.stem}_OCR.pdf"
        if not ocr_version.exists():
            pdfs_to_ocr.append(pdf_file)

    return pdfs_to_ocr


def main():
    parser = argparse.ArgumentParser(
        description="OCR all PDF files in a directory that don't already have OCR versions.",
        epilog="Example: python ocr.py ./downloads",
    )
    parser.add_argument(
        "directory", type=str, help="Path to the directory containing PDF files to OCR"
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="deu+eng",
        help="OCR language codes (default: deu+eng)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which files would be processed without actually doing OCR",
    )

    args = parser.parse_args()

    try:
        directory = Path(args.directory).resolve()
        print(f"Searching for PDFs in: {directory}")

        pdfs_to_process = find_pdfs_to_ocr(directory)
        if not pdfs_to_process:
            print("No PDF files found that need OCR processing.")
            return

        print(f"Found {len(pdfs_to_process)} PDF(s) to process:")
        for pdf_file in pdfs_to_process:
            print(f"  - {pdf_file.name}")

        if args.dry_run:
            print("\nDry run mode - no files will be processed.")
            return

        # Process each PDF
        print(f"\nStarting OCR processing with language: {args.lang}")
        for i, pdf_file in enumerate(pdfs_to_process, 1):
            print(f"\n[{i}/{len(pdfs_to_process)}] Processing: {pdf_file.name}")
            try:
                ocr_pdf(str(pdf_file), lang=args.lang)
                print(f"✓ Successfully processed: {pdf_file.name}")
            except Exception as e:
                print(f"✗ Failed to process {pdf_file.name}: {e}")
                continue

        print(f"\nOCR processing completed. Processed {len(pdfs_to_process)} files.")

    except Exception as e:
        print(f"Exception: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
