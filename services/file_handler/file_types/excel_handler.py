from ..file_operation_contracts import FileTypeStrategy, FileReader, FileWriter
from readers.excel_reader import ExcelReader
from writers.excel_writer import ExcelFileWriter


class ExcelHandler(FileTypeStrategy):
    def get_reader(self) -> FileReader:
        return ExcelReader()
    
    def get_writer(self) -> FileWriter:
        return ExcelFileWriter()
    
    def supports_sheets(self) -> bool:
        return True 