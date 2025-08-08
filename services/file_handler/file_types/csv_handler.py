from ..file_operation_contracts import FileTypeStrategy, FileReader, FileWriter
from readers.csv_reader import CSVReader
from writers.csv_writer import CSVFileWriter


class CSVHandler(FileTypeStrategy):
    def get_reader(self) -> FileReader:
        return CSVReader()
    
    def get_writer(self) -> FileWriter:
        return CSVFileWriter()
    
    def supports_sheets(self) -> bool:
        return False 