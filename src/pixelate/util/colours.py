ESC = "\033["

RESET = "0"
NORMAL = "0"
BOLD = "1"
UNDERLINE = "4"

DEFAULT = ""
BLACK = "30"
RED = "31"
GREEN = "32"
YELLOW = "33"
BLUE = "34"
MAGENTA = "35"
CYAN = "36"
WHITE = "37"


class ColourFormat:
    def __init__(self, colour=WHITE, emphasis=RESET):
        self.colour = colour
        self.emphasis = emphasis

    def use(self):
        print(f"{ESC}{self.emphasis};{self.colour}m", end="")


class ColourFormatContext:
    def __init__(self):
        self.stack = []

    def push(self, colour: ColourFormat):
        self.stack.append(colour)
        self.clear_current_colour()
        self.stack[-1].use()

    def pop(self):
        if len(self.stack) == 0:
            self.clear_current_colour()
            return

        self.stack.pop()
        self.clear_current_colour()

        if len(self.stack) > 0:
            self.stack[-1].use()

    def clear(self):
        self.stack.clear()
        self.clear_current_colour()

    def clear_current_colour(self):
        print(f"{ESC}{RESET}m", end="")
