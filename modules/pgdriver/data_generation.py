import copy
import random
from mimesis import Person
from mimesis import Locale
from mimesis.enums import Gender

def personal_data_generator(count: int = 5):
    person = Person(locale=Locale.RU)

    person_list = []

    for i in range(count):
        gender = random.choice(list(Gender))
        person_data = {
            "last_name": person.last_name(gender=gender),
            "first_name": person.first_name(gender=gender),
            "middle_name": person.patronymic(gender=gender)
        }
        person_list.append(person_data)

    return person_list
