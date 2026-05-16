import asyncio
import io
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Импортируем наши модули
from core.reports import (
    load_data,
    get_user_list,
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

# Глобальные переменные с данными
MEALS_DF = None
PERSONS_LIST = None
USERS_DF = None

# Словарь для хранения выбранного пользователя (chat_id -> Person)
USER_SELECTION = {}

# Список отчётов в формате (название, функция, нужен ли график)
REPORTS = [
    ("Персональная статистика", personal_statistics, True),
    ("Анализ макронутриентов", macro_analysis, True),
    ("Топ блюд по частоте", top_frequent_dishes, False),
    ("Топ блюд по калориям", top_caloric_dishes, False),
    ("Сравнение пользователей", compare_users, True),
    ("Анализ приемов по времени", meal_time_analysis, True),
    ("Календарь питания", nutrition_calendar, True),
    ("Прогресс к цели", progress_to_goal, True),
    ("Общая статистика", overall_statistics, False),
    ("Отчет по эффективности", efficiency_report, True),
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие и показ списка пользователей для выбора."""
    user_list = get_user_list(MEALS_DF)
    keyboard = [
        [
            InlineKeyboardButton(
                f"{row['name']} (ID {row['user_id']})", callback_data=f"user_{row['user_id']}"
            )
        ]
        for _, row in user_list.iterrows()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Привет! Выбери свой профиль:", reply_markup=reply_markup)


async def user_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет выбранного пользователя и показывает меню отчётов."""
    query = update.callback_query
    await query.answer()
    user_id_str = query.data.split("_")[1]
    user_id = int(user_id_str)

    # Находим объект Person
    person = next((p for p in PERSONS_LIST if p.user_id == user_id), None)
    if not person:
        await query.edit_message_text("❌ Ошибка: пользователь не найден.")
        return

    chat_id = update.effective_chat.id
    USER_SELECTION[chat_id] = person

    # Меню отчётов
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"report_{idx}")]
        for idx, (name, _, _) in enumerate(REPORTS)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"✅ Выбран {person.name} (ID {person.user_id})\n\nВыбери отчёт:", reply_markup=reply_markup
    )


async def run_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает выбранный отчёт и отправляет результат (текст + график если есть)."""
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id

    person = USER_SELECTION.get(chat_id)
    if not person:
        await query.edit_message_text("❌ Сначала выбери пользователя командой /start")
        return

    report_idx = int(query.data.split("_")[1])
    report_name, report_func, has_plot = REPORTS[report_idx]

    # Выполняем отчёт (текстовый вывод)
    text_lines = report_func(MEALS_DF, person.user_id)
    text_output = "\n".join(text_lines)

    # Если отчёт может содержать график, пытаемся его сгенерировать
    if has_plot:
        # Для отчётов, которые строят графики, мы перехватываем вывод matplotlib
        # Создаём временный файл для изображения
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            tmp_path = tmpfile.name

        # Временно перенаправляем вывод графиков в этот файл
        original_show = plt.show

        def save_and_close(*args, **kwargs):
            plt.savefig(tmp_path, dpi=100, bbox_inches="tight")
            plt.close()

        plt.show = save_and_close
        try:
            # Вызываем функцию отчёта ещё раз, но теперь она сохранит график
            report_func(MEALS_DF, person.user_id)
        except Exception as e:
            print(f"Ошибка генерации графика: {e}")
        finally:
            plt.show = original_show

        # Отправляем текст
        await query.edit_message_text(text_output[:4096])  # лимит телеграма

        # Отправляем изображение, если оно создалось
        if Path(tmp_path).exists():
            with open(tmp_path, "rb") as f:
                await context.bot.send_photo(chat_id=chat_id, photo=f)
            Path(tmp_path).unlink()
        else:
            await context.bot.send_message(
                chat_id=chat_id, text="⚠️ Не удалось сгенерировать график."
            )
    else:
        # Только текст
        await query.edit_message_text(text_output[:4096])

    # После отправки показываем меню снова (для удобства)
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"report_{idx}")]
        for idx, (name, _, _) in enumerate(REPORTS)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=chat_id, text="🔁 Выбери другой отчёт:", reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Команды:\n"
        "/start – выбор пользователя\n"
        "/menu – показать меню отчётов\n"
        "/help – эта справка"
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    person = USER_SELECTION.get(chat_id)
    if not person:
        await update.message.reply_text("Сначала выбери пользователя через /start")
        return
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"report_{idx}")]
        for idx, (name, _, _) in enumerate(REPORTS)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Меню для {person.name}:", reply_markup=reply_markup)


def main():
    global MEALS_DF, PERSONS_LIST, USERS_DF
    # Загружаем данные (путь к CSV может отличаться)
    PERSONS_LIST, MEALS_DF = load_data("data/nutrition_data.csv")
    USERS_DF = get_user_list(MEALS_DF)

    # Создаём приложение
    app = Application.builder().token("8657864252:AAH_ie2w_p2og6pn-FxK7LOPK0ivUP9ZzUg").build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CallbackQueryHandler(user_selected, pattern="^user_"))
    app.add_handler(CallbackQueryHandler(run_report, pattern="^report_"))

    # Запускаем бота
    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
