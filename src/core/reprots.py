import pandas as pd
import numpy as np

import pandas as pd
from core.Person import Person
from core.Person import calculate_bmr, calculate_tdee, get_target_calories


def load_data(filepath: str) -> tuple[list[Person], pd.DataFrame]:
    """
    Загружает данные из CSV.

    Returns:
        persons: список объектов Person (по одному на каждого пользователя)
        df_meals: DataFrame со всеми записями о приёмах пищи
    """
    df = pd.read_csv(filepath)

    # Преобразование дат и времени
    df["date"] = pd.to_datetime(df["date"])
    df["date_only"] = df["date"].dt.date
    df["hour"] = pd.to_datetime(df["eaten_at"], format="%H:%M").dt.hour

    # Уникальные пользователи (берём первую встреченную строку для каждого user_id)
    users_df = df.groupby("user_id").first().reset_index()

    persons = []
    for _, row in users_df.iterrows():
        # Создаём объект Person без вычисленных полей
        p = Person(
            user_id=int(row["user_id"]),
            name=row["name"],
            gender=row["gender"],
            age=int(row["age"]),
            height_cm=int(row["height_cm"]),
            weight_kg=float(row["weight_kg"]),
            goal=row["goal"],
            activity_level=row["activity_level"],
            loca=row["loca"],
            city=row["city"],
        )
        # Рассчитываем метрики (можно взять из CSV, но пересчёт надёжнее)
        p.bmr = calculate_bmr(p.weight_kg, p.height_cm, p.age, p.gender)
        p.tdee = calculate_tdee(p.bmr, p.activity_level)
        p.target_cal_per_day = get_target_calories(p.tdee, p.goal)
        # target_protein_g можно добавить при необходимости
        persons.append(p)

    return persons, df


def get_user_list(df):
    """Возвращает список уникальных user_id и соответствующих имен"""
    users = df[["user_id", "name"]].drop_duplicates().sort_values("user_id")
    return users

def personal_statistics(df, user_id):
    user_df = df[df["user_id"] == user_id].copy()
    if user_df.empty:
        print(f"Пользователь с ID {user_id} не найден.")
        return

    # Данные пользователя (постоянные)
    user_info = user_df.iloc[0]
    name = user_info["name"]
    target_cal = user_info["target_cal_per_day"]

    # Группировка по дням
    daily = (
        user_df.groupby("date_only")
        .agg(
            total_cal=("dish_calories", "sum"),
            total_protein=("dish_protein_g", "sum"),
            total_fat=("dish_fat_g", "sum"),
            total_carbs=("dish_carbs_g", "sum"),
        )
        .reset_index()
    )

    # Итоги за период
    total_days = len(daily)
    avg_cal = daily["total_cal"].mean()
    avg_protein = daily["total_protein"].mean()
    avg_fat = daily["total_fat"].mean()
    avg_carbs = daily["total_carbs"].mean()

    # Отклонение от цели
    deviation = avg_cal - target_cal
    percent_of_target = (avg_cal / target_cal) * 100

    print(f"\n=== Персональная статистика для {name} (ID {user_id}) ===")
    print(f"Период: {daily['date_only'].min()} – {daily['date_only'].max()}")
    print(f"Всего дней с записями: {total_days}")
    print(f"\nСреднее в день:")
    print(
        f"  Калории: {avg_cal:.0f} ккал (цель {target_cal:.0f} ккал, {percent_of_target:.1f}% от цели)"
    )
    print(f"  Белки: {avg_protein:.1f} г")
    print(f"  Жиры: {avg_fat:.1f} г")
    print(f"  Углеводы: {avg_carbs:.1f} г")
    print(f"\nОтклонение от цели: {deviation:+.0f} ккал в день")

    # Динамика по дням (таблица первых/последних дней)
    print("\nДинамика по дням (первые 7 дней):")
    print(daily.head(7).to_string(index=False))

def macro_analysis(df, user_id):
    user_df = df[df["user_id"] == user_id]
    if user_df.empty:
        print(f"Пользователь с ID {user_id} не найден.")
        return

    # Суммируем по дням
    daily = (
        user_df.groupby("date_only")
        .agg(
            cal=("dish_calories", "sum"),
            protein=("dish_protein_g", "sum"),
            fat=("dish_fat_g", "sum"),
            carbs=("dish_carbs_g", "sum"),
        )
        .reset_index()
    )

    # Средние значения
    avg_cal = daily["cal"].mean()
    avg_protein = daily["protein"].mean()
    avg_fat = daily["fat"].mean()
    avg_carbs = daily["carbs"].mean()

    # Процент калорий из БЖУ (1г белка = 4 ккал, жира = 9, углеводов = 4)
    cal_from_protein = avg_protein * 4
    cal_from_fat = avg_fat * 9
    cal_from_carbs = avg_carbs * 4
    total_calc = cal_from_protein + cal_from_fat + cal_from_carbs

    if total_calc > 0:
        pct_protein = cal_from_protein / total_calc * 100
        pct_fat = cal_from_fat / total_calc * 100
        pct_carbs = cal_from_carbs / total_calc * 100
    else:
        pct_protein = pct_fat = pct_carbs = 0

    name = user_df.iloc[0]["name"]
    print(f"\n=== Анализ макронутриентов для {name} ===")
    print(f"Среднее потребление в день:")
    print(f"  Белки: {avg_protein:.1f} г → {cal_from_protein:.0f} ккал ({pct_protein:.1f}%)")
    print(f"  Жиры:  {avg_fat:.1f} г → {cal_from_fat:.0f} ккал ({pct_fat:.1f}%)")
    print(f"  Углеводы: {avg_carbs:.1f} г → {cal_from_carbs:.0f} ккал ({pct_carbs:.1f}%)")
    print(
        f"  Итого (расчёт): {total_calc:.0f} ккал, средние калории из таблицы: {avg_cal:.0f} ккал"
    )

    # Рекомендуемые нормы (пример: 30% белка, 20% жира, 50% углеводов)
    print("\nСравнение с рекомендуемым соотношением (30/20/50):")
    print(f"  Белки: {pct_protein:.1f}% vs 30%")
    print(f"  Жиры:  {pct_fat:.1f}% vs 20%")
    print(f"  Углеводы: {pct_carbs:.1f}% vs 50%")
    
def top_frequent_dishes(df, user_id, top_n=10):
    user_df = df[df["user_id"] == user_id]
    if user_df.empty:
        print(f"Пользователь с ID {user_id} не найден.")
        return

    freq = user_df.groupby("dish_name").size().sort_values(ascending=False).head(top_n)
    name = user_df.iloc[0]["name"]
    print(f"\n=== Топ-{top_n} самых частых блюд для {name} ===")
    for i, (dish, count) in enumerate(freq.items(), 1):
        print(f"{i:2}. {dish:30} – {count} раз(а)")

def top_caloric_dishes(df, user_id, top_n=10):
    user_df = df[df["user_id"] == user_id]
    if user_df.empty:
        print(f"Пользователь с ID {user_id} не найден.")
        return

    # Средняя калорийность на один приём (с учётом servings)
    # В данных dish_calories уже на одну порцию, servings – множитель
    user_df["total_dish_cal"] = user_df["dish_calories"] * user_df["servings"]
    cal_mean = (
        user_df.groupby("dish_name")["total_dish_cal"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
    )

    name = user_df.iloc[0]["name"]
    print(f"\n=== Топ-{top_n} самых калорийных блюд (средняя калорийность за приём) для {name} ===")
    for i, (dish, cal) in enumerate(cal_mean.items(), 1):
        print(f"{i:2}. {dish:30} – {cal:.0f} ккал в среднем за приём")

def compare_users(df):
    # Агрегируем по каждому пользователю
    users = (
        df.groupby(["user_id", "name", "target_cal_per_day", "activity_level", "gender"])
        .agg(avg_cal=("dish_calories", "mean"), total_days=("date", lambda x: x.nunique()))
        .reset_index()
    )

    # Рассчитаем ИМТ (нужен рост и вес, возьмём из первой записи каждого пользователя)
    bmi_data = (
        df.groupby("user_id")
        .agg(height=("height_cm", "first"), weight=("weight_kg", "first"))
        .reset_index()
    )
    users = users.merge(bmi_data, on="user_id")
    users["bmi"] = users["weight"] / ((users["height"] / 100) ** 2)

    # Отклонение от цели
    users["deviation"] = users["avg_cal"] - users["target_cal_per_day"]
    users["percent_of_target"] = (users["avg_cal"] / users["target_cal_per_day"]) * 100

    print("\n=== Сравнение пользователей ===")
    print(
        users[
            [
                "name",
                "gender",
                "activity_level",
                "bmi",
                "target_cal_per_day",
                "avg_cal",
                "deviation",
                "percent_of_target",
            ]
        ].to_string(index=False)
    )

def meal_time_analysis(df, user_id):
    user_df = df[df["user_id"] == user_id]
    if user_df.empty:
        print(f"Пользователь с ID {user_id} не найден.")
        return

    # Группировка по типу приёма
    meal_stats = (
        user_df.groupby("meal_type")
        .agg(avg_cal=("dish_calories", "mean"), count=("dish_name", "count"))
        .reset_index()
    )

    # Поздние перекусы (после 21:00)
    late_snacks = user_df[(user_df["hour"] >= 21) & (user_df["meal_type"] == "перекус")]
    late_count = late_snacks.shape[0]
    late_days = late_snacks["date_only"].nunique()

    name = user_df.iloc[0]["name"]
    print(f"\n=== Анализ приемов пищи для {name} ===")
    print("Средняя калорийность по типам приёмов:")
    for _, row in meal_stats.iterrows():
        print(f"  {row['meal_type']:10} – {row['avg_cal']:.0f} ккал (всего {row['count']} приёмов)")

    print(f"\nПоздние перекусы (после 21:00): {late_count} раз(а) за {late_days} дней")
    if late_count > 0:
        print("  Примеры:")
        print(
            late_snacks[["date_only", "dish_name", "servings", "dish_calories"]]
            .head(5)
            .to_string(index=False)
        )

def nutrition_calendar(df, user_id, year=None, month=None):
    user_df = df[df["user_id"] == user_id].copy()
    if user_df.empty:
        print(f"Пользователь с ID {user_id} не найден.")
        return

    user_df["year"] = user_df["date"].dt.year
    user_df["month"] = user_df["date"].dt.month

    if year is None:
        year = user_df["year"].max()
    if month is None:
        month = user_df[user_df["year"] == year]["month"].max()

    mask = (user_df["year"] == year) & (user_df["month"] == month)
    month_df = user_df[mask]
    if month_df.empty:
        print(f"Нет данных за {year}-{month}")
        return

    daily_cal = month_df.groupby("date_only")["dish_calories"].sum().reset_index()
    daily_cal.columns = ["date", "calories"]
    target = user_df.iloc[0]["target_cal_per_day"]

    # Добавим цветовую индикацию отклонения (текстом)
    daily_cal["deviation"] = daily_cal["calories"] - target
    daily_cal["status"] = daily_cal["deviation"].apply(
        lambda x: (
            "⬆️ превышение"
            if x > target * 0.1
            else ("⬇️ недобор" if x < -target * 0.1 else "✅ норма")
        )
    )

    name = user_df.iloc[0]["name"]
    print(f"\n=== Календарь питания для {name} за {year}-{month:02d} ===")
    print(f"Цель: {target:.0f} ккал/день\n")
    print(daily_cal.to_string(index=False))
    
def progress_to_goal(df, user_id):
    user_df = df[df["user_id"] == user_id].copy()
    if user_df.empty:
        print(f"Пользователь с ID {user_id} не найден.")
        return

    # Ежедневное потребление
    daily = user_df.groupby("date_only").agg(actual_cal=("dish_calories", "sum")).reset_index()

    # Информация о пользователе
    info = user_df.iloc[0]
    target_cal = info["target_cal_per_day"]
    tdee = info["tdee"]  # Total Daily Energy Expenditure
    initial_weight = info["weight_kg"]

    # Накопленный дефицит/профицит (относительно TDEE, а не target_cal_per_day)
    # target_cal_per_day уже учитывает цель (дефицит/профицит относительно TDEE)
    # Правильнее: deficit = TDEE - actual_cal
    daily["deficit"] = tdee - daily["actual_cal"]
    cumulative_deficit = daily["deficit"].sum()

    # 1 кг жира ≈ 7700 ккал
    weight_change = cumulative_deficit / 7700
    final_weight = initial_weight + weight_change  # если дефицит, weight_change отрицательный

    name = info["name"]
    print(f"\n=== Прогресс к цели для {name} ===")
    print(f"Начальный вес: {initial_weight:.1f} кг")
    print(f"TDEE: {tdee:.0f} ккал/день, целевая калорийность: {target_cal:.0f} ккал/день")
    print(f"Фактическое среднее потребление: {daily['actual_cal'].mean():.0f} ккал/день")
    print(f"Общий дефицит(+) / профицит(-) за период: {cumulative_deficit:+.0f} ккал")
    print(f"Прогнозируемое изменение веса: {weight_change:+.1f} кг")
    print(f"Текущий прогнозируемый вес: {final_weight:.1f} кг")

    # Если есть несколько дней, покажем динамику
    if len(daily) > 1:
        print("\nДинамика дефицита по дням (первые 7 дней):")
        print(daily.head(7)[["date_only", "actual_cal", "deficit"]].to_string(index=False))

def overall_statistics(df):
    total_users = df["user_id"].nunique()
    total_meals = len(df)
    total_dishes = df["dish_name"].nunique()
    date_range = f"{df['date'].min().date()} – {df['date'].max().date()}"

    # Цели пользователей
    goals = df.groupby("user_id")["goal"].first().value_counts()

    print("\n=== Общая статистика ===")
    print(f"Период данных: {date_range}")
    print(f"Всего пользователей: {total_users}")
    print(f"Всего приёмов пищи: {total_meals}")
    print(f"Уникальных блюд: {total_dishes}")
    print("\nРаспределение целей:")
    for goal, count in goals.items():
        print(f"  {goal}: {count} пользователь(ей)")

    # Среднее потребление на пользователя
    user_avg = df.groupby("user_id")["dish_calories"].mean().mean()
    print(f"\nСреднее потребление калорий на одного пользователя: {user_avg:.0f} ккал/приём")

def efficiency_report(df, user_id):
    user_df = df[df["user_id"] == user_id].copy()
    if user_df.empty:
        print(f"Пользователь с ID {user_id} не найден.")
        return

    daily = user_df.groupby("date_only").agg(total_cal=("dish_calories", "sum")).reset_index()
    target = user_df.iloc[0]["target_cal_per_day"]

    daily["within_10pct"] = (daily["total_cal"] >= target * 0.9) & (
        daily["total_cal"] <= target * 1.1
    )
    days_in_range = daily["within_10pct"].sum()
    total_days = len(daily)
    pct = (days_in_range / total_days) * 100 if total_days > 0 else 0

    # Пропуски приёмов (дни, где меньше 3 приёмов?)
    meals_per_day = user_df.groupby("date_only")["meal_type"].nunique()
    low_meal_days = (meals_per_day < 3).sum()

    name = user_df.iloc[0]["name"]
    print(f"\n=== Отчет по эффективности для {name} ===")
    print(f"Цель: {target:.0f} ккал/день")
    print(f"Всего дней с данными: {total_days}")
    print(f"Дней в пределах ±10% от цели: {days_in_range} ({pct:.1f}%)")
    print(f"Дней с малым количеством приёмов (<3): {low_meal_days}")

    # Дни с превышением/недобором
    over_days = (daily["total_cal"] > target * 1.1).sum()
    under_days = (daily["total_cal"] < target * 0.9).sum()
    print(f"Дней с превышением (>110%): {over_days}")
    print(f"Дней с недобором (<90%): {under_days}")

