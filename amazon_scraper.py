import time
from datetime import date
import csv
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
        #self. driver = webdriver.Chrome(service=Service(driver_path), options=opt)
        self. driver = webdriver.Chrome(options=opt)
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
        # Parsing through the webpage
        #soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # List of all the html information related to the product
        #page_results = soup.find_all('div', {'data-component-type': 's-search-result'})
        books_links = [book.get_attribute("href") for book in self.driver.find_elements(*MainLocators.BOOKS)]
    
        #input(print(f'books:{books_links}'))
        return books_links
    
    def navigating_books(self, urls):
        books = []
        for url in urls:
            self.driver.get(url)
            time.sleep(0.2)
            try:
                book = self.extract_book_data()
                self.navigate_formats()
            except Exception as error:
                pass
            print(book)
            books.append(book)
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
            #text = "".join([tag.get_attribute('innerText') for tag in self.driver.find_elements(*locator)])
            text = [tag.get_attribute(attribute) for tag in self.driver.find_elements(*locator)]
        except Exception as error:
            text = ""
        #input(print(f'text: {text}'))
        return text

    def extract_book_data(self): 
        return (
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
                )

    def isLocator(locator, attribute):
        try: 
            element = self._find_element(locator, attribute)
            return True
        except Exception as error:
            #element = ""
            return False
    
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

    def navigate_formats(self):
        descriptions = []
        #format_links = self.find_elements(BookLocators.FORMATS_LINKS, "href")
        #format_links = [self.find_elements(BookLocators.FORMATS_LINKS, "href")]
        format_links = self.extract_formats() 
        #print(f'format_links: {format_links}')
        ##print(f'num_formats: {len(format_links)}')
        ##original_window = self.driver.current_window_handle
        if format_links:
            for name, link in format_links.items():
            #    #self.driver.switch_to.new_window('tab')
                print(f'format_name: {name}')
                print(f'go to  url: {link}')
                self.driver.get(link)
                time.sleep(3)
            #   # #print("---->element")
                ##element = self.driver.find_element(*FormatLocators.CHECK_LIST)
                ##element = self._find_element(FormatLocators.CHECK_LIST, "innerText")
                description_text = self.find_elements(FormatLocators.LIST_VALUES, "innerText")
                print(description_text)
                #if description_text:
                #    descriptions += description_text 
                ##element = element.get_attribute("innerText")
                #print(f'element: {element}')
                ##is_locator = self.isLocator(FormatLocators.CHECK_LIST, "innerText")
                ##print(f'islocator: {is_locator}')
            #   # #if self.driver.find_element(*FormatLocators.TEST_UL).get_attribute("innerText"):
            #   # ###if self.isLocator(FormatLocators.CHECK_LIST, "innerText"):
            #   # ###    print(self.driver.find_elements(*FormatLocators.LIST_VALUES).get_attribute("innerText"))
            #   # ###    print("if checklist_ul")
            #   # ###elif self.isLocator(FormatLocators.CHECK_TABLE, "innerText" ):
            #   # ####elif self.driver.find_element(*FormatLocators.TEST_KEYS).get_attribute("innerText"):
            #   # ###    print(self.driver.find_element(*FormatLocators.TEST_KEYS).get_attribute("innerText"))
            #   # ###    print("if_checklist_table")
            #   #     
            #   # #input(print("test keys"))
            #   # #self.driver.close()
            #   # #self.driver.switch_to.window(original_window)
            #   # print("-" * 100)
            #print(f'descriptions: {descriptions}')


   
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
    my_amazon_bot.product_information_spreadsheet(books)
    

    print(navigation)
    #my_amazon_bot.product_information_spreadsheet(navigation)
