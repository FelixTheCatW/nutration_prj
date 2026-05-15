import curses
from core.Person import Person

def select_user_popup(stdscr, persons: list[Person], selected_id) -> Person:    
    max_name_len = max(len(p.name) for p in persons)
    win_width = max_name_len + 6
    height, width = stdscr.getmaxyx()
    win_width = min(win_width, width - 4)
    win_width = max(win_width, 30)
    win_height = len(persons) + 4
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2

    win = curses.newwin(win_height, win_width, start_y, start_x)
    win.keypad(True)
    curses.curs_set(0)
    win.bkgd(" ", curses.color_pair(171))

    current = 0
    list_len = len(persons)
    while True:
        win.clear()
        win.attron(curses.color_pair(171) | curses.A_BOLD)
        title = " Выберите пользователя "
        win.addstr(0, (win_width - len(title)) // 2, title)
        win.addstr(1, 0, "─" * win_width)
        win.attroff(curses.color_pair(171) | curses.A_BOLD)
        win.addstr(list_len + 2, 0, "-" * win_width)
        
        for i, person in enumerate(persons):
            y = i + 2
            if(person.user_id == selected_id):
                name = "★ " + person.name
            else:
                name = "   " + person.name
            if i == current:
                win.addstr(y, 2, name, curses.A_REVERSE)
            else:
                win.addstr(y, 2, name)

        win.refresh()
        key = win.getch()
        if key == curses.KEY_UP:
            current = (current - 1) % list_len           
        elif key == curses.KEY_DOWN:
            current = (current + 1) % list_len
        elif key == ord("\n") or key == curses.KEY_ENTER:
            return persons[current]
        elif key == 27:
            return None
        
    return None