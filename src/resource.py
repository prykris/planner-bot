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