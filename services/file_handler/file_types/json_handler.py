from ..file_operation_contracts import FileTypeStrategy, FileReader, FileWriter
from readers.json_reader import JSONReader
from writers.json_writer import JSONFileWriter


class JSONHandler(FileTypeStrategy):
    """Strategy for handling JSON file operations"""
    
    def get_reader(self) -> FileReader:
        """Get JSON file reader"""
        return JSONReader()
    
    def get_writer(self) -> FileWriter:
        """Get JSON file writer"""
        return JSONFileWriter()
    
    def supports_sheets(self) -> bool:
        """JSON files don't support sheets"""
        return False
