import random

from src.core.registries import *
from src.core.urser import random_person


def generate_data():
    for index, loca, country in enumerate(LOCALE_TO_COUNTRY.items()):
        user = random_person(index, loca)
        print(user)


def generate_meal(locale: str) -> dict:
    if random.random() > 0.8:
        product, val = random.choice(list(COUNTRIES_FOODS[locale].items()))
    else:
        product, val = random.choice(list(FOODS.items()))

    return {
        "product": product,
        "calories_per_serving": val[0],
        "protein_g": val[1],
        "fat_g": val[2],
        "carbs_g": val[3]
    }