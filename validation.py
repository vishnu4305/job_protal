# Validates user input before database operations
# Checks whether an email has a basic valid format
def is_valid_email(email):
    email = email.strip()
    return "@" in email and "." in email.split("@")[-1]


# Checks whether the value contains only digits
def is_valid_number(value):
    value = value.strip()
    return value.isdigit()


# Checks whether the phone number contains exactly 10 digits
def is_valid_phone(phone):
    phone = phone.strip()
    return phone.isdigit() and len(phone) == 10


# Checks whether the password has at least 8 characters, one letter, and one number
def is_valid_password(password):
    password = password.strip()

    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True


# Checks whether the value matches one of the allowed choices
def is_valid_choice(value, valid_options):
    value = value.strip()
    return value in valid_options


# Gets input from the user and ensures it is not empty
def get_non_empty_input(prompt):
    value = input(prompt).strip()
    while value == "":
        print("This field cannot be empty.")
        value = input(prompt).strip()
    return value


# Gets and validates an email address from the user
def get_valid_email(prompt):
    while True:

        email = get_non_empty_input(prompt)
        if is_valid_email(email):
            return email
        print(
            "Invalid email format. "
            "Example: name@example.com"
        )


# Gets and validates a 10-digit phone number from the user
def get_valid_phone(prompt):
    while True:
        phone = get_non_empty_input(prompt)
        if is_valid_phone(phone):
            return phone
        print("Phone number must be exactly 10 digits.")


# Gets and validates a whole number from the user
def get_valid_number(prompt):
    while True:
        value = get_non_empty_input(prompt)
        if is_valid_number(value):
            return value
        print("This field must be a whole number.")


# Gets and validates a value against a list of allowed choices
def get_valid_choice(prompt, valid_options):
    while True:
        value = get_non_empty_input(prompt)
        if is_valid_choice(value, valid_options):
            return value
        print(
            f"Invalid choice. "
            f"Options: {', '.join(valid_options)}"
        )


# Gets and validates a password from the user
def get_valid_password(prompt):
    while True:
        password = get_non_empty_input(prompt)
        if is_valid_password(password):
            return password
        print(
            "\nInvalid password!"
            "\nPassword must contain:"
            "\n- At least 8 characters"
            "\n- At least one letter"
            "\n- At least one number"
        )
