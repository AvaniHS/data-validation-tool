from validation.exceptions import DataComparisonError
from validation.interfaces.dataframe_validator import IDataFrameValidator


class DataFrameValidator(IDataFrameValidator):
    def validate_dataframe(self, df) -> None:
        if df is None:
            raise DataComparisonError("Input dataframe cannot be None")
        
        if df.empty:
            raise DataComparisonError("Input dataframe is empty")
        
        if len(df.columns) == 0:
            raise DataComparisonError("Input dataframe has no columns")
