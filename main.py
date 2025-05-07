from edu import Edubase, load_credentials


def main():
    try:
        creds = load_credentials()
        with Edubase(creds) as edu:
            edu.login()
            edu.fetch_books()
            edu.print_books()
            edu.choose_book()
            edu.download_book()
    except KeyboardInterrupt:
        print("Operation cancelled by user")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
