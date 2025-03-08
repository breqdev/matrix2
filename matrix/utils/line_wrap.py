MAX_WIDTH = 12


def line_wrap(text: str, max_width: int = MAX_WIDTH) -> list[str]:
    lines = []
    line = ""
    for word in text.split():
        if len(line) + len(word) + 1 <= max_width:
            if line:
                line += " "
            line += word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines
