from ..file_operation_contracts import FileTypeStrategy, FileReader, FileWriter
from readers.json_reader import JSONReader
from writers.json_writer import JSONFileWriter


class JSONHandler(FileTypeStrategy):
    
    def get_reader(self) -> FileReader:
        return JSONReader()
    
    def get_writer(self) -> FileWriter:
        return JSONFileWriter()
    
    def supports_sheets(self) -> bool:
        return False
