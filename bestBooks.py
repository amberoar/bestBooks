from bestBooks_helper import *

def main():
    initial_list = best_of_best()
    books = get_book_info(initial_list)
    export_to_csv(books)

if __name__ == "__main__":
    main()
