from enum import Enum


class Language(Enum):
    Latvian = 1
    English = 2

    def __str__(self):
        return 'Latviešu' if self.value == 1 else 'Angļu'


def select_language():
    while True:
        print("Izvēlieties valodu kura ir Jums iestatīta Facebook profilā:")
        for lang in Language:
            print(f"    {lang.value}. {lang.name}")

        try:
            choice = int(input("Jūsu izvēle: "))
            if 1 <= choice <= 2:
                return Language(choice)
            else:
                print(f"Kļūdaina izvēle. Valoda '{choice}' nepastāv")
        except ValueError:
            print("Kļūdaina izvēle. Lūdzu ievadiet tikai ciparu.")


def prompt_confirmation(prompt, default="Y"):
    while True:
        user_input = input(prompt + f" [{default}]: ").strip().upper()

        if user_input == "":
            user_input = default

        if user_input == "Y":
            return True
        elif user_input == "N":
            return False
        else:
            print("Please enter 'Y' for Yes or 'N' for No.")
