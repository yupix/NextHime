class Color:
    def __init__(self):
        self.pink = "\x1B[38;5;225m"
        self.white = "\x1B[38;5;15]"

    def custom(self, code: str = None) -> str:
        return f"\x1B[38;5;{code}m"
