from bs4 import BeautifulSoup
import requests
import config
import csv
import json

"""
This function will grab the content from the the specified url.
"""
def get_data(url, headers=None):
    r = requests.get(url, headers=headers)
    content = r.content
    soup = BeautifulSoup(content, features="lxml")
    return soup

"""
This function will stip out inconsistencies in book titles so that the function will calculate
appropriate number of matches. This mainly includes ':' and '('
"""
def standardize_title(title):
    title = title.lstrip()
    if ':' in title:
        new_title = title.split(':')
        new_title = new_title[0].rstrip()
        if ' (' in title:
            new_title = new_title.split(' (')
            new_title = new_title[0].rstrip()
    elif ' (' in title:
        new_title = title.split(' (')
        new_title = new_title[0].rstrip()
    else:
        new_title = title.rstrip()
    return new_title

"""
This function will return a list of the best books in 2020 based on Penguin Random House Publisher
"""
def penguin_parser():
    soup = get_data('https://www.penguinrandomhouse.com/the-read-down/the-best-books-of-2020')
    # Create a list of titles from this site
    penguin_titles = []
    for data in soup.findAll('li', attrs={'class': 'inner-facade'}):
        title = data['ttl']
        new_title = standardize_title(title)
        penguin_titles.append(new_title)
    return penguin_titles

"""
This function will return a list of the top 20 books in 2020 from Amazon
"""
def amazon_parser():
    pageNo = 1
    amazon_titles = []
    # ToDo: this isn't great logic, I know that the page number will stop at 2 given the list is only 20
    # books long. This should be refactored to be less fragile
    while pageNo < 3:
        # need to send headers in requet to retrieve content from page
        soup = get_data("https://www.amazon.com/s?i=stripbooks&rh=n%3A7031012011&fs=true&page="+str(pageNo)+"&qid=1608750198&ref=sr_pg_"+str(pageNo), {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"})
        for data in soup.findAll('h2', attrs={'class': 'a-size-mini'}):
            title_element = data.find('span')
            title = title_element.text
            new_title = standardize_title(title)
            amazon_titles.append(new_title)
        pageNo += 1
        return amazon_titles

"""
This function will return a list of the 10 best books in 2020 from the new york times
"""
def nytime_parser():
    soup = get_data("https://www.nytimes.com/2020/11/23/books/review/best-books.html")
    ny_titles = []
    for data in soup.findAll('h2', attrs={'class': 'css-1tt7ig1'}):
        title = data.text
        new_title = standardize_title(title)
        ny_titles.append(new_title)
    return ny_titles

"""
This function will return a list of the top books from the boston globe
"""
def bostonglobe_parser():
    soup = get_data("https://apps.bostonglobe.com/arts/graphics/2020/12/best-books-of-2020/")
    boston_titles = []
    for data in soup.findAll('h3', attrs={'class': 'list__title'}):
        title = data.find('a')
        title_text = title.text
        new_title = standardize_title(title_text)
        boston_titles.append(new_title)
    return boston_titles

"""
This function will return a list of top books from the washington post
"""
def washingtonpost_parser():
    soup = get_data("https://www.washingtonpost.com/graphics/2020/lifestyle/2020-best-books/")
    post_titles = []
    for data in soup.findAll('div', attrs={'class': 'book-container'}):
        title = data.find('h3')
        title_text = title.text
        new_title = standardize_title(title_text)
        post_titles.append(new_title)
    return post_titles

"""
Returns a list of top 10 books from Barnes and Noble
"""
def barnes_parser():
    soup = get_data("https://www.barnesandnoble.com/b/books/barnes-nobles-best-books-of-2020/barnes-nobles-10-best-books-of-2020/_/N-29Z8q8Z2v0b")
    barnes_titles = []
    for data in soup.findAll('a', attrs={'class': 'pImageLink'}):
        title_text = data['title']
        new_title = standardize_title(title_text)
        barnes_titles.append(new_title)
    return barnes_titles

"""
Returns a list of top books from book riot
"""
def bookriot_parser():
    soup = get_data("https://bookriot.com/best-books-of-2020/")
    bookriot_titles = []
    for data in soup.findAll('h2', attrs={'class': 'book-title'}):
        title_text = data.text
        new_title = standardize_title(title_text)
        bookriot_titles.append(new_title)
    return bookriot_titles

"""
Returns a list of top books from goodreads
"""
def goodreads_parser():
    soup = get_data("https://www.goodreads.com/book/popular_by_date/2020")
    goodreads_titles = []
    for data in soup.findAll('a', attrs={'class': 'bookTitle'}):
        title = data.find('span')
        title_text = title.text
        new_title = standardize_title(title_text)
        goodreads_titles.append(new_title)
    return goodreads_titles

"""
Use good reads to get author for each book to use in google api query
"""
def goodreads_author():
    book_author = {}
    soup = get_data("https://www.goodreads.com/book/popular_by_date/2020")
    for data in soup.findAll('tr'):
        title = data.find('a', attrs={'class': 'bookTitle'})
        author = data.find('a', attrs={'class': 'authorName'})
        title_text = title.text
        new_title = standardize_title(title_text)
        author_text = author.text
        book_author[new_title] = author_text
    return book_author

goodreads_author()

"""
This function will look for matching titles between the two lists and return a list of books sorted
by occurrence in multiple lists.
"""
def best_of_best():
    amazon = amazon_parser()
    penguin = penguin_parser()
    nytimes = nytime_parser()
    boston = bostonglobe_parser()
    post = washingtonpost_parser()
    barnes = barnes_parser()
    bookriot = bookriot_parser()
    goodreads = goodreads_parser()
    # this is a dictionary for all top books by source
    all_books = {'amazon':amazon, 'penguin':penguin, 'nytimes': nytimes, 'boston': boston, 'post': post,
                 'barnes': barnes, 'bookriot': bookriot, 'goodreads': goodreads}
    # this dictionary will hold a count of unique books based on number of lists that the book appears
    best_books = {}
    for value in all_books.keys():
        for title in all_books[value]:
            if title in best_books:
                best_books[title] += 1
            else:
                best_books[title] = 1
    # sort dictionary values by the highest number of occurrences in a list
    best_books = dict(sorted(best_books.items(), key=lambda item: item[1], reverse=True))
    print(best_books)
    # only print books that are in at least 2 lists
    final_books = [key for key, value in best_books.items() if value > 1]
    print(final_books)
    return final_books

"""
This function will grab more information about the top books from the google books api.
"""
def get_book_info(book_titles, author_list):
    all_book_info = []

    for title in book_titles:
        book_details = {}
        try:
            author = author_list[title]
        except:
            # not sure why, but the correct google api result is returned when this is used for author vs empty
            author = '" "'
        book_title = title.replace(" ", "+")

        # assumption here is that title and author search will yield 1 result
        r = requests.get(('https://www.googleapis.com/books/v1/volumes?q="{}"+inauthor:{}&maxResults=1&key='+config.api_key).format(book_title, author))
        content = r.content
        json_object = json.loads(content)

        book_data = json_object['items']

        for item in book_data:
            book_details['title'] = title
            authors = item['volumeInfo']['authors']
            # authors returns a lits, but for now, just grab the first one.
            book_details['author'] = authors[0]
            book_details['description'] = item['volumeInfo']['description']
            book_details['pageCount'] = item['volumeInfo']['pageCount']
            book_details['moreInfo'] = item['volumeInfo']['infoLink']
            book_details['publishedDate'] = item['volumeInfo']['publishedDate']
            all_book_info.append(book_details)
    return all_book_info

"""
This function will prent the data from get_book_info to a csv
"""
def export_to_csv(books):
    with open('best_books_2020.csv', mode='w') as csv_file:
        fieldnames = ['title', 'author', 'description', 'pageCount', 'moreInfo', 'publishedDate']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)
