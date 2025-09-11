"""
Join analysis module for detailed join key mismatch analysis.
Provides comprehensive analysis of join key mismatches and failure patterns.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from validation.contracts.join_analysis_contracts import (
    IFailurePatternDetector,
    IKeyAnalyzer,
    IMismatchRowCreator,
    IJoinAnalysisGenerator,
    IJoinAnalysisConfigValidator,
    IJoinAnalysisConfigExtractor,
    IJoinAnalysisResultValidator,
    MatchStatus,
    SeverityLevel,
    MismatchData
)
from validation.exceptions import DataValidationError


class CaseSensitivityDetector(IFailurePatternDetector):
    """Detects case sensitivity mismatches."""
    
    def detect(self, file1_value: str, file2_value: str) -> bool:
        return file1_value.lower() == file2_value.lower() and file1_value != file2_value
    
    def get_pattern_name(self) -> str:
        return "case_sensitivity"


class WhitespaceDetector(IFailurePatternDetector):
    """Detects whitespace-related mismatches."""
    
    def detect(self, file1_value: str, file2_value: str) -> bool:
        return file1_value.strip() == file2_value.strip() and file1_value != file2_value
    
    def get_pattern_name(self) -> str:
        return "whitespace"


class DataTypeMismatchDetector(IFailurePatternDetector):
    """Detects data type mismatches."""
    
    def detect(self, file1_value: str, file2_value: str) -> bool:
        try:
            float(file1_value)
            float(file2_value)
            return str(float(file1_value)) == str(float(file2_value)) and file1_value != file2_value
        except (ValueError, TypeError):
            return False
    
    def get_pattern_name(self) -> str:
        return "data_type_mismatch"


class ValueMismatchDetector(IFailurePatternDetector):
    """Detects general value mismatches."""
    
    def detect(self, file1_value: str, file2_value: str) -> bool:
        return file1_value != file2_value
    
    def get_pattern_name(self) -> str:
        return "value_mismatch"


class MissingValuesDetector(IFailurePatternDetector):
    """Detects missing value patterns."""
    
    def detect(self, file1_value: str, file2_value: str) -> bool:
        return file1_value in ['NULL', 'null', 'None', 'N/A', 'n/a', ''] or \
               file2_value in ['NULL', 'null', 'None', 'N/A', 'n/a', '']
    
    def get_pattern_name(self) -> str:
        return "missing_values"


class FailurePatternFactory:
    """Factory for creating failure pattern detectors."""
    
    @staticmethod
    def create_detectors() -> Dict[str, IFailurePatternDetector]:
        return {
            'case_sensitivity': CaseSensitivityDetector(),
            'whitespace': WhitespaceDetector(),
            'data_type_mismatch': DataTypeMismatchDetector(),
            'value_mismatch': ValueMismatchDetector(),
            'missing_values': MissingValuesDetector()
        }


class KeyAnalyzer(IKeyAnalyzer):
    """Analyzes join keys and detects mismatches."""
    
    def __init__(self, failure_detectors: Optional[Dict[str, IFailurePatternDetector]] = None):
        self.failure_detectors = failure_detectors or FailurePatternFactory.create_detectors()
    
    def analyze_key(self, df: pd.DataFrame, key_name: str, file1_col: str, file2_col: str) -> Dict[str, Any]:
        if file1_col not in df.columns or file2_col not in df.columns:
            return {'mismatch_data': [], 'analysis': 'Columns not found', 'patterns': []}
        
        # Extract the base column names (remove _file1 and _file2 suffixes)
        file1_base = file1_col.replace('_file1', '')
        file2_base = file2_col.replace('_file2', '')
        comparison_col = f"{file1_base}_vs_{file2_base}_comparison"
        
        if comparison_col not in df.columns:
            return {'mismatch_data': [], 'analysis': 'Comparison column not found', 'patterns': []}
        
        mismatched = df[df[comparison_col] == 'no match']
        
        if mismatched.empty:
            file1_unique_values = set(df[file1_col].dropna().astype(str))
            file2_unique_values = set(df[file2_col].dropna().astype(str))
            
            if file1_unique_values == file2_unique_values:
                return {'mismatch_data': [], 'analysis': 'Perfect match detected', 'patterns': []}
            else:
                only_file1 = len(df[(df[file1_col].notna()) & (df[file2_col].isna())])
                only_file2 = len(df[(df[file1_col].isna()) & (df[file2_col].notna())])
                
                if only_file1 > 0 or only_file2 > 0:
                    return {'mismatch_data': [], 'analysis': 'Missing data detected', 'patterns': []}
                else:
                    return {'mismatch_data': [], 'analysis': 'No issues detected', 'patterns': []}
        
        mismatch_data = self._group_mismatches(mismatched, file1_col, file2_col)
        patterns = self._detect_failure_patterns(mismatch_data)
        
        return {
            'mismatch_data': mismatch_data,
            'analysis': f'Found {len(mismatch_data)} unique mismatch patterns',
            'patterns': patterns
        }
    
    def _group_mismatches(self, mismatched: pd.DataFrame, file1_col: str, file2_col: str) -> List[MismatchData]:
        mismatch_groups = {}
        
        for idx, row in mismatched.iterrows():
            val1 = str(row[file1_col]) if pd.notna(row[file1_col]) else 'NULL'
            val2 = str(row[file2_col]) if pd.notna(row[file2_col]) else 'NULL'
            key = (val1, val2)
            
            if key not in mismatch_groups:
                mismatch_groups[key] = MismatchData(
                    file1_value=val1,
                    file2_value=val2,
                    count=0,
                    rows=[]
                )
            
            mismatch_groups[key].count += 1
            mismatch_groups[key].rows.append(idx)
        
        return list(mismatch_groups.values())
    
    def _detect_failure_patterns(self, mismatch_data: List[MismatchData]) -> List[str]:
        patterns = []
        
        for data in mismatch_data:
            for detector in self.failure_detectors.values():
                if detector.detect(data.file1_value, data.file2_value):
                    pattern_name = detector.get_pattern_name()
                    if pattern_name not in patterns:
                        patterns.append(pattern_name)
        
        return patterns


class MismatchRowCreator(IMismatchRowCreator):
    """Creates detailed mismatch rows for analysis."""
    
    def create_mismatch_rows(self, mismatch_data: List[MismatchData], left_key_name: str, right_key_name: str, file1_col: str, file2_col: str) -> List[Dict[str, Any]]:
        detailed_rows = []
        
        for data in mismatch_data:
            detailed_row = {
                'File1_Key_Name': left_key_name,
                'File2_Key_Name': right_key_name,
                'Join_Status': MatchStatus.MISMATCH_DETAIL.value,
                'Match_Level': '1 Key Mismatch',
                'Key_Status': f"{left_key_name}_vs_{right_key_name}_Mismatch",
                'Issue_Type': 'value_mismatch',
                'Mismatched_File1_Value': data.file1_value,
                'Mismatched_File2_Value': data.file2_value,
                'Mismatch_Count': f"{data.count} mismatches found"
            }
            detailed_rows.append(detailed_row)
        
        return detailed_rows


class JoinAnalysisConfigValidator(IJoinAnalysisConfigValidator):
    """Validates join analysis configuration."""
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        detailed_join_analysis = config.get('detailed_join_analysis', 'no')
        if not isinstance(detailed_join_analysis, str):
            raise DataValidationError("detailed_join_analysis must be a string")
        
        if detailed_join_analysis.lower() not in ['yes', 'no']:
            raise DataValidationError("detailed_join_analysis must be 'yes' or 'no'")


class JoinAnalysisConfigExtractor(IJoinAnalysisConfigExtractor):
    """Extracts join analysis configuration."""
    
    def extract_join_analysis_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'detailed_join_analysis': config.get('detailed_join_analysis', 'no'),
            'join_keys': config.get('join_keys', {}),
            'output_path': config.get('output_path', ''),
            'output_sheet': config.get('output_sheet', 'ValidationSummaryKeys')
        }


class JoinAnalysisResultValidator(IJoinAnalysisResultValidator):
    """Validates join analysis results."""
    
    def validate_result(self, result_df: pd.DataFrame) -> None:
        if result_df.empty:
            return
        
        required_columns = [
            'File1_Key_Name', 'File2_Key_Name', 'Join_Status', 
            'Match_Level', 'Key_Status', 'Issue_Type',
            'Mismatched_File1_Value', 'Mismatched_File2_Value', 'Mismatch_Count'
        ]
        
        missing_columns = [col for col in required_columns if col not in result_df.columns]
        if missing_columns:
            raise DataValidationError(f"Missing required columns in join analysis result: {missing_columns}")


class JoinAnalysisGenerator(IJoinAnalysisGenerator):
    """Generates detailed join analysis focusing on mismatches."""
    
    def __init__(self):
        self.key_analyzer = KeyAnalyzer()
        self.mismatch_creator = MismatchRowCreator()
        self.config_validator = JoinAnalysisConfigValidator()
        self.config_extractor = JoinAnalysisConfigExtractor()
        self.result_validator = JoinAnalysisResultValidator()
    
    def generate_join_analysis(self, validation_df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            self.config_validator.validate_configuration(config)
            join_analysis_config = self.config_extractor.extract_join_analysis_config(config)
            
            if join_analysis_config['detailed_join_analysis'].lower() != 'yes':
                return pd.DataFrame()
            
            # Extract join keys using the same logic as the data joiner
            from validation.data_joiner import JoinKeyExtractor
            key_extractor = JoinKeyExtractor()
            left_keys, right_keys = key_extractor.extract_join_keys(config)
            
            analysis_rows = []
            
            # Find matching column pairs in the validation DataFrame
            file1_cols = [col for col in validation_df.columns if col.endswith('_file1')]
            file2_cols = [col for col in validation_df.columns if col.endswith('_file2')]
            
            for i, (left_key, right_key) in enumerate(zip(left_keys, right_keys)):
                # Find the corresponding suffixed columns
                file1_col = None
                file2_col = None
                
                # Look for columns that start with the original key names
                for col in file1_cols:
                    if col.startswith(left_key) and col.endswith('_file1'):
                        file1_col = col
                        break
                
                for col in file2_cols:
                    if col.startswith(right_key) and col.endswith('_file2'):
                        file2_col = col
                        break
                
                if not file1_col or not file2_col:
                    continue
                
                # Use the original key names for analysis (needed for comparison column lookup)
                key_analysis = self.key_analyzer.analyze_key(validation_df, left_key, file1_col, file2_col)
                
                if key_analysis['mismatch_data']:
                    mismatch_rows = self.mismatch_creator.create_mismatch_rows(
                        key_analysis['mismatch_data'], left_key, right_key, file1_col, file2_col
                    )
                    analysis_rows.extend(mismatch_rows)
            
            result_df = pd.DataFrame(analysis_rows) if analysis_rows else pd.DataFrame()
            self.result_validator.validate_result(result_df)
            
            return result_df
            
        except Exception as e:
            raise DataValidationError(f"Failed to generate join analysis: {str(e)}")
