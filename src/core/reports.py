import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from tabulate import tabulate
from core.Person import Person
from core.registries import REPORT_CAPTIONS

# Настройка бэкенда для интерактивных окон (можно оставить TkAgg)
matplotlib.use("TkAgg")
# Поддержка кириллицы
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Microsoft Sans Serif"]
plt.rcParams["axes.unicode_minus"] = False


def pretty_print(df: pd.DataFrame, columns: list[str] = None) -> list[str]:
    if columns is None:
        columns = [col for col in df.columns if col in REPORT_CAPTIONS]
    df_display = df[columns].copy().rename(columns=REPORT_CAPTIONS)
    return tabulate(df_display, headers="keys", tablefmt="plain", showindex=False).split("\n")


def load_data(filepath: str) -> tuple[list[Person], pd.DataFrame]:
    df = pd.read_csv(filepath)

    df["date"] = pd.to_datetime(df["date"])
    df["date_only"] = df["date"].dt.date
    df["hour"] = pd.to_datetime(df["eaten_at"], format="%H:%M").dt.hour

    users_df = df.groupby("user_id").first().reset_index()

    persons = []
    for _, row in users_df.iterrows():
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
        p.bmr = row["bmr"]
        p.tdee = row["tdee"]
        p.target_cal_per_day = row["target_cal_per_day"]
        p.target_protein_g = row["target_protein_g"]
        persons.append(p)
    return persons, df


def get_user_list(df):
    users = df[["user_id", "name"]].drop_duplicates().sort_values("user_id")
    return users


def plot_calorie_trend(daily_df: pd.DataFrame, target_cal: float):
    plt.figure(figsize=(10, 5))
    plt.plot(
        daily_df["date_only"],
        daily_df["total_cal"],
        marker="o",
        linestyle="-",
        linewidth=1,
        markersize=3,
    )
    plt.axhline(y=target_cal, color="r", linestyle="--", label=f"Цель {target_cal:.0f} ккал")
    plt.xlabel("Дата")
    plt.ylabel("Калории (ккал)")
    plt.title("Динамика потребления калорий")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show(block=True)



def plot_macro_pie(avg_protein, avg_fat, avg_carbs):
    cal_protein = avg_protein * 4
    cal_fat = avg_fat * 9
    cal_carbs = avg_carbs * 4
    sizes = [cal_protein, cal_fat, cal_carbs]
    labels = ["Белки", "Жиры", "Углеводы"]
    colors = ["#66b3ff", "#ff9999", "#99ff99"]
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
    plt.title("Распределение калорий по макронутриентам")
    plt.axis("equal")
    plt.tight_layout()
    plt.show(block=True)



def plot_users_comparison(users_display: pd.DataFrame):
    users_sorted = users_display.sort_values("avg_cal")
    x = range(len(users_sorted))
    width = 0.35
    plt.figure(figsize=(10, 6))
    plt.bar(x, users_sorted["avg_cal"], width, label="Среднее потребление", color="blue")
    plt.bar(
        [i + width for i in x],
        users_sorted["target_cal_per_day"],
        width,
        label="Цель",
        color="orange",
    )
    plt.xticks([i + width / 2 for i in x], users_sorted["name"], rotation=45)
    plt.ylabel("Калории (ккал)")
    plt.title("Сравнение среднего потребления с целевой калорийностью")
    plt.legend()
    plt.tight_layout()
    plt.show(block=True)



def plot_meal_type_calories(meal_stats: pd.DataFrame):
    plt.figure(figsize=(8, 4))
    plt.bar(meal_stats["meal_type"], meal_stats["avg_cal"], color="skyblue")
    plt.xlabel("Тип приёма пищи")
    plt.ylabel("Средняя калорийность (ккал)")
    plt.title("Средняя калорийность по типам приёмов")
    plt.tight_layout()
    plt.show(block=True)



def plot_monthly_calendar(daily_cal: pd.DataFrame, target: float):
    daily_cal = daily_cal.sort_values("date")
    plt.figure(figsize=(12, 5))
    plt.bar(daily_cal["date"].dt.day, daily_cal["calories"], width=0.8, color="teal")
    plt.axhline(y=target, color="r", linestyle="--", label=f"Цель {target:.0f} ккал")
    plt.xlabel("День месяца")
    plt.ylabel("Калории (ккал)")
    plt.title(f"Калорийность по дням за {daily_cal['date'].dt.strftime('%Y-%m').iloc[0]}")
    plt.legend()
    plt.xticks(range(1, 32))
    plt.tight_layout()
    plt.show(block=True)



def plot_cumulative_deficit(daily: pd.DataFrame):
    daily = daily.sort_values("date_only")
    daily["cumulative"] = daily["deficit"].cumsum()
    plt.figure(figsize=(10, 5))
    plt.fill_between(daily["date_only"], 0, daily["cumulative"], color="green", alpha=0.3)
    plt.plot(daily["date_only"], daily["cumulative"], marker="o", linestyle="-", linewidth=1)
    plt.xlabel("Дата")
    plt.ylabel("Накопленный дефицит (ккал)")
    plt.title("Накопленный дефицит калорий")
    plt.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show(block=True)



def plot_efficiency_bars(total_days, under_days, within_days, over_days):
    categories = ["Недобор (<90%)", "Норма (±10%)", "Превышение (>110%)"]
    values = [under_days, within_days, over_days]
    plt.figure(figsize=(6, 4))
    plt.bar(categories, values, color=["red", "green", "orange"])
    plt.ylabel("Количество дней")
    plt.title("Эффективность достижения цели по дням")
    plt.tight_layout()
    plt.show(block=True)



# ------------------- Функции отчётов -------------------
def personal_statistics(df: pd.DataFrame, user_id: int) -> list[str]:
    user_df = df[df["user_id"] == user_id].copy()
    if user_df.empty:
        return [f"Пользователь с ID {user_id} не найден."]

    user_info = user_df.iloc[0]
    target_cal = user_info["target_cal_per_day"]

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

    total_days = len(daily)
    avg_cal = daily["total_cal"].mean()
    avg_protein = daily["total_protein"].mean()
    avg_fat = daily["total_fat"].mean()
    avg_carbs = daily["total_carbs"].mean()

    deviation = avg_cal - target_cal
    percent_of_target = (avg_cal / target_cal) * 100

    out = []
    out.append("=== Персональная статистика ===")
    out.append(f"Период: {daily['date_only'].min()} – {daily['date_only'].max()}")
    out.append(f"Всего дней с записями: {total_days}")
    out.append("Среднее в день:")
    out.append(
        f"  Калории: {avg_cal:.0f} ккал (цель {target_cal:.0f} ккал, {percent_of_target:.1f}% от цели)"
    )
    out.append(f"  Белки: {avg_protein:.1f} г")
    out.append(f"  Жиры: {avg_fat:.1f} г")
    out.append(f"  Углеводы: {avg_carbs:.1f} г")
    out.append(f"Отклонение от цели: {deviation:+.0f} ккал в день")
    out.append("Динамика по дням (первые 7 дней):")
    out.extend(pretty_print(daily.head(7)))

    # График в потоке (передаём копию данных)
    plot_calorie_trend(daily.copy(), target_cal)
    return out


def macro_analysis(df: pd.DataFrame, user_id: int) -> list[str]:
    user_df = df[df["user_id"] == user_id]
    if user_df.empty:
        return [f"Пользователь с ID {user_id} не найден."]

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

    avg_cal = daily["cal"].mean()
    avg_protein = daily["protein"].mean()
    avg_fat = daily["fat"].mean()
    avg_carbs = daily["carbs"].mean()

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

    out = []
    out.append("=== Анализ макронутриентов ===")
    out.append("Среднее потребление в день:")
    out.append(f"  Белки: {avg_protein:.1f} г → {cal_from_protein:.0f} ккал ({pct_protein:.1f}%)")
    out.append(f"  Жиры:  {avg_fat:.1f} г → {cal_from_fat:.0f} ккал ({pct_fat:.1f}%)")
    out.append(f"  Углеводы: {avg_carbs:.1f} г → {cal_from_carbs:.0f} ккал ({pct_carbs:.1f}%)")
    out.append(
        f"  Итого (расчёт): {total_calc:.0f} ккал, средние калории из таблицы: {avg_cal:.0f} ккал"
    )
    out.append("Сравнение с рекомендуемым соотношением (30/20/50):")
    out.append(f"  Белки: {pct_protein:.1f}% vs 30%")
    out.append(f"  Жиры:  {pct_fat:.1f}% vs 20%")
    out.append(f"  Углеводы: {pct_carbs:.1f}% vs 50%")

    plot_macro_pie(avg_protein, avg_fat, avg_carbs)
    return out


def top_frequent_dishes(df: pd.DataFrame, user_id: int, top_n: int = 10) -> list[str]:
    user_df = df[df["user_id"] == user_id]
    if user_df.empty:
        return [f"Пользователь с ID {user_id} не найден."]

    freq = user_df.groupby("dish_name").size().sort_values(ascending=False).head(top_n)

    out = [f"=== Топ-{top_n} самых частых блюд ==="]
    for i, (dish, count) in enumerate(freq.items(), 1):
        out.append(f"{i:2}. {dish:30} – {count} раз(а)")
    return out


def top_caloric_dishes(df: pd.DataFrame, user_id: int, top_n: int = 10) -> list[str]:
    user_df = df[df["user_id"] == user_id]
    if user_df.empty:
        return [f"Пользователь с ID {user_id} не найден."]

    user_df = user_df.copy()
    user_df["total_dish_cal"] = user_df["dish_calories"] * user_df["servings"]
    cal_mean = (
        user_df.groupby("dish_name")["total_dish_cal"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
    )

    out = [f"=== Топ-{top_n} самых калорийных блюд (средняя калорийность за приём) ==="]
    for i, (dish, cal) in enumerate(cal_mean.items(), 1):
        out.append(f"{i:2}. {dish:30} – {cal:.0f} ккал в среднем за приём")
    return out


def compare_users(df: pd.DataFrame, user_id: int) -> list[str]:
    users = (
        df.groupby(["user_id", "name", "target_cal_per_day", "activity_level", "gender"])
        .agg(avg_cal=("dish_calories", "mean"), total_days=("date", lambda x: x.nunique()))
        .reset_index()
    )

    bmi_data = (
        df.groupby("user_id")
        .agg(height=("height_cm", "first"), weight=("weight_kg", "first"))
        .reset_index()
    )

    users_display = users.copy()
    users_display = users_display.merge(bmi_data, on="user_id").round(0)

    users_display["bmi"] = (users_display["weight"] / ((users_display["height"] / 100) ** 2)).round(
        0
    )

    users_display["deviation"] = (
        users_display["avg_cal"] - users_display["target_cal_per_day"]
    ).round(0)
    users_display["avg_cal"] = users_display["avg_cal"].round(0)
    users_display["percent_of_target"] = (
        (users_display["avg_cal"] / users_display["target_cal_per_day"]) * 100
    ).round(0)

    out = ["=== Сравнение пользователей ==="]
    out.extend(
        pretty_print(
            users_display[
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
            ]
        )
    )

    plot_users_comparison(users_display.copy())
    return out


def meal_time_analysis(df: pd.DataFrame, user_id: int) -> list[str]:
    user_df = df[df["user_id"] == user_id]
    if user_df.empty:
        return [f"Пользователь с ID {user_id} не найден."]

    meal_stats = (
        user_df.groupby("meal_type")
        .agg(avg_cal=("dish_calories", "mean"), count=("dish_name", "count"))
        .reset_index()
    )

    late_snacks = user_df[(user_df["hour"] >= 21) & (user_df["meal_type"] == "перекус")]
    late_count = late_snacks.shape[0]
    late_days = late_snacks["date_only"].nunique() if not late_snacks.empty else 0

    out = ["=== Анализ приемов пищи ==="]
    out.append("Средняя калорийность по типам приёмов:")
    for _, row in meal_stats.iterrows():
        out.append(
            f"  {row['meal_type']:10} – {row['avg_cal']:.0f} ккал (всего {row['count']} приёмов)"
        )
    out.append(f"Поздние перекусы (после 21:00): {late_count} раз(а) за {late_days} дней")
    if late_count > 0:
        out.append("  Примеры:")
        out.extend(
            pretty_print(
                late_snacks[["date_only", "dish_name", "servings", "dish_calories"]].head(5)
            )
        )

    plot_meal_type_calories(meal_stats.copy())
    return out


def nutrition_calendar(df: pd.DataFrame, user_id: int) -> list[str]:
    user_df = df[df["user_id"] == user_id].copy()
    if user_df.empty:
        return [f"Пользователь с ID {user_id} не найден."]

    user_df["year"] = user_df["date"].dt.year
    user_df["month"] = user_df["date"].dt.month

    year = user_df["year"].max()
    month = user_df[user_df["year"] == year]["month"].max()

    mask = (user_df["year"] == year) & (user_df["month"] == month)
    month_df = user_df[mask]
    if month_df.empty:
        return [f"Нет данных за {year}-{month}"]

    daily_cal = month_df.groupby("date_only")["dish_calories"].sum().reset_index()
    daily_cal.columns = ["date", "calories"]
    target = user_df.iloc[0]["target_cal_per_day"]

    daily_cal["deviation"] = daily_cal["calories"] - target
    daily_cal["status"] = daily_cal["deviation"].apply(
        lambda x: (
            "⬆️ превышение"
            if x > target * 0.1
            else ("⬇️ недобор" if x < -target * 0.1 else "✅ норма")
        )
    )

    out = [f"=== Календарь питания за {year}-{month:02d} ==="]
    out.append(f"Цель: {target:.0f} ккал/день")
    out.extend(daily_cal.to_string(index=False).split("\n"))

    lambda: plot_monthly_calendar(daily_cal.copy(), target)
    return out


def progress_to_goal(df: pd.DataFrame, user_id: int) -> list[str]:
    user_df = df[df["user_id"] == user_id].copy()
    if user_df.empty:
        return [f"Пользователь с ID {user_id} не найден."]

    daily = user_df.groupby("date_only").agg(actual_cal=("dish_calories", "sum")).reset_index()
    info = user_df.iloc[0]
    target_cal = info["target_cal_per_day"]
    tdee = info["tdee"]
    initial_weight = info["weight_kg"]

    daily["deficit"] = tdee - daily["actual_cal"]
    cumulative_deficit = daily["deficit"].sum()
    weight_change = cumulative_deficit / 7700
    final_weight = initial_weight + weight_change

    out = ["=== Прогресс к цели ==="]
    out.append(f"Начальный вес: {initial_weight:.1f} кг")
    out.append(f"TDEE: {tdee:.0f} ккал/день, целевая калорийность: {target_cal:.0f} ккал/день")
    out.append(f"Фактическое среднее потребление: {daily['actual_cal'].mean():.0f} ккал/день")
    out.append(f"Общий дефицит(+) / профицит(-) за период: {cumulative_deficit:+.0f} ккал")
    out.append(f"Прогнозируемое изменение веса: {weight_change:+.1f} кг")
    out.append(f"Текущий прогнозируемый вес: {final_weight:.1f} кг")
    if len(daily) > 1:
        out.append("Динамика дефицита по дням (первые 7 дней):")
        out.extend(
            daily.head(7)[["date_only", "actual_cal", "deficit"]].to_string(index=False).split("\n")
        )

    plot_cumulative_deficit(daily.copy())
    return out


def overall_statistics(df: pd.DataFrame, user_id: int) -> list[str]:
    total_users = df["user_id"].nunique()
    total_meals = len(df)
    total_dishes = df["dish_name"].nunique()
    date_range = f"{df['date'].min().date()} – {df['date'].max().date()}"
    goals = df.groupby("user_id")["goal"].first().value_counts()
    user_avg = df.groupby("user_id")["dish_calories"].mean().mean()

    out = ["=== Общая статистика ==="]
    out.append(f"Период данных: {date_range}")
    out.append(f"Всего пользователей: {total_users}")
    out.append(f"Всего приёмов пищи: {total_meals}")
    out.append(f"Уникальных блюд: {total_dishes}")
    out.append("Распределение целей:")
    for goal, count in goals.items():
        out.append(f"  {goal}: {count} пользователь(ей)")
    out.append(f"Среднее потребление калорий на одного пользователя: {user_avg:.0f} ккал/приём")
    return out


def efficiency_report(df: pd.DataFrame, user_id: int) -> list[str]:
    user_df = df[df["user_id"] == user_id].copy()
    if user_df.empty:
        return [f"Пользователь с ID {user_id} не найден."]

    daily = user_df.groupby("date_only").agg(total_cal=("dish_calories", "sum")).reset_index()
    target = user_df.iloc[0]["target_cal_per_day"]

    daily["within_10pct"] = (daily["total_cal"] >= target * 0.9) & (
        daily["total_cal"] <= target * 1.1
    )
    days_in_range = daily["within_10pct"].sum()
    total_days = len(daily)
    pct = (days_in_range / total_days) * 100 if total_days > 0 else 0

    meals_per_day = user_df.groupby("date_only")["meal_type"].nunique()
    low_meal_days = (meals_per_day < 3).sum()

    over_days = (daily["total_cal"] > target * 1.1).sum()
    under_days = (daily["total_cal"] < target * 0.9).sum()

    out = ["=== Отчет по эффективности ==="]
    out.append(f"Цель: {target:.0f} ккал/день")
    out.append(f"Всего дней с данными: {total_days}")
    out.append(f"Дней в пределах ±10% от цели: {days_in_range} ({pct:.1f}%)")
    out.append(f"Дней с малым количеством приёмов (<3): {low_meal_days}")
    out.append(f"Дней с превышением (>110%): {over_days}")
    out.append(f"Дней с недобором (<90%): {under_days}")

    plot_efficiency_bars(total_days, under_days, days_in_range, over_days)

    return out
