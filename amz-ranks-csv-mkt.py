#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import time
from selenium import webdriver
import re
import datetime
from collections import deque
import logging
import csv
import json
import codecs
import sys
import io


class AmazonScaper(object):

    def __init__(self,keywords, output_file='listing.csv',sleep=2):

        options = webdriver.ChromeOptions()
        #options.add_argument('window-size=800x841')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        #options.add_argument("'user-agent="+user_agent+"'")
        self.browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver',chrome_options=options)  #Add path to your Chromedriver
        self.keyword_queue = deque(keywords)  #Add the start URL to our list of URLs to crawl
        self.output_file = output_file
        self.sleep = sleep
        self.counter = 0
        self.results = []


    def get_page(self, keyword, mkt, page_number):
        try:
            self.browser.get('https://www.'+mkt+'/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords={a}'.format(a=keyword)+'&page='+str(page_number))
            return self.browser.page_source
        except Exception as e:
            logging.exception(e)
            return

    def get_soup(self, html):
        if html is not None:
            soup = BeautifulSoup(html, 'lxml')
            return soup
        else:
            return

    def get_data(self,soup,keyword,mkt,page_num):

        try:
            results = soup.findAll('div', attrs={'class': 's-item-container'})
            for a, b in enumerate(results):
                soup = b
                header = soup.find('h2')
                #result = a + 1 + (32 * (page_num - 1))
                title = header.text
                title = title.replace('[','(')
                title = title.replace(']',')')

                try:
                    link = soup.find('a', attrs={'class': 'a-link-normal a-text-normal'})
                    self.counter = self.counter + 1
                    result = self.counter
                    url = link['href']
                    url = re.sub(r'%2F', '/', str(url))
                    url = re.sub(r'.*/dp/', '', str(url))
                except:
                    url = "None"

                # Extract the ASIN from the URL - ASIN is the breaking point to filter out if the position is sponsored
                ASIN = re.sub(r'/ref.*', '', str(url))

                # Extract Review Score
                score = soup.find_all('span', attrs={'class': 'a-icon-alt'})
                for s in score:
                    review_score = s
                try:
                    score = review_score.text
                except:
                    score = "None"

                # Extract Number of Reviews in the same way
                reviews = soup.find('a', href=re.compile(r'.*#customerReviews'))
                try:
                    reviews = reviews.text
                except:
                    reviews = "None"

                # And again for Prime

                if mkt == 'amazon.fr':
                    PRIME = soup.find('i', attrs={'aria-label': 'Écran'})
                elif mkt == 'amazon.it':
                    PRIME = soup.find('i', attrs={'aria-label': 'Prime'})
                elif mkt == 'amazon.de':
                    PRIME = soup.find('i', attrs={'aria-label': 'Prime'})
                elif mkt == 'amazon.es':
                    PRIME = soup.find('i', attrs={'aria-label': 'Prime'})
                else:
                    PRIME = soup.find('i', attrs={'aria-label': 'Prime'})

                try:
                    PRIME = PRIME.text
                except:
                    PRIME = "None"

                # promo
                promo = soup.find_all('span', attrs={'class': 'a-size-small a-color-secondary'})
                for b in promo:
                    promo = b
                try:
                    promo = promo.text
                except:
                    promo = "None"

                # get orig price
                price_orig = soup.find('span', attrs={'class': 'a-size-small a-color-secondary a-text-strike'})
                try:
                    price_orig = price_orig.text
                except:
                    price_orig = "None"


                # get price
                price = soup.find('span', attrs={'class': 'a-size-base a-color-price s-price a-text-bold'}) 
                try:
                    price = price.text
                except:
                    price = "None"

                if mkt == 'amazon.fr':
                    self.results.append([keyword,
                        mkt,
                        str(result),
                        title,
                        ASIN,
                        score.replace(u' \xe9toiles sur 5' ,'').replace(',' ,'.'),
                        reviews.replace(u'\xa0', ''),
                        PRIME,
                        promo,
                        price_orig.replace('EUR ' ,'').replace(',' ,'.'),
                        price.replace('EUR ' ,'').replace(',' ,'.'),
                        datetime.datetime.today().strftime("%B %d, %Y %H:%M")
                        ])
                elif mkt == 'amazon.it':
                    self.results.append([keyword,
                        mkt,
                        str(result),
                        title,
                        ASIN,
                        score.replace(' su 5 stelle' ,'').replace(',' ,'.'),
                        reviews.replace('.', ''),
                        PRIME,
                        promo,
                        price_orig.replace('EUR ' ,'').replace(',' ,'.'),
                        price.replace('EUR ' ,'').replace(',' ,'.'),
                        datetime.datetime.today().strftime("%B %d, %Y %H:%M")
                        ])
                elif mkt == 'amazon.de':
                    self.results.append([keyword,
                        mkt,
                        str(result),
                        title,
                        ASIN,
                        score.replace(' von 5 Sternen' ,'').replace(',' ,'.'),
                        reviews.replace(u'\xa0', ''),
                        PRIME,
                        promo,
                        price_orig.replace('EUR ' ,'').replace(',' ,'.'),
                        price.replace('EUR ' ,'').replace(',' ,'.'),
                        datetime.datetime.today().strftime("%B %d, %Y %H:%M")
                        ])
                elif mkt == 'amazon.es':
                    self.results.append([keyword,
                        mkt,
                        str(result),
                        title,
                        ASIN,
                        score.replace(u' de un m\xe1ximo de 5 estrellas','').replace(',' ,'.'),
                        reviews.replace(u'\xa0', ''),
                        PRIME,
                        promo,
                        price_orig.replace('EUR ' ,'').replace(',' ,'.'),
                        price.replace('EUR ' ,'').replace(',' ,'.'),
                        datetime.datetime.today().strftime("%B %d, %Y %H:%M")
                        ])
                elif mkt == 'amazon.co.uk':
                    self.results.append([keyword,
                        mkt,
                        str(result),
                        title,
                        ASIN,
                        score.replace(' out of 5 stars' ,'').replace(',' ,'.'),
                        reviews.replace(u'\xa0', ''),
                        PRIME,
                        promo,
                        price_orig.replace(u'\xa3' ,'').replace(',' ,'.'),
                        price.replace(u'\xa3' ,'').replace(',' ,'.'),
                        datetime.datetime.today().strftime("%B %d, %Y %H:%M")
                        ])
                else:
                    self.results.append([keyword,
                        mkt,
                        str(result),
                        title,
                        ASIN,
                        score.replace(u' \xe9toiles sur 5' ,'').replace(',' ,'.'),
                        reviews.replace(u'\xa0', ''),
                        PRIME,
                        promo,
                        price_orig.replace('EUR ' ,'').replace(',' ,'.'),
                        price.replace('EUR ' ,'').replace(',' ,'.'),
                        datetime.datetime.today().strftime("%B %d, %Y %H:%M")
                        ])


        except Exception as e:
            print(e)

        return 1

    def csv_output(self):
        keys = ['Keyword','Market','Rank','Title','ASIN','Score','Reviews','Prime','Promo','PriceOrig','Price','Date']
        print(self.results)
        c = csv.writer(open(self.output_file, 'w'), quoting=csv.QUOTE_NONNUMERIC)
        c.writerow(keys)
        for row in self.results:
            row = [v.decode('utf-8') if isinstance(v, str) else v for v in row]
            c.writerow([unicode(s).encode('utf-8') for s in row])

    def run_crawler(self):
        while len(self.keyword_queue): 
            self.counter = 0
            keyword = self.keyword_queue.popleft() #We grab a keyword from the left of the list
            if market == 'ALL':
                while len(self.market_queue): 
                    tmarket = self.market_queue.popleft() #We grab a market from the left of the list
                    page_no = 1
                    while page_no <= pages:
                        html = self.get_page(keyword,tmarket,page_no)
                        soup = self.get_soup(html)
                        time.sleep(self.sleep) # Wait for the specified time
                        if soup is not None:  #If we have soup - parse and save data
                            self.get_data(soup,keyword,tmarket,page_no)
                            page_no = page_no + 1
            else:
                page_no = 1
                while page_no <= pages:
                    html = self.get_page(keyword,market,page_no)
                    soup = self.get_soup(html)
                    time.sleep(self.sleep) # Wait for the specified time
                    if soup is not None:  #If we have soup - parse and save data
                        self.get_data(soup,keyword,market,page_no)
                        page_no = page_no + 1

        self.browser.quit()
        self.csv_output() # Save the object data to csv


if __name__ == "__main__":
    market = str.replace(sys.argv[1].rstrip('\n'),' ','+')
    keyfile = market + '.keywords'
    keywords = [str.replace(line.rstrip('\n'),' ','+') for line in open(keyfile)] # Use our file of keywords & replaces spaces with +
    pages = int(sys.argv[2])
    ranker = AmazonScaper(keywords) # Create the object
    ranker.run_crawler() # Run the rank checker


