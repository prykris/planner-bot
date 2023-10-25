from prompts import select_language
from facebook.facebook_controls import FacebookControls
from storage import load_credentials, save_credentials


def build_facebook_controls(driver) -> FacebookControls:
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

    return FacebookControls(driver=driver, credentials=[email, password], language=language)
