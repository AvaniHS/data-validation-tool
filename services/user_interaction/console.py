from .base import UserInputProvider

class ConsoleUserInputProvider(UserInputProvider):
    def get_input(self, prompt, required=True, default=None):
        while True:
            value = input(f"{prompt}{' (default: '+default+')' if default else ''}: ")
            if value:
                return value
            if default is not None:
                return default
            if not required:
                return None
            print("This field is required.") 