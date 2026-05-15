import curses
import textwrap

from cli.menu import MENU_ITEMS, MENU_DESC
from cli.screen_writer import ScreenWriter

TOP_LEFT_SCR: ScreenWriter
TOP_RIGHT_SCR: ScreenWriter
BODY_SCR: ScreenWriter

def draw_screen(stdscr, items, descriptions, current_idx, height, width):
    # stdscr.clear()
    init_screens(stdscr)

    for i, item in enumerate(MENU_ITEMS):
        if i == current_idx:
            TOP_LEFT_SCR.write(f"👉 {item}", 0, 0)
            TOP_RIGHT_SCR.write_wrapped(descriptions[current_idx])
        else:
            TOP_LEFT_SCR.write(f"   {item}", 0, 0)

    stdscr.refresh()


def init_screens(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    height, width = stdscr.getmaxyx()
    list_width = max(30, width // 3) + 5
    desc_width = width - list_width - 2
    header_height = 11
    report_height = height - header_height - 2

    global TOP_LEFT_SCR, TOP_RIGHT_SCR, BODY_SCR
    TOP_LEFT_SCR = ScreenWriter(stdscr, 0, 0, list_width, header_height)
    TOP_RIGHT_SCR = ScreenWriter(stdscr, list_width + 1, 0, desc_width, header_height)
    BODY_SCR = ScreenWriter(stdscr, header_height + 1, 0, width, report_height)

    # Заголовок
    TOP_LEFT_SCR.write("Доступные отчеты".center(list_width), 0, 0)
    TOP_RIGHT_SCR.write("Описание".center(desc_width),0, 0)
    # подвал
    help_msg = "↑/↓ - выбор | Enter - запуск | q: выход"
    stdscr.addstr(height - 1, 0, help_msg, curses.color_pair(48))

def main_curses(stdscr):
    init_screens(stdscr)
    current_idx = 0
    height, width = stdscr.getmaxyx()

    while True:
        draw_screen(stdscr, MENU_ITEMS, MENU_DESC, current_idx, height, width)
        key = stdscr.getch()
        items_len = len(MENU_ITEMS)
        if key == ord('q') or key == ord('Q'):
            break
        elif key == curses.KEY_UP:
            current_idx = (current_idx - 1) % items_len
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % items_len
        elif key == ord('\n') or key == curses.KEY_ENTER:
            BODY_SCR.write_wrapped("Отчет сгенерирован. Нажмите любую клавишу для возврата в меню.")
            stdscr.refresh()
            # stdscr.getch()

    curses.endwin()


def generate_report_for_item(item_name):
    pass


def main():
    curses.wrapper(main_curses)


if __name__ == '__main__':
    main()
