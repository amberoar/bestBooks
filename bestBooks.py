from bestBooks_helper import *

def main():
    authors = goodreads_author()
    initial_list = best_of_best()
    books = get_book_info(initial_list, authors)
    export_to_csv(books)

if __name__ == "__main__":
    main()
