from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def initialize_driver():
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--disable-notifications')

    return webdriver.Chrome(options=chrome_options)


driver = initialize_driver()
