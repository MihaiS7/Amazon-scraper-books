import time
from collections import defaultdict
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
    
        #input(print(f'books:{books_links}'))
        return books_links
    
    def navigating_books(self, urls):
        books = []
        for url in urls:
            self.driver.get(url)
            time.sleep(0.5)
            try:
                book = self.extract_book_data()
                descriptions = self.navigate_formats()
                book = book + descriptions
            except Exception as error:
                pass
            print(book)
            books.append(book)
            #print(books)
            # input("pause")
            # return books
            # break
            # break
        return books

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

    def extract_book_data(self): 
        return [
                self.find_element(BookLocators.TITLE),
                self.find_element(BookLocators.AUTHOR),
                self.find_element(BookLocators.PRICE),
                self.find_element(BookLocators.CATEGORY_1),
                self.find_element(BookLocators.CATEGORY_2),
                self.find_element(BookLocators.RATING),
                self.find_element(BookLocators.REVIEW_COUNT),
                self.driver.current_url ,
                self.find_element(BookLocators.LANGUAGE),
                self.find_element(BookLocators.DIMENTIONS),
                " ".join(self.find_elements(BookLocators.FORMATS,"innerText")),
                ]

    def isLocator(locator, attribute):
        try: 
            element = self._find_element(locator, attribute)
            return True
        except Exception as error:
            #element = ""
            return False
    
    def extract_formats(self):
        # Extract available book formats
        format_block = self.driver.find_elements(*BookLocators.FORMATS_LINKS2)
        text = "javascript:void(0)"
        #print([f.text for f in format_block])
        formats = {}
        for format_ in format_block:
            title = format_.find_element(*FormatLocators.TITLE).get_attribute('innerText')
            link = format_.get_attribute("href")
            link = self.driver.current_url if link.count(text) else link
            formats[title] = link
            
        #input(formats)
        return formats

    def _find_element(self, locator, attribute):
        try:
            text = self.driver.find_element(*locator).get_attribute(attribute)
        except Exception as error:
            text = ""
        return text

    def _str_clean(str_, *replacers):
        for replacer in replacers:
            str_ = str_.replace(replacer, "")
        return str_ 
        

    def _explode(lines, sep, piece_sep):
        elements = {}
        for piece in lines.split(sep): 
            #str_ = self._str_clean(piece, ["\u200f", "\u200e"])
            #input(f'piece: {piece}')
            key, value = piece.split(piece_sep)
            elements[key] = value
        return elements
    
    def order(self, books):
        """analize the formats and give order to blank values"""
        ordered_formats = defaultdict(lambda : defaultdict(list))
        
        #input(print(f"quantity of books: {len(books)}"))
        
        for book, formats in books:
            input(print(book[0]))
            for f_title, f_value in formats.items():
                #ordered_formats[f_title] = defaultdict(list)
                #ordered_formats[f_title]
                for detail_title, detail_value in f_value.items():
                    ordered_formats[f_title][detail_title].append(detail_value)
        pprint(ordered_formats)
        input("end order, press to continue")
        

    def navigate_formats(self):
        descriptions = []
        format_links = self.extract_formats() 
        if format_links:
            for name, link in format_links.items():
                print(f'format_name: {name}')
                print(f'go to  url: {link}')
                self.driver.get(link)
                time.sleep(2)
                description_list = self.find_elements(FormatLocators.LIST_VALUES, "innerText")
                description_table = self.find_elements(FormatLocators.TABLE_VALUE, "innerText")
                if description_list:
                    descriptions += description_list
                elif description_table:
                    descriptions += description_table
                description_list = []
                description_table = []
                print(descriptions)
        return descriptions


   
    def navigate_pages(self, category_url):
        # Contains the list of all the product's information
        book_links = []
        try:
            max_number_of_pages = "//span[@class='s-pagination-item s-pagination-disabled']"
    
            number_of_pages = self.driver.find_element(By.XPATH, max_number_of_pages)
            print("Maximum Pages: ", number_of_pages.text)
        except NoSuchElementException:
            max_number_of_pages = "//li[@class='a-normal'][last()]"
            number_of_pages = self.driver.find_element_by_xpath(max_number_of_pages)
    
        for i in range(1, int(number_of_pages.text) + 1):
            # Goes to next page
            next_page_url = category_url + "&page=" + str(i)
            self.driver.get(next_page_url)
            book_links += self.extract_webpage_information()
            break
        return book_links

    def product_information_spreadsheet(self, records):

        print("\n>> Creating an excel sheet and entering the details...")
        today = date.today().strftime("%d-%m-%Y")

        for _ in records:
            file_name = "{}_{}.csv".format(self.category_name, today)
            f = open(file_name, "a", newline='', encoding='utf-8')
            writer = csv.writer(f)
            writer.writerow(['Title', 'Author', 'Price', 'Category1', 'Category 2', 'Rating', 'Review Count', 'Product URL', 'Language', 'Dimensions', 'Formats', 'ASIN', 'Editorial', 'Idioma', 'Tamaño del archivo', 'Texto a voz', 'Lector de pantalla', 'Tipografía mejorada', 'Word Wise', 'Notas adhesiva', 'Longitud de impresión', ])
            writer.writerows(records)
            f.close()

        message = f">> Information about the product '{self.category_name}' is stored in {file_name}\n"

        print(message)

        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, file_name])


if __name__ == "__main__":
    my_amazon_bot = AmazonProductScraper()
    my_amazon_bot.open_browser()

    for category_url in my_amazon_bot.get_category_url():
        books = my_amazon_bot.navigating_books([category_url])
    my_amazon_bot.product_information_spreadsheet(books)
        
    my_amazon_bot.driver.close()

# Test
