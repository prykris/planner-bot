# import time
import json
import os
import time
from random import choice
from typing import Optional

import pyperclip
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tabulate import tabulate

from driver_setup import driver
from events_db import events, name, details
from facebook_actions import login_to_facebook
from inputs import prompt_confirmation
from selenium_buff import paste_content
from storage import load_credentials, save_credentials
from xpath_map import EVENT_NAME_INPUT, EVENT_DETAILS_TEXTAREA, DATE_INPUT, TIME_INPUT, VISIBILITY_DROPDOWN, \
    IN_PERSON_OPTION, END_DATE_BUTTON, TIME_END_INPUT, DATE_END_INPUT


def enter_time():
    time_input = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, TIME_INPUT))
    )

    time_input.click()

    time_input.send_keys(Keys.CONTROL + "a")
    time_input.send_keys(event['partial_begin_current'].strftime("%I:%M %p"))
    time_input.send_keys(Keys.RETURN)


def enter_date():
    date_input = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, DATE_INPUT))
    )

    date_input.click()
    date_input.send_keys(Keys.CONTROL + "a")
    date_input.send_keys(event['partial_begin_current'].strftime("%b %d, %Y"))
    date_input.send_keys(Keys.RETURN)


def enter_end_time():
    time_input = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, TIME_END_INPUT))
    )

    time_input.click()

    time_input.send_keys(Keys.CONTROL + "a")
    time_input.send_keys(event['partial_end_current'].strftime("%I:%M %p"))
    time_input.send_keys(Keys.RETURN)


def enter_end_date():
    date_input = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, DATE_END_INPUT))
    )

    date_input.click()
    date_input.send_keys(Keys.CONTROL + "a")
    date_input.send_keys(event['partial_end_current'].strftime("%b %d, %Y"))
    date_input.send_keys(Keys.RETURN)


def enter_event_name(event_name_: str):
    event_name_input = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, EVENT_NAME_INPUT))
    )

    paste_content(driver, event_name_input, event_name_)


def enter_event_details(event_details_: str):
    details_input = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, EVENT_DETAILS_TEXTAREA))
    )

    paste_content(driver, details_input, event_details_)


def event_in_person():
    visibility_dropdown_element = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, VISIBILITY_DROPDOWN))
    )

    visibility_dropdown_element.click()

    in_person_option_element = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, IN_PERSON_OPTION))
    )

    in_person_option_element.click()


def select_random_image(directory: str) -> Optional[str]:
    # Convert the directory path to an absolute path
    directory = os.path.abspath(directory)

    # Check if the directory exists
    if not os.path.exists(directory):
        return None

    # Get a list of all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Check if there are any files in the directory
    if not files:
        return None

    # Choose a random file from the list
    random_file = choice(files)

    # Get the full path of the random file
    full_path = os.path.join(directory, random_file)

    return full_path


def upload_picture(image_path: str) -> None:
    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )

    file_input.send_keys(image_path)


def write_location(city, state, repeat=True):
    try:
        add_location_input = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Add location']"))
        )
    except TimeoutException:
        print("Location input couldn't be found, enter the location manually.")
        print("it has been inserted into your clipboard, use ctrl+v to paste.")
        pyperclip.copy(f'{city}, {state}')

        if repeat:
            write_location(city, state, False)

        prompt_confirmation("Is location set?")
        return

    add_location_input.click()

    time.sleep(2)

    add_location_input.send_keys(f'{city}, {state}')


def enter_location(city: str, state: str):
    WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, "//label[@aria-label='Is it in person or virtual?']"))
    ).click()

    WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@role="option"][1]'))
    ).click()

    write_location(city, state)


def add_end_date():
    WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, END_DATE_BUTTON))
    ).click()


if __name__ == "__main__":
    print('Starting Event Planner Bot v0.1.0!')

    # Try to load saved credentials
    email, password = load_credentials()

    # If not available, ask the user
    if email is None or password is None:
        email = input('Enter email: ')
        password = input('Enter password: ')
        save_credentials(email, password)
        print(
            'Akreditācijas dati saglabāti failā "credentials.json". Lai mainītu vai rediģētu datus, dzēsiet šo failu '
            'vai rediģējiet to manuāli.')
    else:
        print(
            'Akreditācijas dati ielādēti no faila "credentials.json". Lai pārslēgtu kontus, dzēsiet failu vai '
            'rediģējiet to manuāli.')

    try:
        print(f'Ienākam Facebook ar e-pastu {email}...')
        # Login to Twitter
        if not login_to_facebook(email, password):
            raise Exception('Ielogošanās neizdevās! Pārbaudiet savus akreditācijas datus.')

        if not prompt_confirmation('Ielogojies veiksmīgi! Manuāli pārslēdzies uz lapu.'):
            exit()

        for event, metadata, metadata_file in events('../events/filtered_events.json', 50000, 0.5):
            # Skip events that have already been completed or failed
            if not metadata['status'] == 'Pending':
                # print(
                #     f'Skipping city {event["city_ascii"]}, {event["admin_name"]} (ID: {event["id"]}) (Status: {metadata["status"]})')
                continue
            if prompt_confirmation('Lai atvērtu pasākumu izveides lapu nospiediet Enter'):
                driver.get('https://facebook.com/events/create')
            else:
                print('Gaidam, kad atvērsies pasākumu izveides lapu: https://facebook.com/events/create.')

            try:
                WebDriverWait(driver, 1).until(EC.alert_is_present())

                driver.switch_to.alert.accept()
            except TimeoutException:
                pass
            WebDriverWait(driver, 60 * 60).until(
                EC.url_contains('facebook.com/events/create')
            )

            event_name = name(event)
            event_details = details(event)

            metadata['event_name'] = event_name
            metadata['event_details'] = event_details
            metadata['image'] = select_random_image('../images')

            print(f'Izveidojam pasākumu pilsētai {event["city_ascii"]}, {event["admin_name"]} (ID: {event["id"]})...')

            print(tabulate([
                ["Latitude", "Longitude", event['timezone'], "Europe/Riga", "Timezone"],
                [
                    event['latitude'], event['longitude'], event['partial_begin'], event['partial_begin_current']
                ],
                [
                    "", "", event['partial_end'], event['partial_end_current']
                ]
            ], headers="firstrow", tablefmt="pipe"))

            try:
                enter_event_name(event_name)
            except Exception:
                print('Notika negaidīta kļūda ievadot pasākuma nosaukumu.')

            try:
                enter_event_details(event_details)
            except Exception:
                print('Notika negaidīta kļūda ievadot pasākuma tekstu.')

            try:
                enter_date()
            except Exception:
                print('Notika negaidīta kļūda ievadot pasākuma sākuma datumu.')

            try:
                enter_time()
            except:
                print('Notika negaidīta kļūda ievadot pasākuma sākuma laiku.')

            try:
                add_end_date()
            except:
                print('Notika negaidīta kļūda pievienojot pasākumam beigu datumu.')

            try:
                enter_end_date()
            except:
                print('Notika negaidīta kļūda ievadot pasākuma beigu datumu.')

            try:
                enter_end_time()
            except:
                print('Notika negaidīta kļūda ievadot pasākuma beigu laiku.')

            try:
                enter_location(event['city_ascii'], event['admin_name'])
            except:
                print('Notika kļūda ievadot pasākuma vietu.')

            try:
                if metadata['image'] is not None:
                    upload_picture(metadata['image'])
                else:
                    print('No image selected.')
            except:
                print('Notika kļūda ievadot pasākuma attēlu.')

            event_posted = prompt_confirmation('Lai saglabātu šo pasākumu kā izveidotu, lūdzu nospiediet ENTER. '
                                               'Pretējā gadījumā ievadiet \'N\' un tad nospiedet ENTER')

            if event_posted:
                metadata['status'] = 'Submitted'
                print('Event posted!')
            else:
                metadata['status'] = 'Cancelled'
                print('Event cancelled!')

            metadata['confirmed'] = event_posted

            # Save the metadata
            with open(metadata_file, "w") as file:
                json.dump(metadata, file)

        time.sleep(5)
    except Exception as e:
        raise e

    # Wait until all Chrome windows are closed
    while len(driver.window_handles) > 0:
        time.sleep(1)  # Wait for 1 second before checking again

    driver.quit()
