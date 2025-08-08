import pandas as pd
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from services.user_interaction.interaction import UserInteraction

from ..file_operation_contracts import IErrorHandler


class StandardErrorHandler:
    def __init__(self, user_interaction: 'UserInteraction'):
        self.user_interaction = user_interaction
    
    def handle_error(self, error: Exception, file_path: str, operation: str) -> str:
        if isinstance(error, (pd.errors.EmptyDataError, pd.errors.ParserError, ValueError)):
            message = f"File is empty, corrupted, or unreadable. {error}"
        elif isinstance(error, (PermissionError, OSError)):
            message = f"File is open in another application, locked, or permission denied. {error}"
        else:
            message = f"Unexpected error during {operation}: {error}"
        
        print(f"\n[ERROR] Could not {operation} file '{file_path}': {message}")
        return self.user_interaction.get_valid_file_path(
            f"Please enter a new {'output ' if 'write' in operation else ''}file path (or type 'exit' to quit)"
        )


class SilentErrorHandler:
    def __init__(self, logger=None):
        self.logger = logger or print
    
    def handle_error(self, error: Exception, file_path: str, operation: str) -> str:
        self.logger(f"Error during {operation} of '{file_path}': {error}")
        return None


class RetryErrorHandler:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self._retry_count = 0
    
    def handle_error(self, error: Exception, file_path: str, operation: str) -> str:
        if self._retry_count < self.max_retries:
            self._retry_count += 1
            delay = self.base_delay * (2 ** (self._retry_count - 1))
            print(f"Retrying {operation} in {delay} seconds... (attempt {self._retry_count}/{self.max_retries})")
            import time
            time.sleep(delay)
            return file_path
        else:
            print(f"Max retries ({self.max_retries}) exceeded for {operation} of '{file_path}'")
            return None 