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

    def write(self, text: str, indent: int = 0, color: int = 0):
        try:
            if self.y >= self.height - 1:
                return False

            if not text or not text.strip():
                return True

            if len(text) > self.width - self.x - 1 - indent:
                text = text[: self.width - 1 - indent]

            if color > 0 and color not in colors_init:                
                curses.init_pair(color + 1, color, -1)
                colors_init.add(color)

            self.stdscr.addstr(self.y, self.x + indent, text, curses.color_pair(color))
            self.y += 1

            return True
        except curses.error:
            return False

    def write_wrapped(self, text, indent=0, color=0):
        lines = wrap_text(text, self.width - indent - 2)
        for line in lines:
            self.write(line, indent, color)

        return True

    def write_separator(self, char="=", color=0):
        separator = char * (self.width - 2)
        self.write(separator, 0, color)
        self.y += 1
        return True


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