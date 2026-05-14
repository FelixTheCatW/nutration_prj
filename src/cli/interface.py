import curses
from screen_writer import ScreenWriter
def draw_interface(
    stdscr,
    modules: list[dict],
    current_idx: int,
    show_demo: bool,
):
    stdscr.clear()

    height, width = stdscr.getmaxyx()

    sw = ScreenWriter(stdscr)

    names_max_lens = max((len(x["module_name"]) for x in modules), default=10) * 2
    sw.write("Меню".center(width), 0, 48)
    sw.write(("~" * names_max_lens).center(width), 0, 48)

    for i, mod in enumerate(modules):
        name = mod["module_name"]
        if i == current_idx:
            line = f"👉 {name}".center(width - 2)
        else:
            line = f"    {name}".center(width - 2)
        sw.write(line, 0, 81)

    sw.write_separator("=", 244)

    if show_demo:
        demo_path = modules[current_idx]["demo"]
        if demo_path:
            demo_result = run_module_file(demo_path)

            if demo_result["stdout"]:
                sw.write("Сообщения выполнения тестов:", 0, 203)
                original_lines = demo_result["stdout"].splitlines()
                for line in original_lines:
                    if not sw.write_wrapped(line, 2):
                        break

            if demo_result["stderr"]:
                sw.new_line()
                sw.write("Вывод результатов фреймворка unittest:", 0, 203)
                error_lines = demo_result["stderr"].splitlines()
                for line in error_lines:
                    if line:  # Пропускаем совсем пустые, если нужно
                        if not sw.write_wrapped(line, 2):
                            break
    else:
        sw.write("Описание модуля:", 0, 13)
        doc_text = modules[current_idx]["docstring"]
        sw.write_wrapped(doc_text, 2)

        funcs = modules[current_idx]["functions"]
        if funcs:
            sw.write("Функции модуля:", 0, 34)

            for func_name, func_doc in funcs:
                sw.write(f"  📌 {func_name}", 0, 0)

                if func_doc:
                    for line in func_doc.splitlines():
                        sw.write_wrapped(line, 4, 250)

                sw.new_line()

    # --- Footer (подвал) ---
    help_msg = "↑/↓: выбор модуля | Enter: запустить тесты | q: выход"
    stdscr.addstr(height - 1, 0, help_msg, curses.color_pair(48))

    stdscr.refresh()

