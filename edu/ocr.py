import os
import ocrmypdf


def ocr_pdf(in_path: str, lang="deu+eng") -> None:
    try:
        out_path = in_path.replace(".pdf", "_OCR.pdf")
        assert not os.path.exists(out_path), f"Output file {out_path} already exists"

        ocrmypdf.ocr(
            input_file=in_path,
            output_file=out_path,
            language=lang,
            output_type="pdf",
            use_threads=False,
            jobs=max(1, os.cpu_count() - 2),
            progress_bar=True,
        )

        print(f"OCR complete: {out_path}")
    except Exception as e:
        print(f"Error during OCR: {e}")
        raise e
