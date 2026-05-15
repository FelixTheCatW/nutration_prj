import curses
from pandas import DataFrame
from cli.menu import MENU_ITEMS, MENU_DESC
from cli.screen_writer import ScreenWriter, init_colors
from cli.user_popup import select_user_popup
from core.Person import Person
from core.reprots import *


TOP_LEFT_SCR: ScreenWriter
TOP_RIGHT_SCR: ScreenWriter
BODY_SCR: ScreenWriter
Nutrition_Data: DataFrame
Users_Data: list[Person]
SELECTED_PERSON: Person = None

def draw_screen(stdscr, items, descriptions, current_idx):
    init_screens(stdscr)

    for i, item in enumerate(MENU_ITEMS):
        if i == current_idx:
            TOP_LEFT_SCR.write(f"► {i + 1:2}. {item}", 140)
            TOP_RIGHT_SCR.write(descriptions[current_idx])
        else:
            TOP_LEFT_SCR.write(f"  {i + 1:2}. {item}")
   

def init_screens(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    height, width = stdscr.getmaxyx()
    list_width = max(30, width // 3) + 5
    desc_width = width - list_width
    header_height = 12
    report_height = height - 1

    global TOP_LEFT_SCR, TOP_RIGHT_SCR, BODY_SCR
    TOP_LEFT_SCR = ScreenWriter(stdscr, 0, 0, list_width, header_height)
    TOP_RIGHT_SCR = ScreenWriter(stdscr, list_width + 1, 0, desc_width, header_height)
    BODY_SCR = ScreenWriter(stdscr, 0, header_height, width, report_height)

    # Заголовок
    TOP_LEFT_SCR.write("Доступные отчеты".center(list_width), 171)
    TOP_RIGHT_SCR.write("Описание".center(desc_width), 171)
    # подвал
    help_msg = "↑/↓ - выбор | Enter - запуск | U - выбрать пользователя | Q: выход"    
    BODY_SCR.write_bottom(help_msg, 171)
    if SELECTED_PERSON:
        selected_user = f"Клиент: {SELECTED_PERSON.name} ({SELECTED_PERSON.city}), {SELECTED_PERSON.gender[0]} — {SELECTED_PERSON.height_cm}/{SELECTED_PERSON.age}"
        selected_user += f" цель: {SELECTED_PERSON.goal}, активность: {SELECTED_PERSON.activity_level}"
        TOP_RIGHT_SCR.write_bottom(selected_user, 99)


def main_curses(stdscr):
    init_screens(stdscr)
    current_idx = 0
    height, width = stdscr.getmaxyx()

    init_colors(stdscr)

    global SELECTED_PERSON
    SELECTED_PERSON = select_user_popup(stdscr, Users_Data, None)

    while True:
        draw_screen(stdscr, MENU_ITEMS, MENU_DESC, current_idx)
        stdscr.refresh()
        key = stdscr.getch()
        items_len = len(MENU_ITEMS)
        if key == ord("q") or key == ord("Q"):
            break
        elif key == curses.KEY_UP:
            current_idx = (current_idx - 1) % items_len
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % items_len
        elif key == ord("\n") or key == curses.KEY_ENTER:
            BODY_SCR.write("Отчет сгенерирован. Нажмите любую клавишу для возврата в меню.")
            stdscr.refresh()
            key = stdscr.getch()
        elif key == ord("u") or key == ord("U"):
            SELECTED_PERSON = select_user_popup(stdscr, Users_Data, SELECTED_PERSON.user_id)

    curses.endwin()


def generate_report_for_item(item_name):
    pass


def main():

    global Nutrition_Data, Users_Data
    Users_Data, Nutrition_Data = load_data("data/nutrition_data.csv")
    curses.wrapper(main_curses)


if __name__ == "__main__":
    main()
