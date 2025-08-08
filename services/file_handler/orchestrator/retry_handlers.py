from ..file_operation_contracts import IRetryExecutor, FileOperationResult, IErrorHandler, IFileValidator


class RetryExecutor:
    def __init__(self, error_handler: IErrorHandler, file_validator: IFileValidator):
        self.error_handler = error_handler
        self.file_validator = file_validator
    
    def execute_with_retry(self, operation_func, file_path: str, operation_name: str) -> FileOperationResult:
        current_path = file_path
        
        while True:
            try:
                self.file_validator.validate_file_operation(current_path)
                result = operation_func()
                return FileOperationResult(success=True, data=result)
                
            except Exception as e:
                current_path = self.error_handler.handle_error(e, current_path, operation_name)
                if not current_path:
                    return FileOperationResult(success=False, error_message="Operation cancelled by user")


class NoRetryExecutor:
    def __init__(self, file_validator: IFileValidator):
        self.file_validator = file_validator
    
    def execute_with_retry(self, operation_func, file_path: str, operation_name: str) -> FileOperationResult:
        try:
            self.file_validator.validate_file_operation(file_path)
            result = operation_func()
            return FileOperationResult(success=True, data=result)
            
        except Exception as e:
            return FileOperationResult(success=False, error_message=str(e)) 