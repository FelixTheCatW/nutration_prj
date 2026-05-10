import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import math
from ..core.registries import *

fake = Faker('ru_RU')

# ------------------------ СПРАВОЧНИКИ ------------------------


# Коэффициенты активности для расчета TDEE (Total Daily Energy Expenditure)

# ------------------------ 3. ФУНКЦИИ ДЛЯ РАСЧЕТА НОРМ ------------------------
def calculate_bmr(weight_kg, height_cm, age, gender):
    """Harris-Benedict (пересмотренный) - BMR в ккал/день"""
    if gender == 'male':
        return 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)

def calculate_tdee(bmr, activity_level):
    return bmr * ACTIVITY_FACTORS[activity_level]

def get_target_calories(tdee, goal):
    """Корректировка калорий в зависимости от цели"""
    if goal == 'weight_loss':
        return tdee - 500  # дефицит 500 ккал/день
    elif goal == 'muscle_gain':
        return tdee + 300  # профицит 300 ккал/день
    else:
        return tdee

def get_target_macros(target_cal, goal):
    """
    Расчет целевых БЖУ (г/день) в зависимости от цели и общей калорийности.
    weight_loss: повышенный белок (30% белка, 30% жира, 40% углеводов)
    muscle_gain: высокий белок (35% белка, 25% жира, 40% углеводов)
    maintenance: сбалансированно (25% белка, 30% жира, 45% углеводов)
    """
    if goal == 'weight_loss':
        protein_pct, fat_pct, carb_pct = 0.30, 0.30, 0.40
    elif goal == 'muscle_gain':
        protein_pct, fat_pct, carb_pct = 0.35, 0.25, 0.40
    else:
        protein_pct, fat_pct, carb_pct = 0.25, 0.30, 0.45

    protein_cal = target_cal * protein_pct
    fat_cal = target_cal * fat_pct
    carb_cal = target_cal * carb_pct

    # 1 г белка = 4 ккал, 1 г жира = 9 ккал, 1 г углеводов = 4 ккал
    protein_g = protein_cal / 4
    fat_g = fat_cal / 9
    carbs_g = carb_cal / 4

    return round(protein_g, 1), round(fat_g, 1), round(carbs_g, 1)

def get_meal_planned_calories(target_cal_per_day, meal_type):
    """Распределение дневной нормы по приемам пищи"""
    distribution = {
        'breakfast': 0.25,
        'lunch': 0.35,
        'dinner': 0.30,
        'snack': 0.10
    }
    return round(target_cal_per_day * distribution.get(meal_type, 0.20), 0)

def get_exercise_burned(activity_level, goal):
    """
    Генерация случайных затрат калорий на тренировку (в день приема пищи)
    с учетом уровня активности и цели.
    """
    if activity_level in ['sedentary', 'light']:
        base_burn = random.choice([0, 80, 120])
    elif activity_level == 'moderate':
        base_burn = random.choice([100, 150, 200, 250])
    elif activity_level == 'active':
        base_burn = random.choice([200, 300, 400])
    else:  # very_active
        base_burn = random.choice([400, 500, 600])

    # Для muscle_gain тренировки обычно интенсивнее
    if goal == 'muscle_gain':
        base_burn = int(base_burn * random.uniform(1.1, 1.3))
    elif goal == 'weight_loss':
        base_burn = int(base_burn * random.uniform(0.9, 1.1))

    return base_burn

# ------------------------ 4. ГЕНЕРАЦИЯ ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ ------------------------
class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.gender = random.choice(['male', 'female'])
        self.age = random.randint(18, 65)
        self.height_cm = random.randint(150, 195)
        # Вес зависит от пола
        if self.gender == 'male':
            self.weight_kg = round(random.uniform(60, 120), 1)
        else:
            self.weight_kg = round(random.uniform(50, 100), 1)
        self.goal = random.choice(GOALS)
        self.activity_level = random.choice(ACTIVITY_LEVELS)

        # Расчет BMR и TDEE
        self.bmr = calculate_bmr(self.weight_kg, self.height_cm, self.age, self.gender)
        self.tdee = calculate_tdee(self.bmr, self.activity_level)
        self.target_cal_per_day = get_target_calories(self.tdee, self.goal)
        self.target_protein_g, self.target_fat_g, self.target_carbs_g = get_target_macros(
            self.target_cal_per_day, self.goal
        )

    def update_weight(self, days_passed):
        """
        Упрощенное изменение веса со временем (для реализма).
        При потере веса - уменьшаем, при наборе - увеличиваем.
        """
        if self.goal == 'weight_loss':
            # теряем ~0.5 кг в неделю (но с вариациями)
            change = -0.07 * days_passed + random.uniform(-0.2, 0.2)
        elif self.goal == 'muscle_gain':
            change = 0.05 * days_passed + random.uniform(-0.1, 0.2)
        else:
            change = random.uniform(-0.03, 0.03) * days_passed
        new_weight = self.weight_kg + change
        # Ограничения
        if self.gender == 'male':
            new_weight = max(55, min(130, new_weight))
        else:
            new_weight = max(45, min(110, new_weight))
        self.weight_kg = round(new_weight, 1)
        # Пересчитываем BMR и TDEE
        self.bmr = calculate_bmr(self.weight_kg, self.height_cm, self.age, self.gender)
        self.tdee = calculate_tdee(self.bmr, self.activity_level)
        self.target_cal_per_day = get_target_calories(self.tdee, self.goal)
        self.target_protein_g, self.target_fat_g, self.target_carbs_g = get_target_macros(
            self.target_cal_per_day, self.goal
        )

# ------------------------ 5. ФУНКЦИЯ ГЕНЕРАЦИИ ОДНОЙ ЗАПИСИ ------------------------
def generate_meal_record(meal_id, user, meal_date):
    """
    Генерирует запись для конкретного пользователя на указанную дату.
    """
    country = random.choice(list(COUNTRIES_FOODS.keys()))
    foods = COUNTRIES_FOODS[country]
    product = random.choice(list(foods.keys()))
    calories_per_serving, protein_g, fat_g, carbs_g = foods[product]

    servings = random.randint(1, 3)
    total_calories = servings * calories_per_serving

    city = random.choice(CITIES[country])

    meal_type = random.choice(MEAL_TYPES)
    meal_source = random.choice(MEAL_SOURCES)

    # Рассчитываем плановую калорийность для этого приема
    planned_cal = get_meal_planned_calories(user.target_cal_per_day, meal_type)
    deviation = total_calories - planned_cal

    # День недели и сезон
    day_of_week = meal_date.strftime('%A')  # Monday, Tuesday...
    month = meal_date.month
    if month in [12, 1, 2]:
        season = 'winter'
    elif month in [3, 4, 5]:
        season = 'spring'
    elif month in [6, 7, 8]:
        season = 'summer'
    else:
        season = 'autumn'

    # Флаг праздника (упрощенно: Новый год, 8 марта, майские)
    holiday_flag = 1 if ((meal_date.month == 1 and meal_date.day == 1) or
                         (meal_date.month == 3 and meal_date.day == 8) or
                         (meal_date.month == 5 and meal_date.day in [1, 9])) else 0

    # Время приготовления (зависит от типа блюда и источника)
    if meal_source == 'home_cooked':
        prep_time = random.randint(15, 90)
    elif meal_source == 'instant':
        prep_time = random.randint(2, 10)
    else:
        prep_time = random.randint(5, 30)

    # Рейтинг приема (субъективная оценка)
    meal_rating = round(random.uniform(1, 5), 1)

    return {
        'meal_id': meal_id,
        'user_id': user.user_id,
        'meal_date': meal_date,
        'day_of_week': day_of_week,
        'season': season,
        'holiday_flag': holiday_flag,
        'country': country,
        'city': city,
        'goal': user.goal,
        'meal_type': meal_type,
        'meal_source': meal_source,
        'product': product,
        'servings': servings,
        'calories_per_serving': calories_per_serving,
        'protein_g': protein_g,
        'fat_g': fat_g,
        'carbs_g': carbs_g,
        'total_calories': total_calories,
        'meal_planned_calories': planned_cal,
        'calories_deviation': deviation,
        'meal_prep_time_min': prep_time,
        'meal_rating': meal_rating,
        # Данные пользователя на этот день (могут меняться)
        'user_age': user.age,
        'user_gender': user.gender,
        'user_weight_kg': user.weight_kg,
        'user_height_cm': user.height_cm,
        'user_activity_level': user.activity_level,
        'user_bmr': round(user.bmr, 1),
        'user_tdee': round(user.tdee, 1),
        'user_target_cal_per_day': user.target_cal_per_day,
        'user_target_protein_g': user.target_protein_g,
        'user_target_fat_g': user.target_fat_g,
        'user_target_carbs_g': user.target_carbs_g,
    }

# ------------------------ 6. ОСНОВНАЯ ГЕНЕРАЦИЯ ДАТАСЕТА ------------------------
def generate_dataset(num_users=10, meals_per_user=50):
    """
    Генерирует набор данных для указанного числа пользователей
    и количества приёмов пищи на каждого (случайные даты в 2026).
    """
    users = [User(i+1) for i in range(num_users)]
    all_records = []
    meal_id_counter = 1

    # Для каждого пользователя генерируем дни
    for user in users:
        start_date = datetime(2026, 1, 1)
        end_date = datetime(2026, 12, 31)
        # Случайные даты (не все дни, а только те, когда есть запись о приёме)
        # Для простоты: генерируем meals_per_user случайных дат
        meal_dates = []
        for _ in range(meals_per_user):
            days_offset = random.randint(0, (end_date - start_date).days)
            date = start_date + timedelta(days=days_offset)
            meal_dates.append(date)
        meal_dates.sort()

        # Сортируем даты и имитируем изменение веса со временем
        prev_date = None
        days_passed = 0
        for idx, date in enumerate(meal_dates):
            if prev_date is None:
                days_passed = 0
            else:
                days_passed = (date - prev_date).days
                if days_passed > 0:
                    user.update_weight(days_passed)
            prev_date = date

            # Генерируем запись приема пищи (можно несколько в день, но для простоты - один)
            record = generate_meal_record(meal_id_counter, user, date)
            all_records.append(record)
            meal_id_counter += 1

    df = pd.DataFrame(all_records)

    # Добавляем вычисляемые кумулятивные столбцы (по user_id и дате)
    # Для этого надо агрегировать калории за день - это лучше сделать отдельно,
    # но для демонстрации добавим простые: дневной остаток и флаг выполнения плана.
    # (Полноценное окно потребовало бы группировки, но для CSV оставим как есть)

    # Добавим столбец compliance (выполнение плана по калориям в пределах ±10%)
    df['meal_compliance_flag'] = (abs(df['calories_deviation']) <= 0.1 * df['meal_planned_calories']).astype(int)

    # Дневной накопленный intake и остаток лучше считать отдельным скриптом,
    # но для примера добавим столбец net_calories (с учетом тренировок) - сгенерируем случайно
    # В реальности exercise_calories_burned нужно привязывать к дате, а не к приему.
    # Упростим: добавим случайные затраты на тренировку, зависящие от активности.
    df['exercise_calories_burned'] = df.apply(
        lambda row: get_exercise_burned(row['user_activity_level'], row['goal']), axis=1
    )
    df['net_calories'] = df['total_calories'] - df['exercise_calories_burned']

    # Вернем df
    return df

# Генерация датасета: 10 пользователей × по 50 приёмов = 500 записей
df_final = generate_dataset(num_users=10, meals_per_user=50)

# Сохраняем в CSV
df_final.to_csv('meal_log_advanced.csv', index=False, encoding='utf-8-sig')

# Выводим информацию о датасете
print(f"Сгенерировано записей: {len(df_final)}")
print("\nПервые 5 строк:")
print(df_final.head())
print("\nДоступные столбцы:")
print(list(df_final.columns))