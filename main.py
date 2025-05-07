from edu import Edubase, load_credentials


def main():
    try:
        creds = load_credentials()
        with Edubase(creds) as edu:
            edu.login()
            edu.fetch_books()

            while True:
                edu.print_books()
                edu.choose_book()
                edu.download_book()
                edu.ocr_book()

                if input("Download another book? (y/n): ").lower() != "y":
                    break

    except KeyboardInterrupt:
        print("Operation cancelled by user")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
