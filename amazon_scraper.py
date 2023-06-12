import time
from collections import defaultdict
from itertools import chain, cycle
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

format_fields = defaultdict(set)

class AmazonProductScraper:
    def __init__(self):
        self.driver = None
        self.category_name = None
        self.formatted_category_name = None

    def open_browser(self):

        opt = Options()

        opt.add_argument("--disable-infobars")
        opt.add_argument("--disable-extensions")
        opt.add_argument('--log-level=OFF')
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])

        url = "https://www.amazon.es/"
        driver_path = "chromedriver"
        self. driver = webdriver.Chrome(service=Service(driver_path), options=opt)
        # Website URL
        self.driver.get(url)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.NAME, 'accept'))
        )
        accept_button = self.driver.find_element(By.NAME, 'accept')
        accept_button.click()


        # Wait till the page has been loaded
        time.sleep(3)

    def get_category_url(self):

        self.category_name = input("\n>> Enter the product/category to be searched: ")

        self.formatted_category_name = self.category_name.replace(" ", "+")

        # This is the product url format for all products
        category_url = "https://www.amazon.es/s?k={}&ref=nb_sb_noss"

        category_url = category_url.format(self.formatted_category_name)

        print(">> Category URL: ", category_url)

        # Go to the product webpage
        self.driver.get(category_url)
        # To be used later while navigating to different pages
        return category_url

    def extract_webpage_information(self):
        books_links = [book.get_attribute("href") for book in self.driver.find_elements(*MainLocators.BOOKS)]
        return books_links
    
    def navigating_books(self, urls):
        books = []
        for num, url in enumerate(urls, 1):
            print(f'num_url: {num} ')
            self.driver.get(url)
            time.sleep(0.2)
            book = self.extract_book_data()
            descriptions = self.navigate_formats()
            book = (book, descriptions)
            books.append(book)
            print(books)
            if num == 5:
                break
            #return books
            #break
            #break
        self.driver.close()
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
                #" ".join(self.find_elements(BookLocators.FORMATS,"innerText")),
                ]

    
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
            
        #input(formats)
        return formats

    def _find_element(self, locator, attribute):
        try:
            text = self.driver.find_element(*locator).get_attribute(attribute)
        except Exception as error:
            text = ""
        return text

    
    def order(self, books):
        """analize the formats and give order to blank values"""
        print(format_fields)
        ##input("show format_fields")
        ordered_formats = defaultdict(lambda : defaultdict(list))
        books_ = [] 
        
        #input(print(f"quantity of books: {len(books)}"))
        
        for book, formats in books:
            ##input(print(book[0]))
            formats_to_fill  = list(zip(set(format_fields.keys()).difference(set(formats.keys())), cycle([''])))
            print(formats_to_fill)
            ##input("not_present_formats")
            for f_title, f_value in chain(formats.items(), formats_to_fill):
                #ordered_formats[f_title] = defaultdict(list)
                #ordered_formats[f_title]
                if not f_value:
                    f_value = {}
                values_to_fill  = list(zip(format_fields[f_title].difference(set(f_value.keys())), cycle([''])))
                ##print(values_to_fill)
                ##input("values_to_fill")
                for detail_title, detail_value in chain(f_value.items(), values_to_fill):
                    ordered_formats[f_title][detail_title].append(detail_value)
                    #book.append(detail_value)
            books_.append(book)
        all_values = [] 
        for values in ordered_formats.values():
            for list_values in values.values():
                all_values.append(list_values)
        
        ordered_formats = list(zip(*all_values))
        final_list = []
        for index in range(len(ordered_formats)):
            final_list.append(books_[index] + list(ordered_formats[index]))
            

        print(final_list)
        input("final_list")
        return final_list
        

    def navigate_formats(self):
        descriptions = {}
        format_links = self.extract_formats() 
        if format_links:
            for name, link in format_links.items():
                print(f'format_name: {name}')
                print(f'go to  url: {link}')
                self.driver.get(link)
                time.sleep(1)
                list_keys = [title.text.replace(":", "").strip() for title in self.driver.find_elements(*FormatLocators.DETAIL_LIST_TITLES)] 
                list_values = [values.text.strip() for values in self.driver.find_elements(*FormatLocators.DETAIL_LIST_VALUES)] 
                table_keys = [title.text for title in self.driver.find_elements(*FormatLocators.TEST_KEYS)]
                table_values = [values.text for values in self.driver.find_elements(*FormatLocators.TEST_VALUES)]
                if list_keys:
                    print("list_keys")
                #    #descriptions += description_list_value
                    descriptions[name] = dict(zip(list_keys, list_values))                    
                    print(list_values)
                    format_fields[name].update(list_keys)
                    #print(list_values)
                elif table_keys:
                    print("list_table")
                #    #descrioptions += description_table_keys
                    descriptions[name] = dict(zip(table_keys, table_values))                    
                    format_fields[name].update(list_keys)
                    print(table_keys)
                list_keys = []
                table_keys = []
                list_values = []
                table_values = []
                #print(descriptions)
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
    
            extraction_information = ">> Page {} - webpage information extracted"
            #$print(extraction_information.format(i))
            break
    
    
    
    
        return book_links

    def product_information_spreadsheet(self, records):

        print("\n>> Creating an excel sheet and entering the details...")
        today = date.today().strftime("%d-%m-%Y")

        for _ in records:
            file_name = "{}_{}.csv".format(self.category_name, today)
            f = open(file_name, "w", newline='', encoding='utf-8')
            writer = csv.writer(f)
            writer.writerow(['Title', 'Author', 'Price', 'Category1', 'Category 2', 'Rating', 'Review Count', 'Product URL', 'Language', 'Dimensions', 'Formats'])
            writer.writerows(records)
            f.close()

        message = f">> Information about the product '{self.category_name}' is stored in {file_name}\n"

        print(message)

        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, file_name])


if __name__ == "__main__":
    my_amazon_bot = AmazonProductScraper()

    my_amazon_bot.open_browser()

    category_details = my_amazon_bot.get_category_url()

    #my_amazon_bot.extract_product_information(my_amazon_bot.extract_webpage_information())

    navigation = my_amazon_bot.navigate_pages(category_details)
    
    books = my_amazon_bot.navigating_books(navigation)
    books = my_amazon_bot.order(books)
    input("pause2000")
    my_amazon_bot.product_information_spreadsheet(books)
    

    print(navigation)
    #my_amazon_bot.product_information_spreadsheet(navigation)
