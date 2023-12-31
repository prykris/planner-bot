import time
from typing import List

import pyperclip
from selenium.common import TimeoutException, ElementClickInterceptedException, UnexpectedAlertPresentException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from language import Language
from selenium_buff import paste_content
from prompts import confirm
from tabulate import tabulate
from xpath_map import LOGIN_EMAIL_INPUT, LOGIN_PASSWORD_INPUT, LOGIN_BUTTON, ACCEPT_COOKIES_BUTTON, TIME_INPUT, \
    TIME_END_INPUT, IN_PERSON_OPTION, VISIBILITY_DROPDOWN, EVENT_DETAILS_TEXTAREA, EVENT_NAME_INPUT, DATE_INPUT, \
    DATE_END_INPUT, END_DATE_BUTTON

from events import name, details
from resource import select_random_image


class FacebookControls:
    def __init__(self, driver, credentials: List[str], language: Language):
        self.driver = driver
        self.credentials = credentials
        self.language = language
        self.loggedIn = False
        pass

    def enter_event(self, event: dict):
        pass

    def accept_cookies(self) -> bool:
        try:
            self.driver.find_element(By.XPATH, ACCEPT_COOKIES_BUTTON).click()
            return True
        except:
            return False

    def login(self) -> bool:
        email, password = self.credentials

        if email is None or password is None:
            return False

        self.driver.get("https://www.facebook.com/")
        time.sleep(2)

        # Enter the username
        try:
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, LOGIN_EMAIL_INPUT))
            )

            email_input.send_keys(email)
            pass
        except TimeoutException:
            print("No username input detected within 10 seconds, quitting...")
            return False

        # Enter the password
        try:
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, LOGIN_PASSWORD_INPUT))
            )

            password_input.send_keys(password)
        except TimeoutException:
            print("No password input detected within 10 seconds, quitting...")
            return False

        # Click the login button
        self.accept_cookies()
        time.sleep(1)

        while True:
            attempt = 0
            try:
                attempt += 1

                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, LOGIN_BUTTON))
                )

                login_button.click()
                break
            except ElementClickInterceptedException:
                print(f"Login button not clickable. Perhaps some overlay is obstructing the button.")
                print(f"trying again... [{attempt}]")
                self.accept_cookies()
                time.sleep(1)
            except TimeoutException:
                print(f"Login button missing, trying again... [{attempt}]")
                self.accept_cookies()
                time.sleep(1)

        self.loggedIn = True

        return True

    def open_event_creation_form(self) -> None:
        try:
            self.driver.get("https://www.facebook.com/events/create/")
        except UnexpectedAlertPresentException:
            time.sleep(3)
            self.driver.get("https://www.facebook.com/events/create/")

    def enter_time(self, event: dict, end: bool):
        time_input = WebDriverWait(self.driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, TIME_INPUT if end is False else TIME_END_INPUT))
        )

        time_input.click()

        date_key = 'partial_begin_current' if end is False else 'partial_end_current'

        time_input.send_keys(Keys.CONTROL + "a")
        time_input.send_keys(event[date_key].strftime(
            "%I:%M %p" if self.language is Language.English else "%H:%M")
        )
        time_input.send_keys(Keys.RETURN)

    def enter_date(self, event: dict, end: bool):
        date_input = WebDriverWait(self.driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, DATE_INPUT if end is False else DATE_END_INPUT))
        )

        date_key = 'partial_begin_current' if end is False else 'partial_end_current'

        date_input.click()
        date_input.send_keys(Keys.CONTROL + "a")
        date_input.send_keys(event[date_key].strftime("%b %d, %Y"))
        date_input.send_keys(Keys.RETURN)

    def enter_event_name(self, event_name_: str):
        event_name_input = WebDriverWait(self.driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, EVENT_NAME_INPUT))
        )

        paste_content(self.driver, event_name_input, event_name_)

    def enter_event_details(self, event_details_: str):
        details_input = WebDriverWait(self.driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, EVENT_DETAILS_TEXTAREA))
        )

        paste_content(self.driver, details_input, event_details_)

    def event_in_person(self):
        visibility_dropdown_element = WebDriverWait(self.driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, VISIBILITY_DROPDOWN))
        )

        visibility_dropdown_element.click()

        in_person_option_element = WebDriverWait(self.driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, IN_PERSON_OPTION))
        )

        in_person_option_element.click()

    def upload_picture(self, image_path: str) -> None:
        file_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )

        file_input.send_keys(image_path)

    def write_location(self, city, state, repeat=True):
        try:
            add_location_input = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Add location']"))
            )
        except TimeoutException:
            print("Nevarēja atrast lokācijas ievades lauciņu, lūdzu ievadiet to manuāli.")
            print("esošā lokācija ir pieejama jūsu starpliktuvē, izmantojiet CTRL + V, lai ielīmētu.")
            pyperclip.copy(f'{city}, {state}')

            if repeat:
                self.write_location(city, state, False)

            confirm("Is location set?")
            return

        add_location_input.click()

        time.sleep(2)

        add_location_input.send_keys(f'{city}, {state}')

    def enter_location(self, city: str, state: str):
        WebDriverWait(self.driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//label[@aria-label='Is it in person or virtual?']"))
        ).click()

        WebDriverWait(self.driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@role="option"][1]'))
        ).click()

        self.write_location(city, state)

    def add_end_date(self):
        WebDriverWait(self.driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, END_DATE_BUTTON))
        ).click()

    def _wait_for_event_form(self):
        try:
            WebDriverWait(self.driver, 1).until(EC.alert_is_present())

            self.driver.switch_to.alert.accept()
        except TimeoutException:
            pass

        try:
            WebDriverWait(self.driver, 60).until(
                EC.url_contains('facebook.com/events/create')
            )
        except TimeoutException:
            raise Exception('Event form not loaded within 60 seconds.')

    def create_event(self, event: dict, metadata: dict) -> None:
        self.open_event_creation_form()
        self._wait_for_event_form()

        event_name = name(event)
        event_details = details(event)

        metadata['event_name'] = event_name
        metadata['event_details'] = event_details
        metadata['image'] = select_random_image('../images')

        print(f'Izveidojam pasākumu pilsētai {event["city_ascii"]}, {event["admin_name"]} (ID: {event["id"]})...')

        print(tabulate([
            ["Platums", "Garums", event['timezone'], "Europe/Riga", "Iedzīvotāju skaits"],
            [
                event['latitude'], event['longitude'], event['partial_begin'], event['partial_begin_current'],
                event['population']
            ],
            [
                "", "", event['partial_end'], event['partial_end_current'], ""
            ]
        ], headers="firstrow", tablefmt="pipe"))

        try:
            self.enter_event_name(event_name)
        except Exception:
            print('Notika negaidīta kļūda ievadot pasākuma nosaukumu.')

        try:
            self.enter_event_details(event_details)
        except Exception:
            print('Notika negaidīta kļūda ievadot pasākuma tekstu.')

        try:
            self.enter_date(event, False)
        except Exception:
            print('Notika negaidīta kļūda ievadot pasākuma sākuma datumu.')

        try:
            self.enter_time(event, False)
        except:
            print('Notika negaidīta kļūda ievadot pasākuma sākuma laiku.')

        try:
            self.add_end_date()
        except:
            print('Notika negaidīta kļūda pievienojot pasākumam beigu datumu.')

        try:
            self.enter_date(event, True)
        except:
            print('Notika negaidīta kļūda ievadot pasākuma beigu datumu.')

        try:
            self.enter_time(event, True)
        except:
            print('Notika negaidīta kļūda ievadot pasākuma beigu laiku.')

        try:
            self.enter_location(event['city_ascii'], event['admin_name'])
        except:
            print('Notika kļūda ievadot pasākuma vietu.')

        try:
            if metadata['image'] is not None:
                self.upload_picture(metadata['image'])
            else:
                print('No image selected.')
        except Exception as e:
            print('Notika kļūda ievadot pasākuma attēlu.', e)

        try:
            # Find the element with the specified selector
            element = self.driver.find_element(
                By.CSS_SELECTOR,
                "span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft.x1120s5i"
            )

            # Change the innerHTML of the element
            self.driver.execute_script('arguments[0].innerHTML = "Pasākums ievadīts! Gatavs turpināt";', element)
        except Exception as e:
            print("Maza kļūme mainot formas titulu:", str(e))
