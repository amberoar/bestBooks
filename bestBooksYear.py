from bs4 import BeautifulSoup
import requests
import re

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
This function will look for matching titles between the two lists and return a list of books sorted
by occurrence in multiple lists.
"""
def best_of_best():
    amazon = amazon_parser()
    penguin = penguin_parser()
    nytimes = nytime_parser()
    boston = bostonglobe_parser()
    post = washingtonpost_parser()
    # this is a dictionary for all top books by source
    all_books = {'amazon':amazon, 'penguin':penguin, 'nytimes': nytimes, 'boston': boston, 'post': post}
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

best_of_best()
# penguin_parser()
