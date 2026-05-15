import curses

from src.utils.text_utils import wrap_text

colors_init: set = set()


class ScreenWriter:
    def __init__(self, stdscr, x, y, width, height):
        self.stdscr = stdscr
        self.height = height
        self.width = width
        self.y = y
        self.x = x

    def new_line(self):
        self.y += 1

    def __write(self, text: str, y, x, color: int = 0):
        try:
            if y >= self.height:
                return False

            if not text or not text.strip():
                return True

            if len(text) > self.width - x - 1:
                text = text[: self.width - 1]

            # if color > 0 and color not in colors_init:
            #     curses.init_pair(color + 1, color, -1)
            #     colors_init.add(color)

            self.stdscr.addstr(y, x, text, curses.color_pair(color))

            return True
        except curses.error:
            return False

    def write(self, text, color=0):
        lines = wrap_text(text, self.width - 2)
        for line in lines:
            self.__write(line, self.y, self.x, color)
            self.y += 1

        return True

    def write_bottom(self, text, color=0):
        lines = wrap_text(text, self.width - 2)
        l_l = len(lines)        
        for line in lines:
            self.__write(line, self.height - l_l, self.x, color)
            l_l -= 1

        return True

    def write_separator(self, char="=", color=0):
        separator = char * (self.width - 2)
        self.write(separator, 0, color)
        self.y += 1
        return True


def select_user_popup(stdscr, users_df):
    """Показывает окно выбора пользователя и возвращает (user_id, name)."""
    height, width = stdscr.getmaxyx()
    win_height = min(len(users_df) + 4, height - 4)
    win_width = min(60, width - 4)
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2
    win = curses.newwin(win_height, win_width, start_y, start_x)
    win.keypad(True)
    curses.curs_set(0)
    win.bkgd(" ", curses.color_pair(171))
    win.box()
    win.addstr(0, 2, " Выберите пользователя ", curses.A_BOLD)

    users = users_df[["user_id", "name"]].to_records(index=False)
    current = 0
    max_display = win_height - 3
    start_idx = 0

    while True:
        win.clear()
        win.box()
        win.addstr(0, 2, " Выберите пользователя ", curses.A_BOLD)
        visible = users[start_idx : start_idx + max_display]
        for i, (uid, name) in enumerate(visible):
            y = i + 2
            if start_idx + i == current:
                win.addstr(y, 2, f" {name} ", curses.A_REVERSE)
            else:
                win.addstr(y, 2, f" {name} ")
        win.refresh()
        key = win.getch()
        if key == curses.KEY_UP:
            if current > 0:
                current -= 1
                if current < start_idx:
                    start_idx = current
        elif key == curses.KEY_DOWN:
            if current < len(users) - 1:
                current += 1
                if current >= start_idx + max_display:
                    start_idx = current - max_display + 1
        elif key == ord("\n") or key == curses.KEY_ENTER:
            uid, name = users[current]
            return uid, name
        elif key == 27:  # ESC
            return None, None
    return None, None


def init_colors(stdscr):
    if not curses.has_colors():
        return

    curses.start_color()
    curses.use_default_colors()

    max_colors = curses.COLORS
    max_pairs = curses.COLOR_PAIRS

    # We can only initialize up to max_pairs - 1 pairs (pair 0 is reserved)
    usable_colors = min(max_colors, max_pairs - 1)

    for i in range(usable_colors):
        # pair numbers: 1 .. usable_colors
        curses.init_pair(i + 1, i, -1)
