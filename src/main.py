from driver_setup import initialize_driver
from facebook_builder import build_facebook_controls
from prompts import confirm
from session import Session
from metadata_provider import LocalMetadataProvider
from event_data_providers import LocalEventDataProvider

events_posted = 0

if __name__ == "__main__":
    print('Starting Event Planner Bot v0.1.0!')

    session = Session(
        LocalEventDataProvider('../events/filtered_events.json'),
        LocalMetadataProvider('../sessions/filtered_events')
    )

    print('Total events: ', len(session.all_events()))
    print('Pending events: ', len(session.pending_events()))
    print('Accepted events: ', len(session.accepted_events()))
    print('Cancelled events: ', len(session.cancelled_events()))

    for event, metadata in session:
        print(event, metadata)
        exit()

    driver = initialize_driver()
    facebook = build_facebook_controls(driver)

    try:
        print(f'Ienākam Facebook ar e-pastu {facebook.credentials[0]}...')

        # Login to Twitter
        if not facebook.login():
            raise Exception('Ielogošanās neizdevās! Pārbaudiet savus akreditācijas datus.')

        if not confirm('Ielogošanās veiksmīga! Manuāli pārslēdzieties uz darba lapu, ja nepieciešams.'):
            exit()

        for event, metadata, metadata_file in events('../events/filtered_events.json', 50000, 0.5):
            # Skip events that have already been completed or failed
            if not metadata['status'] == 'Pending':
                # print( f'Skipping city {event["city_ascii"]}, {event["admin_name"]} (ID: {event["id"]}) (Status: {
                # metadata["status"]})')
                continue
            if confirm('Lai atvērtu pasākumu izveides lapu nospiediet pogu Enter'):
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

            event_posted = confirm('Lai saglabātu šo pasākumu kā izveidotu, lūdzu nospiediet ENTER. '
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
