from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def initialize_driver():
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--disable-notifications')
    # chrome_options.headless = True
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
