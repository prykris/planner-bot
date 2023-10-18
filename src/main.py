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
from prompts import prompt_confirmation, select_language, Language
from selenium_buff import paste_content
from storage import load_credentials, save_credentials
from xpath_map import EVENT_NAME_INPUT, EVENT_DETAILS_TEXTAREA, DATE_INPUT, TIME_INPUT, VISIBILITY_DROPDOWN, \
    IN_PERSON_OPTION, END_DATE_BUTTON, TIME_END_INPUT, DATE_END_INPUT


def enter_time(language_: Language, end: bool):
    time_input = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, TIME_INPUT if end is False else TIME_END_INPUT))
    )

    time_input.click()

    date_key = 'partial_begin_current' if end is False else 'partial_end_current'

    time_input.send_keys(Keys.CONTROL + "a")
    time_input.send_keys(event[date_key].strftime(
        "%I:%M %p" if language_ is Language.English else "%H:%M")
    )
    time_input.send_keys(Keys.RETURN)


def enter_date(end: bool):
    date_input = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, DATE_INPUT if end is False else DATE_END_INPUT))
    )

    date_key = 'partial_begin_current' if end is False else 'partial_end_current'

    date_input.click()
    date_input.send_keys(Keys.CONTROL + "a")
    date_input.send_keys(event[date_key].strftime("%b %d, %Y"))
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
        print("Nevarēja atrast lokācijas ievades lauciņu, lūdzu ievadiet to manuāli.")
        print("esošā lokācija ir pieejama jūsu starpliktuvē, izmantojiet CTRL + V, lai ielīmētu.")
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


events_posted = 0

if __name__ == "__main__":
    print('Starting Event Planner Bot v0.1.0!')

    # Try to load saved credentials
    email, password, language = load_credentials()

    # If not available, ask the user
    if email is None or password is None or language is None:
        email = input('Ievadiet e-pastu: ')
        password = input('Ievadiet paroli: ')
        language = select_language()

        try:
            save_credentials(email, password, language)
            print(
                'Akreditācijas dati saglabāti failā "credentials.json". Lai mainītu vai rediģētu datus, dzēsiet šo failu '
                'vai rediģējiet to manuāli.')
        except Exception as e:
            print('Neizdevās saglabāt akreditācijas failu. Kļūda: ')
            print(e)

    else:
        print(
            'Akreditācijas dati ielādēti no faila "credentials.json". Lai pārslēgtu kontus, dzēsiet failu vai '
            'rediģējiet to manuāli.')

    print('Facebook valoda: ' + str(language))

    try:
        print(f'Ienākam Facebook ar e-pastu {email}...')
        # Login to Twitter
        if not login_to_facebook(email, password):
            raise Exception('Ielogošanās neizdevās! Pārbaudiet savus akreditācijas datus.')

        if not prompt_confirmation('Ielogošanās veiksmīga! Manuāli pārslēdzieties uz darba lapu, ja nepieciešams.'):
            exit()

        for event, metadata, metadata_file in events('../events/filtered_events.json', 50000, 0.5):
            # Skip events that have already been completed or failed
            if not metadata['status'] == 'Pending':
                # print( f'Skipping city {event["city_ascii"]}, {event["admin_name"]} (ID: {event["id"]}) (Status: {
                # metadata["status"]})')
                continue
            if prompt_confirmation('Lai atvērtu pasākumu izveides lapu nospiediet pogu Enter'):
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
                enter_event_name(event_name)
            except Exception:
                print('Notika negaidīta kļūda ievadot pasākuma nosaukumu.')

            try:
                enter_event_details(event_details)
            except Exception:
                print('Notika negaidīta kļūda ievadot pasākuma tekstu.')

            try:
                enter_date(False)
            except Exception:
                print('Notika negaidīta kļūda ievadot pasākuma sākuma datumu.')

            try:
                enter_time(language, False)
            except:
                print('Notika negaidīta kļūda ievadot pasākuma sākuma laiku.')

            try:
                add_end_date()
            except:
                print('Notika negaidīta kļūda pievienojot pasākumam beigu datumu.')

            try:
                enter_date(True)
            except:
                print('Notika negaidīta kļūda ievadot pasākuma beigu datumu.')

            try:
                enter_time(language, True)
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

            try:
                # Find the element with the specified selector
                element = driver.find_element(
                    By.CSS_SELECTOR,
                    "span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft.x1120s5i"
                )

                # Change the innerHTML of the element
                driver.execute_script('arguments[0].innerHTML = "Pasākums ievadīts! Gatavs turpināt";', element)
            except Exception as e:
                print("Maza kļūme mainot formas titulu:", str(e))

            event_posted = prompt_confirmation('Lai saglabātu šo pasākumu kā izveidotu, lūdzu nospiediet ENTER. '
                                               'Pretējā gadījumā ievadiet \'N\' un tad nospiedet ENTER')

            if event_posted:
                metadata['status'] = 'Submitted'
                events_posted += 1

                print('Pasākums izveidots! Kopējais skaits šajā sesijā: ' + str(events_posted))
            else:
                metadata['status'] = 'Cancelled'
                print('Pasākums atzīmēts kā izlaists!')

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
