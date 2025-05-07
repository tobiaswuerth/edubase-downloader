import io
import os
import signal
import sys
import time
import re
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter
from tqdm import trange

from .credentials import Credentials


class Edubase:
    def __init__(self, credentials: Credentials):
        self.credentials: Credentials = credentials
        self.playwright = None
        self.browser = None
        self.page = None

        self.setup_signal_handlers()
        self.ensure_browsers_installed()

        self.books = []
        self.book_id = None

    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, sig, frame):
        print("\nReceived interrupt, cleaning up...")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        if self.browser:
            print("Closing browser...")
            try:
                self.browser.close()
            except Exception:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass

    def ensure_browsers_installed(self):
        try:
            import subprocess
            from playwright._impl._driver import (
                compute_driver_executable,
                get_driver_env,
            )

            driver_executable, driver_cli = compute_driver_executable()
            subprocess.run(
                [driver_executable, driver_cli, "install", "chromium"],
                env=get_driver_env(),
                check=True,
            )
        except Exception as e:
            print(f"Failed to install browser: {e}")
            exit(1)

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6567.90 Safari/537.36"
        )
        self.page = context.new_page()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def login(self):
        print("Logging in...")
        self.page.goto(
            url="https://app.edubase.ch/#promo?popup=login",
            wait_until="networkidle",
        )
        time.sleep(1)

        self.page.fill('input[name="login"]', self.credentials.username)
        self.page.fill('input[name="password"]', self.credentials.password)
        self.page.click('button[type="submit"]')
        time.sleep(1)

        assert (
            "An account with the credentials you entered does not exist"
            not in self.page.locator("body").inner_text()
        ), "Login failed - invalid credentials"
        print("Login successful")

    def fetch_books(self):
        print("Fetching book list...")
        self.page.wait_for_selector("#libraryItems li")
        time.sleep(2)

        books = []
        links = self.page.query_selector_all("a.lu-library-item-aux")
        BOOK_ID_REGEX = re.compile(r"#doc/(\d+)")

        for link in links:
            href = link.get_attribute("href")
            title = link.get_attribute("title")

            if href and (match := BOOK_ID_REGEX.match(href)):
                books.append({"id": match.group(1), "title": title})

        print(f"Found {len(books)} books")
        self.books = books

    def print_books(self):
        if not self.books:
            print("<No books available>")
            return

        print("Available books:")
        for idx, book in enumerate(self.books):
            print(f"- {idx}: {book['title']}")

    def choose_book(self):
        while True:
            choice = input("Enter book index to download: ")
            try:
                idx = int(choice)
            except ValueError:
                print("Invalid input, please enter a number.")

            if 0 <= idx < len(self.books):
                self.book_id = self.books[idx]["id"]
                break
            else:
                print("Invalid selection, please try again.")

    def download_book(self):
        out_dir = "downloads"
        os.makedirs(out_dir, exist_ok=True)

        file_name = f"{self.book_id}.pdf"
        file_name = os.path.join(out_dir, file_name)
        assert not os.path.exists(file_name), f"File {file_name} already exists"

        print(f"Downloading book {self.book_id} to {file_name}...")
        self.page.goto(
            f"https://app.edubase.ch/#doc/{self.book_id}/1",
            wait_until="networkidle",
        )
        time.sleep(0.5)

        max_pages_raw = self.page.evaluate(
            """
            () => {
                const paginationElement = document.querySelector("#pagination");
                if (!paginationElement) return "0";
                const spans = Array.from(paginationElement.getElementsByTagName("span"));
                const pageSpan = spans.find(span => span.textContent.includes("/ "));
                return pageSpan ? pageSpan.innerHTML : "0";
            }
        """
        )

        max_pages = int(max_pages_raw.replace("/ ", ""))

        pdf = PdfWriter()
        for i in trange(1, max_pages + 1, desc="Downloading pages", unit="page"):
            self.page.goto(
                f"https://app.edubase.ch/#doc/{self.book_id}/{i}",
                wait_until="networkidle",
            )
            time.sleep(0.5)

            pdf_bytes = self.page.pdf()
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            pdf.add_page(pdf_reader.pages[0])

        print(f"Saving {file_name}...")
        pdf.write(file_name)
        pdf.close()
        print(f"Book {self.book_id} successfully downloaded to {file_name}")
