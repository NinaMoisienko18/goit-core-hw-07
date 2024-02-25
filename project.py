from collections import UserDict
import re
from datetime import datetime, timedelta


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            error_messages = {
                KeyError: "Contact not found.",
                ValueError: "Invalid input.",
                IndexError: "Invalid input. Please provide the name."
            }
            return error_messages.get(type(e), "An error occurred.")

    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        number_pattern = r"\b\d{10}\b"  # You might want to improve this pattern
        if re.match(number_pattern, value):
            super().__init__(value)
        else:
            count_figures = len(value)
            print(f"Number - {value} - incorrect, it has {count_figures} figures")


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        try:
            date_pattern = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')
            if date_pattern.match(value):
                self.value = datetime.strptime(value, "%d.%m.%Y").date()

        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class BirthdayBook(UserDict):
    def __init__(self):
        super().__init__()

    def add_birthday(self, name, birthday):
        self.data[name] = birthday
        return f"Birthday was successfully added for '{name}'"

    def find_birthday(self, name):
        return self.data.get(name, None)

    def remove_birthday(self, name):
        if name in self.data:
            self.data.pop(name)
        else:
            return f"Birthday for {name} not found in Birthday book."

    def show_all_birthdays(self):
        if not self.data:
            return "There are no birthdays in the Birthday book."

        result = "\n>>> All Birthdays:\n"
        for name, birthday in self.data.items():
            result += f"'name': {name}, 'birthday': {birthday}\n"

        return result

    def get_upcoming_birthdays(self):
        dict_with_dates_for_ones = {}
        current_day = datetime.now().date()
        current_week_start = current_day - timedelta(days=current_day.weekday())  # Start of the current week

        for name, birthday in self.data.items():
            birthday_day = birthday.value

            formatted_date_birthday = datetime(current_day.year, birthday_day.month, birthday_day.day).date()

            difference = formatted_date_birthday - current_day

            if 0 <= difference.days < 7 and formatted_date_birthday.weekday() in [0, 1, 2, 3, 4]:
                dict_with_dates_for_ones[name] = formatted_date_birthday.strftime("%Y.%m.%d")
            elif difference.days < 0 and formatted_date_birthday.weekday() not in [5, 6]:
                continue
            else:  # If it falls on Saturday or Sunday
                days_until_monday = 7 - formatted_date_birthday.weekday()
                formatted_date_birthday += timedelta(days=days_until_monday)
                dict_with_dates_for_ones[name] = formatted_date_birthday.strftime("%Y.%m.%d")

        return dict_with_dates_for_ones


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    @input_error
    def add_phone(self, phone):
        try:
            phone_instance = Phone(phone)
            if len(self.phones) == 0 or phone_instance not in self.phones:
                self.phones.append(phone_instance)
                return f"Contact '{self.name}' added."
        except ValueError as e:
            return str(e)

    @input_error
    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    @input_error
    def edit_phone(self, phone_old, phone_new):
        old_number = Phone(phone_old)
        new_number = Phone(phone_new)
        if old_number.value in [phone.value for phone in self.phones] and new_number not in self.phones:
            idx = [phone.value for phone in self.phones].index(old_number.value)
            self.phones[idx] = new_number
            return f"Contact '{self.name}' changed."
        else:
            return f"Such number {phone_old} isn't in Address book"

    @input_error
    def show_all(self, contacts):
        if not contacts:
            return "There are no contacts."

        result = "\n>>> All Contacts:\n"
        for name, number in contacts.items():
            result += f"{name}: {number}\n"

        return result

    @input_error
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(map(str, self.phones))}"


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        if name in self.data:
            return self.data[name]
        else:
            return f"Record for {name} not found in Address book."

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)
        else:
            return f"Record for {name} not found in Address book."

    def get_upcoming_birthdays(self, birthday_book):
        return birthday_book.get_upcoming_birthdays()


def main():
    record_instance = None
    birthday_book = BirthdayBook()
    address_book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Goodbye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            record_instance = Record(args[0])
            result = record_instance.add_phone(args[1])
            if result.startswith("Contact"):
                address_book.add_record(record_instance)
            print(result)
        elif command == "change":
            record_instance = address_book.find(args[0])
            print(record_instance.edit_phone(args[1], args[2]))
        elif command == "phone":
            print(address_book.find(args[0]))
        elif command == "all":
            if record_instance:
                print(record_instance.show_all(address_book.data))
                print(">>> List of upcoming birthdays this week:")
                upcoming_birthdays = address_book.get_upcoming_birthdays(birthday_book)
                for name, congrat in upcoming_birthdays.items():
                    print(f"* {name}, {congrat}")
            else:
                print("No record to show. Use 'add' command first.")
        elif command == "add-birthday":
            try:
                record_name, birthday = args
            except ValueError:
                print("Invalid input for 'add-birthday' command. Please provide both the name and birthday.")
                continue  # Restart the loop to get another user input
            record = address_book.find(record_name)
            if record is None:
                print(f"Contact '{record_name}' not found.")
            else:
                birthday_book.add_birthday(record_name, Birthday(birthday))
                print(f"Birthday for '{record_name}' added.")
        elif command == "show-birthday":
            record_name = args[0]
            record = address_book.find(record_name)
            if record is None:
                print(f"Contact '{record_name}' not found.")
            elif isinstance(record, str):
                print(f"Invalid contact name: '{record_name}'.")
            else:
                birthday = birthday_book.find_birthday(record_name)
                if birthday is None:
                    print(f"No birthday found for '{record_name}'.")
                else:
                    print(f"Birthday day for '{record_name}' ---> {birthday}")
        elif command == "birthdays":
            print(birthday_book.show_all_birthdays())
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()