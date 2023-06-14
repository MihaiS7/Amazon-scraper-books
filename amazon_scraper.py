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
        self.book_data = {}

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
        self.book_data = {
                'Title': self.find_element(BookLocators.TITLE),
                'Author': self.find_element(BookLocators.AUTHOR),
                'Price': self.find_element(BookLocators.PRICE),
                'Category 1': self.find_element(BookLocators.CATEGORY_1),
                'Category 2': self.find_element(BookLocators.CATEGORY_2),
                'Rating': self.find_element(BookLocators.RATING),
                'Review Count': self.find_element(BookLocators.REVIEW_COUNT),
                'Product URL': self.driver.current_url,
                'Language': self.find_element(BookLocators.LANGUAGE),
                'Dimensions': self.find_element(BookLocators.DIMENTIONS),
                'Formats': " ".join(self.find_elements(BookLocators.FORMATS,"innerText")),

                'Kindle_Asín': '',
                'Kindle_Editorial': '',
                'Kindle_Tamaño del archivo': '',
                'Kindle_Texto a voz': '',
                'Kindle_Lector de pantalla': '',
                'Kindle_Tipografía mejorada': '',
                'Kindle_Word Wise': '',
                'Kindle_Páginas': '',
                'Kindle_En Kindle Scribe': '',
                'Kindle_Precio': '',
                'Kindle_Tiempo': '',
                'Kindle_Autor': '',
                'Kindle_Narrador': '',
                'Kindle_Fecha de lanzamiento': '',
                'Kindle_Editor': '',
                'Kindle_Versión': '',
                'Kindle_Idioma': '',
                'Kindle_Asín': '',
                'Kindle_Acento': '',

                'Audiobook_Asín': '',
                'Audiobook_Editorial': '',
                'Audiobook_Precio': '',
                'Audiobook_Idioma': '',
                'Audiobook_Páginas': '',
                'Audiobook_ISBN-10': '',
                'Audiobook_ISBN-13': '',
                'Audiobook_Edad de lectura': '',
                'Audiobook_Peso del producto': '',
                'Audiobook_Dimensiones': '',

                'Hardcover_Asín': '',
                'Hardcover_Editorial': '',
                'Hardcover_Precio': '',
                'Hardcover_Idioma': '',
                'Hardcover_Páginas': '',
                'Hardcover_ISBN-10': '',
                'Hardcover_ISBN-13': '',
                'Hardcover_Edad de lectura': '',
                'Hardcover_Peso del producto': '',
                'Hardcover_Dimensiones': '',

                'Softcover_Asín': '',
                'Softcover_Editorial': '',
                'Softcover_Precio': '',
                'Softcover_Idioma': '',
                'Softcover_Páginas': '',
                'Softcover_ISBN-10': '',
                'Softcover_ISBN-13': '',
                'Softcover_Edad de lectura': '',
                'Softcover_Peso del producto': '',
                'Softcover_Dimensiones': '',
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
        
        for book, formats in books:
            input(print(book[0]))
            for f_title, f_value in formats.items():
                for detail_title, detail_value in f_value.items():
                    ordered_formats[f_title][detail_title].append(detail_value)
        pprint(ordered_formats)
        input("end order, press to continue")

    def navigate_formats(self):
        format_links = self.extract_formats() 
        if format_links:
            for name, link in format_links.items():
                self.driver.get(link)
                time.sleep(2)
                description_list = self.find_elements(FormatLocators.LIST_VALUES, "innerText")
                description_table = self.find_elements(FormatLocators.TABLE_VALUE, "innerText")
                descriptions = description_list or description_table

                if name == 'Kindle':
                    self.book_data['Kindle_Asín'] = descriptions[0] if len(descriptions) > 0 else ''
                    self.book_data['Kindle_Editorial'] = descriptions[1] if len(descriptions) > 1 else ''
                    self.book_data['Kindle_Tamaño del archivo'] = descriptions[2] if len(descriptions) > 2 else ''
                    self.book_data['Kindle_Texto a voz'] = descriptions[3] if len(descriptions) > 3 else ''
                    self.book_data['Kindle_Lector de pantalla'] = descriptions[4] if len(descriptions) > 4 else ''
                    self.book_data['Kindle_Tipografia mejorada'] = descriptions[5] if len(descriptions) > 5 else ''
                    self.book_data['Kindle_Word Wise'] = descriptions[6] if len(descriptions) > 6 else ''
                    self.book_data['Kindle_Paginas'] = descriptions[7] if len(descriptions) > 7 else ''
                    self.book_data['Kindle_En Kindle Scribe'] = descriptions[8] if len(descriptions) > 8 else ''
                    self.book_data['Kindle_Precio'] = descriptions[9] if len(descriptions) > 9 else ''
                    self.book_data['Kindle_Tiempo'] = descriptions[10] if len(descriptions) > 10 else ''
                    self.book_data['Kindle_Autor'] = descriptions[11] if len(descriptions) > 11 else ''
                    self.book_data['Kindle_Narrador'] = descriptions[12] if len(descriptions) > 12 else ''
                    self.book_data['Kindle_Fecha de lanzamiento'] = descriptions[13] if len(descriptions) > 13 else ''
                    self.book_data['Kindle_Editor'] = descriptions[14] if len(descriptions) > 14 else ''
                    self.book_data['Kindle_Version'] = descriptions[15] if len(descriptions) > 15 else ''
                    self.book_data['Kindle_Idioma'] = descriptions[16] if len(descriptions) > 16 else ''
                    self.book_data['Kindle_Asin'] = descriptions[17] if len(descriptions) > 17 else ''
                    self.book_data['Kindle_Acento'] = descriptions[18] if len(descriptions) > 18 else ''
                    

                elif name == 'Audiobook':
                    self.book_data['Audiobook_Asín'] = descriptions[0] if len(descriptions) > 0 else ''
                    self.book_data['Audiobook_Editorial'] = descriptions[1] if len(descriptions) > 1 else ''
                    self.book_data['Audiobook_Precio'] = descriptions[2] if len(descriptions) > 2 else ''
                    self.book_data['Audiobook_Idioma'] = descriptions[3] if len(descriptions) > 3 else ''
                    self.book_data['Audiobook_Paginas'] = descriptions[4] if len(descriptions) > 4 else ''
                    self.book_data['Audiobook_ISBN-10'] = descriptions[5] if len(descriptions) > 5 else ''
                    self.book_data['Audiobook_ISBN-13'] = descriptions[6] if len(descriptions) > 6 else ''
                    self.book_data['Audiobook_Edad de lectura'] = descriptions[7] if len(descriptions) > 7 else ''
                    self.book_data['Audiobook_Peso del prodocto'] = descriptions[8] if len(descriptions) > 8 else ''
                    self.book_data['Audiobook_Dimensiones'] = descriptions[9] if len(descriptions) > 9 else ''
                    

                elif name == 'Hardcover':
                    self.book_data['Hardcover_Asín'] = descriptions[0] if len(descriptions) > 0 else ''
                    self.book_data['Hardcover_Editorial'] = descriptions[1] if len(descriptions) > 1 else ''
                    self.book_data['Hardcover_Precio'] = descriptions[2] if len(descriptions) > 2 else ''
                    self.book_data['Hardcover_Idioma'] = descriptions[3] if len(descriptions) > 3 else ''
                    self.book_data['Hardcover_Paginas'] = descriptions[4] if len(descriptions) > 4 else ''
                    self.book_data['Hardcover_ISBN-10'] = descriptions[5] if len(descriptions) > 5 else ''
                    self.book_data['Hardcover_ISBN-13'] = descriptions[6] if len(descriptions) > 6 else ''
                    self.book_data['Hardcover_Edad de lectura'] = descriptions[7] if len(descriptions) > 7 else ''
                    self.book_data['Hardcover_Peso del producto'] = descriptions[8] if len(descriptions) > 8 else ''
                    self.book_data['Hardcover_Dimensiones'] = descriptions[9] if len(descriptions) > 9 else ''
                    

                elif name == 'Softcover':
                    self.book_data['Softcover_Asín'] = descriptions[0] if len(descriptions) > 0 else ''
                    self.book_data['Softcover_Editorial'] = descriptions[1] if len(descriptions) > 1 else ''
                    self.book_data['Softcover_Precio'] = descriptions[2] if len(descriptions) > 2 else ''
                    self.book_data['Softcover_Idioma'] = descriptions[3] if len(descriptions) > 3 else ''
                    self.book_data['Softcover_Paginas'] = descriptions[4] if len(descriptions) > 4 else ''
                    self.book_data['Softcover_ISBN-10'] = descriptions[5] if len(descriptions) > 5 else ''
                    self.book_data['Softcover_ISBN-13'] = descriptions[6] if len(descriptions) > 6 else ''
                    self.book_data['Softcover_Edad de lectura'] = descriptions[7] if len(descriptions) > 7 else ''
                    self.book_data['Softcover_Peso del producto'] = descriptions[8] if len(descriptions) > 8 else ''
                    self.book_data['Softcover_Dimensiones'] = descriptions[9] if len(descriptions) > 9 else ''
                    
            return self.book_data
        
    def navigating_books(self, urls):
        books = []
        for url in urls:
            self.driver.get(url)
            time.sleep(0.5)
            try:
                book = self.extract_book_data()
                print(f"Book data: {book}")
                descriptions = self.navigate_formats()
                book.update(descriptions)
            except Exception as error:
                print(f"An error occurred: {error}")
                pass
            if book:
                books.append(book)
        return books
    
    def product_information_spreadsheet(self, book_data):

        print("\n>> Creating an excel sheet and entering the details...")
        keys = book_data[0].keys()
        with open('books.csv', 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
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
         
    my_amazon_bot.product_information_spreadsheet(all_books)
    my_amazon_bot.driver.close()