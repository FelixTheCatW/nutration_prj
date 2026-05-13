import random

from src.core.registries import *
from src.core.Person import random_person


def generate_data():
    persons = [random_person(index, loca) for index, loca in enumerate(LOCALE_MAP.values())]
    for person in persons:
        meals = [generate_meal_2(person.loca, meal_t, person.tdee, person.goal) for meal_t in MEAL_TYPES]
        yield person, meals


def generate_meal(locale: str) -> dict:
    if random.random() > 0.8:
        locale_country = LOCALE_TO_COUNTRY[locale]
        product, val = random.choice(list(COUNTRIES_FOODS[locale_country].items()))
    else:
        product, val = random.choice(list(FOODS.items()))

    return {
        "product": product,
        "servings": random.randint(1, 3),
        "calories": val[0],
        "protein_g": val[1],
        "fat_g": val[2],
        "carbs_g": val[3]
    }


def generate_meal_2(locale: str, meal_t: str, target_calories: float, user_goal: str) -> dict:
    # выбор национальной или глобальной кухни
    is_local = random.random() < 0.75

    if is_local:
        country_name = LOCALE_TO_COUNTRY[locale]
        meals_list = COUNTRIES_MEALS_BY_TYPE[country_name][meal_t]

        if len(meals_list) < 3:
            meals_list += GLOBAL_MEALS_BY_TYPE[meal_t]

    else:
        meals_list = GLOBAL_MEALS_BY_TYPE[meal_t]

    # выберите 1-3 блюда с весами
    chosen_dishes = []
    remaining_kcal = target_calories
    while remaining_kcal > 50 and len(chosen_dishes) < 4:
        dish = random.choices(meals_list, weights=[w[0] for _, w in meals_list], k=1)[0]
        name, (kcal, prot, fat, carbs) = dish
        servings = get_servings(kcal, user_goal)
        kcal_total = kcal * servings
        if kcal_total <= remaining_kcal * 1.3:  # допустимый перебор
            chosen_dishes.append({
                "product": name,
                "servings": servings,
                "calories": round(kcal * servings, 1),
                "protein_g": round(prot * servings, 1),
                "fat_g": round(fat * servings, 1),
                "carbs_g": round(carbs * servings, 1)
            })
            remaining_kcal -= kcal_total
        else:
            break
    return {"meals": chosen_dishes, "meal_type": meal_t, "eaten_at": generate_time(meal_t)}


def generate_time(meal_t: str) -> str:
    match meal_t:
        case "завтрак":
            hour = random.randint(7, 10)
            minute = random.choice([0, 15, 30, 45])
        case "обед":
            hour = random.randint(12, 15)
            minute = random.choice([0, 15, 30, 45])
        case "ужин":
            hour = random.randint(18, 21)
            minute = random.choice([0, 15, 30, 45])
        case "перекус":
            # перекусы могут быть в разное время
            hour = random.choice([10, 11, 16, 17])
            minute = random.choice([0, 15, 30, 45])
        case _:
            hour = 12
            minute = 0
    return f"{hour:02d}:{minute:02d}"


def get_servings(calories_per_serving, goal):
    base = 1
    if goal == 'weight_loss':
        base = random.choice([0.5, 0.8, 1.0])
    elif goal == 'muscle_gain':
        base = random.choice([1.0, 1.2, 1.5])
    # округлите до 0.5
    max_servings = 2 if calories_per_serving > 300 else 3
    servings = min(max_servings, base + random.uniform(-0.2, 0.3))
    return round(servings * 2) / 2  # кратно 0.5
