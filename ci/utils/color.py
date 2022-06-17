import colorama

colorama.init()

# Foreground colors
FORES = {
    "black": colorama.Fore.BLACK,
    "red": colorama.Fore.RED,
    "green": colorama.Fore.GREEN,
    "yellow": colorama.Fore.YELLOW,
    "blue": colorama.Fore.BLUE,
    "magenta": colorama.Fore.MAGENTA,
    "cyan": colorama.Fore.CYAN,
    "white": colorama.Fore.WHITE,
}

# Background colors
BACKS = {
    "black": colorama.Back.BLACK,
    "red": colorama.Back.RED,
    "green": colorama.Back.GREEN,
    "yellow": colorama.Back.YELLOW,
    "blue": colorama.Back.BLUE,
    "magenta": colorama.Back.MAGENTA,
    "cyan": colorama.Back.CYAN,
    "white": colorama.Back.WHITE,
}

# Stylizing options
BRIGHTNESS = {
    "dim": colorama.Style.DIM,
    "normal": colorama.Style.NORMAL,
    "bright": colorama.Style.BRIGHT,
}


def color_string(content, color, brightness=BRIGHTNESS["normal"]) -> None:
    return f"{brightness}{color}{content}{colorama.Style.RESET_ALL}"
