import random
from dataclasses import dataclass, field

from faker import Faker
from pandas.core import nanops

from src.core.registries import GOALS, ACTIVITY_LEVELS, ACTIVITY_FACTORS


@dataclass
class Person:
    user_id: int
    name: str
    activity_level: str
    height_cm: int
    age: int
    gender: str
    weight_kg: float
    goal: str
    city: str
    loca: str

    bmr: float = field(init=False, default=0.0)
    target_cal_per_day: float = field(init=False, default=0.0)
    target_protein_g: float = field(init=False, default=0.0)
    tdee: float = field(init=False, default=0.0)

    def __init__(self, user_id, name: str, gender: str, age, height_cm, weight_kg, goal, activity_level, loca, city):
        self.user_id = user_id
        self.name = name
        self.gender = gender
        self.age = age
        self.height_cm = height_cm
        self.weight_kg = weight_kg
        self.goal = goal
        self.activity_level = activity_level
        self.loca = loca
        self.city = city


def random_person(user_id: int, locale: str) -> Person:
    fake = Faker(locale)
    gender = random.choice(['мужской', 'женский'])
    if gender == 'мужской':
        weight = round(random.uniform(60, 120), 1)
        name = fake.name_male()
    else:
        weight = round(random.uniform(50, 100), 1)
        name = fake.name_female()
    person = Person(user_id=user_id,
                    name=name,
                    age=random.randint(18, 70),
                    gender=gender,
                    height_cm=random.randint(150, 195),
                    weight_kg=weight,
                    goal=random.choice(list(GOALS.values())),
                    activity_level=random.choice(list(ACTIVITY_LEVELS.values())),
                    loca=locale,
                    city=fake.city()
                    )
    person.bmr = calculate_bmr(person.weight_kg, person.height_cm, person.age, person.gender)
    person.tdee = calculate_tdee(person.bmr, person.activity_level)
    person.target_cal_per_day = get_target_calories(person.tdee, person.goal)

    return person


def calculate_bmr(weight_kg, height_cm, age, gender):
    """Harris-Benedict (пересмотренный)"""
    if gender == 'мужской':
        return 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)


def calculate_tdee(bmr, activity_level):
    return bmr * ACTIVITY_FACTORS[activity_level]


def get_target_calories(tdee, goal):
    if goal == 'похудение':
        return tdee - 500
    elif goal == 'набор_мышц':
        return tdee + 300
    else:  # поддержание
        return tdee


def get_target_macros(target_cal, goal):
    if goal == 'похудение':
        protein_pct, fat_pct, carb_pct = 0.30, 0.30, 0.40
    elif goal == 'набор_мышц':
        protein_pct, fat_pct, carb_pct = 0.35, 0.25, 0.40
    else:
        protein_pct, fat_pct, carb_pct = 0.25, 0.30, 0.45

    protein_cal = target_cal * protein_pct
    fat_cal = target_cal * fat_pct
    carb_cal = target_cal * carb_pct

    return round(protein_cal / 4, 1), round(fat_cal / 9, 1), round(carb_cal / 4, 1)


def get_meal_planned_calories(target_cal_per_day, meal_type):
    distribution = {'завтрак': 0.25, 'обед': 0.35, 'ужин': 0.30, 'перекус': 0.10}
    return round(target_cal_per_day * distribution[meal_type], 0)


def get_exercise_burned(activity_level):
    levels = {'сидячий': [0, 50, 80], 'лёгкий': [50, 100, 150], 'умеренный': [100, 150, 200, 250],
              'активный': [200, 300, 400], 'очень активный': [400, 500, 600]}
    return random.choice(levels.get(activity_level, [0, 100]))
