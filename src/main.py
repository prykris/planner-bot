import sys

from driver_setup import initialize_driver
from facebook.facebook_builder import build_facebook_controls
from session import Session
from metadata_provider import LocalMetadataProvider
from event_data_providers import LocalEventDataProvider
from prompts import confirm

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

    driver = initialize_driver()
    facebook = build_facebook_controls(driver)

    if not facebook.login():
        print('Login failed.')
        sys.exit(1)
    else:
        confirm('Pārslēdzieties uz darba lapu un nospiediet Enter, lai turpinātu!')

    for event, metadata in session.pending_events():
        try:
            facebook.create_event(event, metadata)

            posted = confirm('Pasākums publicēts?')

            if posted:
                metadata['status'] = 'Submitted'
            else:
                metadata['status'] = 'Cancelled'

        except Exception as e:
            print(e)
        finally:
            print('Metadata saved!')
            session.metadata_provider.save(event, metadata)
