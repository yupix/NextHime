class Color:
    PINK = '\x1B[38;5;225m'

    def __init__(self):
        pass

    def custom(self, code: str = None) -> str:
        return f'\x1B[38;5;{code}m'
