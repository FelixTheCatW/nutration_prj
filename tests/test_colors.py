import curses


def test_colors(stdscr):
    if not curses.has_colors():
        stdscr.addstr("Terminal does not support colors.")
        stdscr.refresh()
        stdscr.getch()
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

    # Display each color
    for i in range(usable_colors):
        stdscr.addstr(f"{i:3} ", curses.color_pair(i + 1))
        if (i + 1) % 12 == 0:
            stdscr.addstr("\n")

    stdscr.refresh()
    stdscr.getch()


curses.wrapper(test_colors)
