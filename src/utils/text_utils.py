def wrap_text(text: str, width: int) -> list:
    """
    Разбивает длинный текст на строки заданной ширины.

    Аргументы:
        text (str): Исходный текст.
        width (int): Максимальная длина строки.

    Возвращает:
        list[str]: Список строк, укладывающихся в заданную ширину.
    """
    if not text:
        return [""]

    if len(text) <= width:
        return [text]

    words = text.split()
    if not words:
        return [""]

    lines = []
    current_line = []
    current_len = 0
        
    for word in words:
        extra_space = 1 if current_line else 0
        if current_len + len(word) + extra_space <= width:
            current_line.append(word)
            current_len += len(word) + extra_space
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines
