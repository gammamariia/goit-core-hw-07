from collections import UserDict
from datetime import date, datetime, timedelta

commands = """
1)help - Show commands
2)hello - How can I help you?
3)add [ім'я] [номер телефону]-  Add a new contact
4)change [ім'я] [новий номер телефону] - Change phone number
5)phone [ім'я] - Show phone number
6)all - Show all conttacts
7)close or exit - Exit the application
8)add-birthday [ім'я] [дата народження] - Add birthday date for a contact in the format DD-MM-YYYY
9)show-birthday [ім'я]: Show birthday
10)birthdays: Show upcoming birthdays within the next 7 days
"""


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, phone_number):
        phone_number = phone_number.strip()
        if phone_number.startswith("380"):
            if len(phone_number) != 10 and not phone_number.isdigit():
                raise ValueError(
                    "Phone number must be 10 digits long and contain only numbers."
                )
            value = phone_number
        elif len(phone_number) == 10 and phone_number.isdigit():
            value = phone_number
        else:
            raise ValueError(
                "Phone number must be 10 digits long and contain only numbers."
            )
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            date_value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(date_value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def find_phone(self, phone):
        phone = Phone(phone).value if not isinstance(phone, Phone) else phone.value
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if not phone_to_edit:
            raise ValueError(f"Phone number {old_phone} not found")
        new_phone = Phone(new_phone)
        phone_to_edit.value = new_phone.value

    def remove_phone(self, phone: str):
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)
        result = f"Contact name: {self.name.value}, phones: {phones_str}"
        if self.birthday:
            result += f", birthday: {self.birthday.value.strftime('%d-%m-%Y')}"
        return result


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, days=7, filter_weekend=True):
        upcoming_birthdays = []
        today = date.today()
        for user in self.data.values():
            if not user.birthday:
                continue
            birthday_this_year = user.birthday.value.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if 0 <= (birthday_this_year - today).days <= days:
                congratulation_date = self.adjust_for_weekend(birthday_this_year)
                birthday = Birthday(congratulation_date)
                upcoming_birthdays.append(
                    {"name": user.name.value, "congratulation_date": birthday}
                )
            return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    cmd = parts[0].lower()
    args = parts[1:]
    return cmd, args


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return e
        except IndexError:
            return "Enter user name."
        except KeyError:
            return "Contact not found."
        except AttributeError:
            return "Contact not found."
        except Exception as e:
            return f"An error occurred: {e}"

    return inner


@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book):
    name = args[0]
    return f"{name}'s phone number: {book[name]}"


@input_error
def show_all(book):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.values())


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record.birthday is None:
        return f"{name} has no birthday set."
    return f"{name}'s birthday is {record.birthday.value.strftime('%d-%m-%Y')}"


@input_error
def birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    result = []
    for item in upcoming:
        result.append(f"{item['name']}: {item['birthday']}")
    return "\n".join(result)


def main():
    print("Start")
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if not command:
            continue
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "help":
            print(commands)
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
