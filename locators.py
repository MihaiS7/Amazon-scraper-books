from selenium.webdriver.common.by import By

class MainLocators():
    BOOKS = (By.XPATH, '//span[@data-component-type="s-product-image"]/a')

class BookLocators():
    AUTHOR =(By.XPATH, '//span[@class="author notFaded"]/span/span[contains(text(), "Autor")]/../../a')
    TITLE = (By.XPATH, '//span[@id="productTitle"]')
    PRICE = (By.XPATH, '//span[@id="price"]')
    CATEGORY_1 = (By.XPATH, '//div[@id="wayfinding-breadcrumbs_feature_div"]/ul/li[3]/span/a')
    CATEGORY_2 =(By.XPATH, '//div[@id="wayfinding-breadcrumbs_feature_div"]/ul/li[5]/span/a')
    RATING = (By.XPATH, '//div[@id="averageCustomerReviews_feature_div"]//a[@role]/span')
    REVIEW_COUNT =(By.XPATH, '//div[@id="averageCustomerReviews_feature_div"]//span[@id="acrCustomerReviewText"]')
    LANGUAGE =(By.XPATH, '//div[@id="detailBullets_feature_div"]/ul/li[2]/span[@class="a-list-item"]/span[last()]')
    DIMENTIONS =(By.XPATH, '//div[@id="detailBullets_feature_div"]/ul/li[last()]/span[@class="a-list-item"]/span[last()]')
    FORMATS = (By.XPATH, '//div[@id="tmmSwatches"]//ul//li//span[@class="a-button-inner"]/a/span')
    FORMATS_BLOCK = (By.XPATH, '//div[@id="tmmSwatches"]//ul//li//span[@class="a-button-inner"]//a')
    FORMATS_LINKS = (By.XPATH, '//div[@id="tmmSwatches"]//ul//li//span[@class="a-button-inner"]/a/span[1]')
    FORMATS_LINKS2 = (By.XPATH, '//div[@id="tmmSwatches"]//ul//li//span[@class="a-button-inner"]/a')
    PUBLICATION = (By.XPATH, '//*[@id="rpi-attribute-book_details-publication_date"]/div[3]')
    AUDIO_TIME = (By.XPATH, '//*[@id="rpi-attribute-audiobook_details-listening_length"]/div[3]')
    ASIN = (By.XPATH, '//*[@id="detailsAsin"]/td/span')

    # Formats
    KINDLE = (By.XPATH, '//*[@id="a-autoid-3-announce"]')
    AUDIO_BOOK = (By.XPATH, '//*[@id="a-autoid-6-announce"]')
    PAPER_BOOK = (By.XPATH, '//*[@id="a-autoid-5-announce"]')

class FormatLocators():
    TITLE = (By.XPATH, './/br/preceding-sibling::span')
    PRICE = (By.XPATH, './/br//preceding-sibling::span/../span[2]')
    DETAIL_TABLE = (By.XPATH, '//div[contains(@id,"productdetails")]//tbody//tr/')
    TEST_KEYS = (By.XPATH, '//div[contains(@id,"productdetails")]//tbody//tr/th/span')
    TEST_UL = (By.XPATH, '//*[@id="detailBullets_feature_div"]/ul/li')
    TABLE_KEY = (By.XPATH, './th')
    #TABLE_VALUE = (By.XPATH, './td')
    CHECK_LIST = (By.XPATH, '//*[@id="detailBullets_feature_div"]/ul')
    CHECK_TABLE = (By.XPATH, '//div[contains(@id,"productdetails")]//tbody')
    LIST_VALUES = (By.XPATH, '//div[@id="detailBullets_feature_div"]/ul/li/span/span[2]') 
    TABLE_VALUE = (By.XPATH, '//div[contains(@id,"productdetails")]//tbody//tr/td')  
