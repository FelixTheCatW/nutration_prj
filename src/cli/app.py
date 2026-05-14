import curses
import textwrap

def draw_menu(stdscr, items, descriptions, current_idx, start_idx, height, width):
    """Отрисовка двухколоночного меню.
    items: список названий пунктов
    descriptions: список описаний (соответствует items)
    current_idx: выбранный индекс в общем списке
    start_idx: с какого индекса начинать отображение (для прокрутки)
    height, width: размеры экрана
    """
    stdscr.clear()
    # Левая колонка – список (30% ширины)
    list_width = max(30, width // 3) + 5
    desc_width = width - list_width - 2

    # Заголовок
    stdscr.addstr(0, 0, "Доступные отчеты (↑/↓ - выбор, Enter - запуск)", curses.A_BOLD)
    stdscr.addstr(0, list_width + 2, "Описание", curses.A_BOLD)

    max_display = height - 3  # строк под список
    visible_items = items[start_idx:start_idx + max_display]

    for i, item in enumerate(visible_items):
        y = i + 2
        x = 0
        idx = start_idx + i
        # Выделяем текущий пункт
        if idx == current_idx:
            stdscr.addstr(y, x, f"> {item}", curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, f"  {item}")

    # Описание текущего пункта
    if 0 <= current_idx < len(descriptions):
        desc = descriptions[current_idx]
        wrapped = textwrap.wrap(desc, width=desc_width)
        for i, line in enumerate(wrapped):
            if i + 2 < height:
                stdscr.addstr(i + 2, list_width + 2, line)

    stdscr.refresh()

def main_curses(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    # Пример данных – ваши реальные отчеты
    items = [
        "1. Персональная статистика пользователя",
        "2. Анализ макронутриентов",
        "3. Топ блюд по частоте",
        "4. Топ блюд по калориям",
        "5. Сравнение пользователей",
        "6. Анализ приемов по времени",
        "7. Календарь питания",
        "8. Прогресс к цели",
        "9. Общая статистика",
        "10. Отчет по эффективности",
        # ... можно добавить ещё
    ]
    descriptions = [
        "Суммарное потребление калорий и БЖУ, сравнение с целью, динамика по дням.",
        "Соотношение белков, жиров, углеводов в процентах от калорий, сравнение с нормой.",
        "Список блюд, которые пользователь заказывает чаще всего (по количеству приемов).",
        "Самые калорийные блюда в рационе (средняя калорийность за прием).",
        "Сводная таблица по всем пользователям: ИМТ, активность, среднее отклонение от нормы.",
        "Средняя калорийность завтрака, обеда, ужина, перекусов; поздние приемы пищи.",
        "Тепловая карта калорий по дням месяца, выделение дней с сильным превышением.",
        "Прогноз изменения веса на основе дефицита/профицита калорий.",
        "Количество приемов, общее потребление по всем пользователям, распределение целей.",
        "Процент дней, когда калорийность в пределах ±10% от цели, пропуски приемов.",
    ]

    current_idx = 0
    start_idx = 0
    height, width = stdscr.getmaxyx()

    while True:
        draw_menu(stdscr, items, descriptions, current_idx, start_idx, height, width)
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break
        elif key == curses.KEY_UP:
            if current_idx > 0:
                current_idx -= 1
                if current_idx < start_idx:
                    start_idx = current_idx
        elif key == curses.KEY_DOWN:
            if current_idx < len(items) - 1:
                current_idx += 1
                # Прокрутка вниз, если выбранный уходит за видимую область
                if current_idx >= start_idx + (height - 3):
                    start_idx = current_idx - (height - 3) + 1
        elif key == ord('\n') or key == curses.KEY_ENTER:
            # Запуск выбранного отчета
            # Здесь надо очистить экран и выполнить генерацию отчета
            # После генерации – вернуться в меню (например, по нажатию любой клавиши)
            generate_report_for_item(items[current_idx])  # ваша функция
            stdscr.clear()
            stdscr.addstr(0, 0, "Отчет сгенерирован. Нажмите любую клавишу для возврата в меню.")
            stdscr.refresh()
            stdscr.getch()

    curses.endwin()

def generate_report_for_item(item_name):
    # Здесь ваша логика генерации отчета (сохранить в файл, вывести в консоль и т.д.)
    # Для примера просто имитируем
    print(f"Генерация отчета: {item_name}")
    # Можно также создать временный файл и открыть его через less, или просто вывести в curses

def main():
    curses.wrapper(main_curses)

if __name__ == '__main__':
    main()