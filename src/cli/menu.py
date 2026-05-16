# src/cli/menu.py

from core.reports import (
    personal_statistics,
    macro_analysis,
    top_frequent_dishes,
    top_caloric_dishes,
    compare_users,
    meal_time_analysis,
    nutrition_calendar,
    progress_to_goal,
    overall_statistics,
    efficiency_report,
)

# Список кортежей: (название, описание, функция)
menu_options = [
    (
        "Персональная статистика",
        "Суммарное потребление калорий и БЖУ, сравнение с целью, динамика по дням.",
        personal_statistics,  # принимает (df_meals, user_id)
    ),
    (
        "Анализ макронутриентов",
        "Соотношение белков, жиров, углеводов в процентах от калорий, сравнение с нормой.",
        macro_analysis,  # принимает (df_meals, user_id)
    ),
    (
        "Топ блюд по частоте",
        "Список блюд, которые пользователь заказывает чаще всего (по количеству приемов).",
        top_frequent_dishes,  # принимает (df_meals, user_id)
    ),
    (
        "Топ блюд по калориям",
        "Самые калорийные блюда в рационе (средняя калорийность за прием).",
        top_caloric_dishes,  # принимает (df_meals, user_id)
    ),
    (
        "Сравнение пользователей",
        "Сводная таблица по всем пользователям: ИМТ, активность, среднее отклонение от нормы.",
        compare_users,  # принимает (df_meals, list[Person])
    ),
    (
        "Анализ приемов по времени",
        "Средняя калорийность завтрака, обеда, ужина, перекусов; поздние приемы пищи.",
        meal_time_analysis,  # принимает (df_meals, user_id)
    ),
    (
        "Календарь питания",
        "Тепловая карта калорий по дням месяца, выделение дней с сильным превышением.",
        nutrition_calendar,  # принимает (df_meals, user_id)
    ),
    (
        "Прогресс к цели",
        "Прогноз изменения веса на основе дефицита/профицита калорий.",
        progress_to_goal,  # принимает (df_meals, user_id)
    ),
    (
        "Общая статистика",
        "Количество приемов, общее потребление по всем пользователям, распределение целей.",
        overall_statistics,  # принимает (df_meals, list[Person])
    ),
    (
        "Отчет по эффективности",
        "Процент дней, когда калорийность в пределах ±10% от цели, пропуски приемов.",
        efficiency_report,  # принимает (df_meals, user_id)
    ),
]

# Для удобства можно также создать отдельные списки названий и описаний,
# извлекая их из кортежей:
MENU_ITEMS = [item[0] for item in menu_options]
MENU_DESC = [item[1] for item in menu_options]
MENU_ACTIONS = [item[2] for item in menu_options]
