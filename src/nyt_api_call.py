# NYT Book Review Web Parser, easily adaptable to other websites
# by Jack Hester
# Note: depends on beautifulsoup4, and urllib2!
# v 0.0.2, now for python 3.x
import argparse
import os
import re
import glob
import datetime as dt
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import time
from bs4 import BeautifulSoup as bs
import os.path
import sys
import warnings
import datetime
import json
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
warnings.filterwarnings("ignore", category=UserWarning)

json_output_dir = "/Users/jack/Desktop/chong_analysis/times_json"
review_output_dir = "/Users/jack/Desktop/chong_analysis/times_reviews"
api_key = ""

# uncomment one or both of these to run things
download=False
extract_reviews=True

def download_isbn10(isbn):
    json_url = "https://api.nytimes.com/svc/books/v3/reviews.json?isbn=" + isbn + "&api-key="+api_key
    filedata = urllib2.urlopen(json_url)
    json_content = json.loads(filedata.read().decode())
    #j = json.load(json_content)
    #print(json_content)
    res = json_content['results'][0]
    review_url = res['url']
    reviewer = res['byline'].replace(' ','-')
    author = res['book_author'].replace(' ','-')
    book_title = res['book_title'].replace(' ','-')
    rev_date = res['publication_dt'].replace(' ','-')
    try:
        sauce = urllib2.urlopen(review_url).read()
        soup = bs(sauce)
        try:
            review_title = soup.find('h1', {'class': 'css-1i12ox0 e1h9rw200'}).text
            review_title = review_title.replace(' ','-')
        except:
            review_title = "REV_TITLE_ERR"
        download_title = reviewer +"_"+ review_title +"_"+ author +"_"+ book_title +"_"+ rev_date +".txt"
        with open(os.path.join(review_output_dir,download_title),'w+', encoding='utf-8', errors='ignore') as f:
            for a in soup.findAll('p', {'class': 'css-axufdj evys1bk0'}):
                f.write(str(a.text))
                f.write("\n")
    except:
        print('error downloading at: ', review_url)
        pass

def download_url(review_url):
    print('trying to directly download', review_url)
    try:
        sauce = urllib2.urlopen(review_url).read()
        soup = bs(sauce)
        try:
            review_title = soup.find('h1', {'class': 'css-1i12ox0 e1h9rw200'}).text
            review_title = review_title.replace(' ','-')
        except:
            review_title = "REV_TITLE_ERR"
            pass
        try:
            reviewer = soup.find('span', {'class': 'css-1baulvz last-byline'}).text
        except:
            reviewer = "REV_NAME_ERR"
            pass
        try:
            rev_date = currSoup.time['datetime'] # got time from the article's html
            rev_date = dateString.split('T')[0]
        except:
            rev_date="REV_DATE_ERR"
        download_title = reviewer +"_"+ review_title +"_"+ "BOOK_AUTHOR_ERR" +"_"+ "BOOK_TITLE_ERR" +"_"+ rev_date +".txt"
        with open(os.path.join(review_output_dir,download_title),'w+', encoding='utf-8', errors='ignore') as f:
            for a in soup.findAll('p', {'class': 'css-axufdj evys1bk0'}):
                f.write(str(a.text))
                f.write("\n")
        f.close()
    except:
        print('error downloading at: ', review_url)
        pass


if download==True:
    for i in range(0, int(33361/20)+1): # this number came from the number of books found #(https://developer.nytimes.com/docs/books-product/1/routes/lists/best-sellers/history.json/get)
        if i > 0 and i%2 == 0:
            time.sleep(12)
        offset = i*20
        url = "https://api.nytimes.com/svc/books/v3/lists/best-sellers/history.json?offset=" + str(offset) + "&api-key=" + api_key
        filedata = urllib2.urlopen(url)
        datatowrite = filedata.read()
        filename = os.path.join(json_output_dir, ("books_"+str(i)+".json"))
        with open(filename, 'wb', encoding='utf-8', errors='ignore') as f:
            f.write(datatowrite)
        f.close()

if extract_reviews == True:
    for f in os.listdir(json_output_dir):
        with open(os.path.join(json_output_dir, f)) as json_file:
            data = json.load(json_file)
            for res in data['results']:
                review_info = res['reviews']
                book_rev_link = review_info[0]['book_review_link']
                ranks_history = res['ranks_history']
                #if len(ranks_history) == 0:
                #    if book_rev_link!=None and len(book_rev_link) > 1:
                #       print(book_rev_link)
                #        #count+=1
                if len(ranks_history) > 1:
                    category = ranks_history[0]['list_name']
                    if category in ['Combined Print and E-Book Fiction',
                                    'Combined Print & E-Book Fiction',
                                    'combined-print-and-e-book-fiction',
                                    'Hardcover Fiction',
                                    'hardcover-fiction',
                                    'Trade Fiction Paperback',
                                    'trade-fiction-paperback',
                                    'E-Book Fiction',
                                    'e-book-fiction',
                                    'Combined Print Fiction',
                                    'Combined Hardcover & Paperback Fiction',
                                    'combined-print-fiction',
                                    'Audio Fiction',
                                    'audio-fiction',
                                    'mass-market-paperback']:
                        if len(book_rev_link) > 1:
                            isbns = res['isbns']
                            isbn10 = isbns[0]['isbn10']
                            try:
                                download_isbn10(isbn10)
                            except:
                                print('error for isbn: ', isbn10)
                                #print(f)
                                #print("xxx")
                                #print(isbn10)
                                #print("xxx")
                                #print(book_rev_link)
                                download_url(book_rev_link)
                            time.sleep(6)
        json_file.close()

#download_isbn10('9781524763138')
