def generate_passwords(company_name, current_year, special_chars_required, uppercase_required):
    # Capitalize the company name if uppercase is required
    if uppercase_required:
        company_name = company_name.capitalize()

    # Define the base password variations
    base_variations = [
        "{name}1",
        "{name}2",
        "{name}3",
        "{name}4",
        "{name}5",
        "{name}6",
        "{name}7",
        "{name}8",
        "{name}9",
        "{name}01",
        "{name}02",
        "{name}03",
        "{name}04",
        "{name}05",
        "{name}06",
        "{name}07",
        "{name}08",
        "{name}09",
        "{name}{year}",
        "{name}123",
        "{name}1234"
    ]

    # Define the special characters variations
    special_chars_variations = ["!", "@", "#", "$", "%", "&", "*", "(", ")", "-"]

    # Initialize the list of generated passwords
    passwords = []

    # Iterate through the base variations
    for base_variation in base_variations:
        # Format the password with the company name and current year
        password = base_variation.format(name=company_name, year=current_year)

        # If special characters are required, append each special character
        if special_chars_required:
            for special_char in special_chars_variations:
                passwords.append(password + special_char)
        # If special characters are not required, add the password to the list
        else:
            passwords.append(password)

    return passwords

# Print the banner
print("================================")
print("    PASSWORD GENERATOR")
print("================================")

# Ask for user input
company_name = input("Enter the company name: ")
current_year = input("Enter the current year: ")
special_chars = input("Do the passwords require special characters? (yes/no): ")
uppercase = input("Do the passwords require uppercase? (yes/no): ")

# Convert user input to boolean values
special_chars_required = special_chars.lower() == "yes"
uppercase_required = uppercase.lower() == "yes"

# Generate the passwords
passwords = generate_passwords(company_name, current_year, special_chars_required, uppercase_required)

# Print the generated passwords
print("\nGenerated Passwords:")
for index, password in enumerate(passwords, 1):
    print(f"{index}. {password}")
