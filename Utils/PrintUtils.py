from colorama import init, Fore, Back, Style

THOUGHT_COLOR = Fore.GREEN
OBSERVATION_COLOR = Fore.YELLOW
ROUND_COLOR = Fore.BLUE


def color_print(text, color=None, end="\n"):
    if color is not None:
        print(color + text + Style.RESET_ALL, end=end, flush=True)
    else:
        print(text, end=end, flush=True)
