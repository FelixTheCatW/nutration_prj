import faker

def generate_data():
    pass


# fake = faker("ru_RU")
def generate_meal(locale: str):
    pass
def generate_person(locale: str):
    fake = faker.Faker(locale)
    return {
        "name": fake.name(),
        "city": fake.city(),
    }