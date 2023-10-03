import time

from selenium.common import TimeoutException, ElementClickInterceptedException, UnexpectedAlertPresentException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from driver_setup import driver
from xpath_map import LOGIN_EMAIL_INPUT, LOGIN_PASSWORD_INPUT, LOGIN_BUTTON, ACCEPT_COOKIES_BUTTON


def accept_cookies() -> bool:
    try:
        driver.find_element(By.XPATH, ACCEPT_COOKIES_BUTTON).click()
        return True
    except:
        return False


def login_to_facebook(email: str, password: str) -> bool:
    driver.get("https://www.facebook.com/")
    time.sleep(2)

    # Enter the username
    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, LOGIN_EMAIL_INPUT))
        )

        email_input.send_keys(email)
        pass
    except TimeoutException:
        print("No username input detected within 10 seconds, quitting...")
        return False

    # Enter the password
    try:
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, LOGIN_PASSWORD_INPUT))
        )

        password_input.send_keys(password)
    except TimeoutException:
        print("No password input detected within 10 seconds, quitting...")
        return False

    # Click the login button
    accept_cookies()
    time.sleep(1)

    while True:
        attempt = 0
        try:
            attempt += 1

            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, LOGIN_BUTTON))
            )

            login_button.click()
            break
        except ElementClickInterceptedException:
            print(f"Login button not clickable. Perhaps some overlay is obstructing the button.")
            print(f"trying again... [{attempt}]")
            accept_cookies()
            time.sleep(1)
        except TimeoutException:
            print(f"Login button missing, trying again... [{attempt}]")
            accept_cookies()
            time.sleep(1)

    return True


def open_event_creation_form():
    try:
        driver.get("https://www.facebook.com/events/create/")
    except UnexpectedAlertPresentException:
        time.sleep(3)
        driver.get("https://www.facebook.com/events/create/")
