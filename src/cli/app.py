import curses
import textwrap

from cli.menu import MENU_ITEMS, MENU_DESC
from cli.screen_writer import ScreenWriter

colors_init: set = set()


def draw_screen(stdscr, items, descriptions, current_idx, start_idx, height, width):
    stdscr.clear()

    # Левая колонка – список (30% ширины)
    list_width = max(30, width // 3) + 5
    desc_width = width - list_width - 2
    header_height = 11
    report_height = height - header_height
    # Заголовок
    TOP_LEFT_SCR.write("Доступные отчеты".center(list_width), 0, 0)
    TOP_RIGHT_SCR.write("Описание".center(desc_width),0, 0)

    max_display = height - 3  # строк под список
    visible_items = items[start_idx:start_idx + max_display]

    for i, item in enumerate(visible_items):
        y = i + 2
        x = 0
        idx = start_idx + i
        if idx == current_idx:
            stdscr.addstr(y, x, f"👉 {item}", curses.A_UNDERLINE)
        else:
            stdscr.addstr(y, x, f"   {item}")

    # Описание текущего пункта
    if 0 <= current_idx < len(descriptions):
        desc = descriptions[current_idx]
        wrapped = textwrap.wrap(desc, width=desc_width)
        for i, line in enumerate(wrapped):
            if i + 2 < height:
                stdscr.addstr(i + 2, list_width + 2, line)

    help_msg = "↑/↓ - выбор | Enter - запуск | q: выход"
    stdscr.addstr(height - 1, 0, help_msg, curses.color_pair(48))
    stdscr.refresh()


TOP_LEFT_SCR: ScreenWriter
TOP_RIGHT_SCR: ScreenWriter
BODY_SCR: ScreenWriter


def init_screens(stdscr):
    global TOP_LEFT_SCR, TOP_RIGHT_SCR, BODY_SCR
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    height, width = stdscr.getmaxyx()
    list_width = max(30, width // 3) + 5
    desc_width = width - list_width - 2
    header_height = 11

    TOP_LEFT_SCR = ScreenWriter(stdscr, 0, 0, list_width, header_height)
    TOP_RIGHT_SCR = ScreenWriter(stdscr, list_width + 1, 0, desc_width, header_height)
    BODY_SCR = ScreenWriter(stdscr, header_height + 1, 0, width, height - header_height - 2)


def main_curses(stdscr):
    init_screens(stdscr)
    current_idx = 0
    start_idx = 0
    height, width = stdscr.getmaxyx()

    while True:
        draw_screen(stdscr, MENU_ITEMS, MENU_DESC, current_idx, start_idx, height, width)
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
            stdscr.getch()

    curses.endwin()


def generate_report_for_item(item_name):
    pass


def main():
    curses.wrapper(main_curses)


if __name__ == '__main__':
    main()
