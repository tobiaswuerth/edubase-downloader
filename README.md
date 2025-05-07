# Edubase Downloader + OCR
Backup/Download your **bought** Edubase books to PDFs, because nobody likes proprietary ebook readers. 

---

## Setup (on Windows)
```bash
git clone https://github.com/tobiaswuerth/edubase-downloader.git
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

**Setup OCR (if necessary):**
- download and setup https://github.com/UB-Mannheim/tesseract/wiki
- add installation directory to system environment variable ``PATH`` (to let it access ``tesseract.exe``)
- open link https://github.com/tesseract-ocr/tessdata/
    - download the languages you intend to use:
        - note: code is setup for Deutsch and English, if you need something else, adjust the default in [ocr.py](edu/ocr.py)
        - note: English is available by default, needs no additional download
        - `deu` for Deutsch, download [deu.traineddata](https://github.com/tesseract-ocr/tessdata/raw/refs/heads/main/deu.traineddata)  
    - put the files into the installation sub-directory `tessdata` (e.g. `\Tesseract-OCR\tessdata\deu.traineddata`)
- download and setup https://ghostscript.com/releases/gsdnld.html

## Usage

1. Update the [config.yaml](config.yaml) file with your edubase login credentials
2. Run `py .\main.py`

This will:
1. opens new browser window
2. login using your credentials
3. find all books
4. lets you choose which book to download
5. download PDF to ``/downloads/`` directory
6. OCR the PDF (if setup correctly)
7. ... choose to download another one or not, goto step 4. and repeat


---

## Legal
This code does not "crack" any copy protection. It simply makes automated screenshots of every single site of a **bought** document/book. Since Edubase cannot guarantee the existence/support for their reader app if they go out of business, this repo was created to save, backup and preserve **bought** Edubase documents as the widely adapted and well documented PDF format.
