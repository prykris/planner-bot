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
