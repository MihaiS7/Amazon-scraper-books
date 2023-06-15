import time
from collections import defaultdict
from itertools import chain
from datetime import date
import csv
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
import subprocess, sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from locators import MainLocators, BookLocators, FormatLocators
import os
import pandas as pd


class AmazonProductScraper:
    def __init__(self):
        self.driver = None
        self.category_name = None
        self.formatted_category_name = None
        self.book_data = {}
        self.price_keys = set()
        self.format_keys = set()

    def open_browser(self):
        # Setting browser
        opt = Options()
        opt.add_argument("--disable-infobars")
        opt.add_argument("--disable-extensions")
        opt.add_argument('--log-level=OFF')
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])

        url = "https://www.amazon.es/"
        driver_path = "chromedriver"
        #self. driver = webdriver.Chrome(service=Service(driver_path), options=opt)

        # Opening chrome
        self.driver = webdriver.Chrome(options=opt)
        self.driver.get(url)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.NAME, 'accept'))
        )
        accept_button = self.driver.find_element(By.NAME, 'accept')
        accept_button.click()

        time.sleep(3)

    def get_category_url(self):
        data = pd.read_csv("input.csv")

        for url in data["url"]:
            self.driver.get(url)
            yield url

    def extract_webpage_information(self):
        books_links = [book.get_attribute("href") for book in self.driver.find_elements(*MainLocators.BOOKS)]
    
        #input(print(f'boks:{books_links}'))
        return books_links
    

    def find_element(self, locator):
        try:
            text = self.driver.find_element(*locator).text
        except Exception as error:
            text = ""
        return text

    def find_elements(self, locator, attribute):
        try:
            text = [tag.get_attribute(attribute) for tag in self.driver.find_elements(*locator)]
        except Exception as error:
            text = ""
        return text

    def _format_prices(self):
        formats = {}
        for format_ in self.driver.find_elements(*BookLocators.FORMATS_BLOCK):
            title = format_.find_element(*FormatLocators.TITLE).get_attribute("innerText").strip()
            price = format_.find_element(*FormatLocators.PRICE).get_attribute("innerText").strip()
            formats[f'Price_{title}'] = price
            #titles = [title.find_element(*FormatLocators.TITLE).get_attribute("innerText") for title in self.driver.find_elements(*BookLocators.FORMATS_BLOCK)]
            #price = [price.find_element(*FormatLocators.PRICE).get_attribute("innerText") for price in self.driver.find_elements(*BookLocators.FORMATS_BLOCK)]
        self.price_keys.update(formats.keys())
        return formats
    
    def process_formats(self,category_name):
        list_keys = [title.text.replace(":", "").strip() for title in self.driver.find_elements(*FormatLocators.DETAIL_LIST_TITLES)] 
        list_values = [values.text.strip() for values in self.driver.find_elements(*FormatLocators.DETAIL_LIST_VALUES)] 
        table_keys = [title.text.strip() for title in self.driver.find_elements(*FormatLocators.DETAIL_TABLE_KEYS)] 
        table_values = [values.text.strip() for values in self.driver.find_elements(*FormatLocators.DETAIL_TABLE_VALUES)] 
        formats = dict(zip([ f'{category_name}_{key}' for key in list_keys], list_values)) if list_keys else dict(zip([f'{category_name}_{key}' for key in table_keys], table_values))
        return formats

    def extract_book_data(self): 
        self.book_data = {
                'Title': self.find_element(BookLocators.TITLE),
                'Author': self.find_element(BookLocators.AUTHOR),
                **self._format_prices(),
                'Category 1': self.find_element(BookLocators.CATEGORY_1),
                'Category 2': self.find_element(BookLocators.CATEGORY_2),
                'Rating': self.find_element(BookLocators.RATING),
                'Review Count': self.find_element(BookLocators.REVIEW_COUNT),
                'Product URL': self.driver.current_url,
                'Language': self.find_element(BookLocators.LANGUAGE),
                'Dimensions': self.find_element(BookLocators.DIMENTIONS),
                }
        return self.book_data

    def extract_formats(self):
        format_block = self.driver.find_elements(*BookLocators.FORMATS_LINKS2)
        text = "javascript:void(0)"
        #print([f.text for f in format_block])
        formats = {}
        for format_ in format_block:
            title = format_.find_element(*FormatLocators.TITLE).get_attribute('innerText')
            link = format_.get_attribute("href")
            link = self.driver.current_url if link.count(text) else link
            formats[title] = link

        return formats
    

    def navigate_formats(self):
        format_links = self.extract_formats() 
        format_details = {}
        if format_links:
            for name, link in format_links.items():
                self.driver.get(link)
                time.sleep(1)
                format_details.update(self.process_formats(name))
                #self.format_keys[name].update(format_details.keys())
                self.format_keys.update(format_details.keys())
            #return self.book_data
            return format_details
        
    def navigating_books(self, urls):
        books = []
        for url in urls:
            self.driver.get(url)
            time.sleep(0.5)
            #try:
            book = self.extract_book_data()
            print(f"Book data: {book}")
            descriptions = self.navigate_formats()
            book.update(descriptions)
            #except Exception as error:
                #print(f"An error occurred: {error}")
                #pass
            #if book:
            books.append(book)
        return books
    
    def product_information_spreadsheet(self, book_data, prices_keys, format_keys):

        print("\n>> Creating an excel sheet and entering the details...")
        #format_keys = [*set([key for key in chain(*format_keys.values())])]
        price_keys_ = [key for key in self.book_data.keys() if key not in chain(prices_keys, format_keys)]
        field_names = price_keys_[:2] + list(price_keys) + price_keys_[2:] + sorted(format_keys)
        with open('books.csv', 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, field_names)
            dict_writer.writeheader()
            dict_writer.writerows(book_data)
            print("Data written to CSV file. ")

if __name__ == "__main__":
    my_amazon_bot = AmazonProductScraper()
    my_amazon_bot.open_browser()

    all_books = []
    for category_url in my_amazon_bot.get_category_url():
        books = my_amazon_bot.navigating_books([category_url])
        print(f"Books: {books}")
        all_books.extend(books)
    price_keys, format_keys = my_amazon_bot.price_keys, my_amazon_bot.format_keys
         
    my_amazon_bot.product_information_spreadsheet(all_books, price_keys, format_keys)
    my_amazon_bot.driver.close()
