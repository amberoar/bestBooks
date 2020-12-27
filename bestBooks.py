from bestBooks_helper import * 

def main():
    books = get_book_info()
    export_to_csv(books)

if __name__ == "__main__":
    main()
