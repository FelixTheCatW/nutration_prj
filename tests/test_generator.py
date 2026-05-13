from datetime import date, timedelta
from pprint import pprint

from src.cli.data_generator import generate_data, generate_persons, generate_day_nutrition
from src.core.Person import Person
from src.core.registries import COUNTRIES_MEALS_BY_TYPE, GLOBAL_MEALS_BY_TYPE, LOCALES

import csv
from datetime import date, timedelta


class TestGenerator:

    def test_registry(self):
        print("COUNTRIES_MEALS_BY_TYPE")
        pprint(COUNTRIES_MEALS_BY_TYPE, width=40, sort_dicts=False)
        print("*" * 40)
        print("GLOBAL_MEALS_BY_TYPE")
        pprint(GLOBAL_MEALS_BY_TYPE, width=40, sort_dicts=False)
        pass

    def test_generate_persons(self):
        persons = generate_persons(20)
        pprint(persons, width=100)

    def test_generate_day(self):
        persons = generate_persons(len(LOCALES))
        start = date(2025, 1, 1)
        end = date(2025, 12, 31)

        d = start
        while d <= end:
            for person in persons:
                data = generate_day_nutrition(person)
                for meal in data:
                    print(person.name, meal["meal_type"], ", ".join([x["product"] for x in meal["meals"]]))
                print("_" * 80)
            d += timedelta(days=1)

    def test_generate_year_to_csv(self):
        persons = generate_persons(len(LOCALES))
        start = date(2025, 1, 1)
        end = date(2025, 12, 31)
        save_detailed_nutrition_to_csv(persons, start, end, r"data\nutrition_data.csv")

def save_detailed_nutrition_to_csv(persons: list[Person], start_date: date, end_date: date, filename: str):
    """
    Сохраняет в CSV каждое блюдо для каждого человека за каждый день.
    Включает все поля и свойства Person, а также детали блюда: servings, калории, БЖУ.
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Заголовки: все поля Person (включая вычисляемые) + поля приёма пищи + поля блюда
        headers = [
            'date',
            'user_id', 'name', 'activity_level', 'height_cm', 'age', 'gender',
            'weight_kg', 'goal', 'city', 'loca',
            'bmr', 'target_cal_per_day', 'target_protein_g', 'tdee',
            'meal_type', 'eaten_at',
            'dish_name', 'servings', 'dish_calories', 'dish_protein_g', 'dish_fat_g', 'dish_carbs_g'
        ]
        writer.writerow(headers)

        current_date = start_date
        while current_date <= end_date:
            for person in persons:
                day_meals = generate_day_nutrition(person)  # список словарей приёмов пищи
                for meal_data in day_meals:
                    meal_type = meal_data['meal_type']
                    eaten_at = meal_data['eaten_at']
                    dishes = meal_data['meals']  # список блюд (каждое – словарь)

                    for dish in dishes:
                        row = [
                            current_date.isoformat(),
                            person.user_id, person.name, person.activity_level, person.height_cm,
                            person.age, person.gender, person.weight_kg, person.goal, person.city, person.loca,
                            person.bmr, person.target_cal_per_day, person.target_protein_g, person.tdee,
                            meal_type, eaten_at,
                            dish['product'], dish['servings'],
                            dish['calories'], dish['protein_g'], dish['fat_g'], dish['carbs_g']
                        ]
                        writer.writerow(row)
            current_date += timedelta(days=1)

    print(f"Детальные данные сохранены в {filename}")
