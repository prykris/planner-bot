# import time
import json
import os
import time
from random import choice
from typing import Optional

import pyperclip
from selenium.common import TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from tabulate import tabulate

from driver_setup import driver
from facebook_actions import login_to_facebook, open_event_creation_form
from selenium_buff import paste_content
from inputs import prompt_confirmation
from xpath_map import EVENT_NAME_INPUT, EVENT_DETAILS_TEXTAREA, DATE_INPUT, TIME_INPUT, VISIBILITY_DROPDOWN, \
    IN_PERSON_OPTION, CREATE_EVENT_BUTTON
from storage import load_credentials, save_credentials

from selenium.webdriver.support import expected_conditions as EC

from events_db import events, name, details


def enter_time():
    time_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, TIME_INPUT))
    )

    time_input.click()

    time_input.send_keys(Keys.CONTROL + "a")
    time_input.send_keys(event['partial_begin_current'].strftime("%I:%M %p"))
    time_input.send_keys(Keys.RETURN)


def enter_date():
    date_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, DATE_INPUT))
    )

    date_input.click()
    date_input.send_keys(Keys.CONTROL + "a")
    date_input.send_keys(event['partial_begin'].strftime("%b %d, %Y"))
    date_input.send_keys(Keys.RETURN)


def enter_event_name(event_name: str):
    event_name_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, EVENT_NAME_INPUT))
    )

    paste_content(driver, event_name_input, event_name)


def enter_event_details(event_details: str):
    details_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, EVENT_DETAILS_TEXTAREA))
    )

    paste_content(driver, details_input, event_details)


def event_in_person():
    visibility_dropdown_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, VISIBILITY_DROPDOWN))
    )

    visibility_dropdown_element.click()

    in_person_option_element = WebDriverWait(driver, 10).until(
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
        input = WebDriverWait(driver, 10).until(
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

    input.click()

    time.sleep(2)

    input.send_keys(f'{city}, {state}')


def enter_location(city: str, state: str):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//label[@aria-label='Is it in person or virtual?']"))
    ).click()

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@role="option"][1]'))
    ).click()

    write_location(city, state)


if __name__ == "__main__":
    print('Starting Event Planner Bot v0.1.0!')

    # Try to load saved credentials
    email, password = load_credentials()

    # If not available, ask the user
    if email is None or password is None:
        email = input('Enter email: ')
        password = input('Enter password: ')
        save_credentials(email, password)
        print('Credentials saved to credentials.json, delete this file to change or edit the file manually.')
    else:
        print('Credentials loaded from credentials.json. To switch accounts delete the file or edit it manually.')

    try:
        print(f'Logging into Facebook with email {email}...')
        # Login to Twitter
        if not login_to_facebook(email, password):
            raise Exception('Login failed! Check your credentials.')

        if not prompt_confirmation('Login successful! Manually switch the page.'):
            exit()

        for event, metadata, metadata_file in events('../events/filtered_events.json', 50000, 0.5):
            # Skip events that have already been completed or failed
            if not metadata['status'] == 'Pending':
                print(
                    f'Skipping city {event["city_ascii"]}, {event["admin_name"]} (ID: {event["id"]}) (Status: {metadata["status"]})')
                continue

            event_name = name(event)
            event_details = details(event)

            metadata['event_name'] = event_name
            metadata['event_details'] = event_details
            metadata['image'] = select_random_image('../images')

            print(f'Creating event for city {event["city_ascii"]}, {event["admin_name"]} (ID: {event["id"]})...')

            try:
                open_event_creation_form()

                enter_event_name(event_name)

                enter_event_details(event_details)

                enter_date()

                enter_time()
            except UnexpectedAlertPresentException:
                print('Unexpected alert. Skipping this city.')
                continue
            except TimeoutException as e:
                print('Failed to find element in time. Skipping this city.')
                print(e.msg)
                continue
            except:
                print('Unexpected error. Skipping this city.')
                continue

            enter_location(event['city_ascii'], event['admin_name'])

            if metadata['image'] is not None:
                upload_picture(metadata['image'])
            else:
                print('No image selected.')

            print(tabulate([
                ["Latitude", "Longitude", "Begin (Local)", "Begin (Current)", "Timezone"],
                [event['latitude'], event['longitude'], event['partial_begin'], event['partial_begin_current'],
                 event['timezone']],
            ], headers="firstrow", tablefmt="pipe"))

            should_click_create = prompt_confirmation('Post the event?')

            if should_click_create:
                try:
                    create_event_button = WebDriverWait(driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, CREATE_EVENT_BUTTON))
                    )

                    create_event_button.click()
                    time.sleep(5)
                    print('Create event button clicked!')
                except TimeoutException:
                    print('Create event button missing. or you probably clicked it manually.')
                    print('Therefore it will be considered as submitted event. Wait for the next one ...')
                except:
                    print('There was an unexpected error. If the event is not yet posted, post it manually.')
                    prompt_confirmation('Can we continue?')

                print('Event created!')

            metadata['status'] = 'Submitted'
            # if metadata['image'] is not None:
            # else:
            #     print('Aborting...')
            #     # metadata["status"] = "Cancelled"

            # Save the metadata
            with open(metadata_file, "w") as file:
                json.dump(metadata, file)

            if should_click_create:
                time.sleep(10)

        time.sleep(5)
    except Exception as e:
        raise e

    # Wait until all Chrome windows are closed
    while len(driver.window_handles) > 0:
        time.sleep(1)  # Wait for 1 second before checking again

    driver.quit()
