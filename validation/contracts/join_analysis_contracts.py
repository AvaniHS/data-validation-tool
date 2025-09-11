"""
Contracts for join analysis functionality.
Defines interfaces for detailed join analysis and mismatch detection.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
from dataclasses import dataclass
from enum import Enum


class MatchStatus(Enum):
    PERFECT_MATCH = "perfect_match"
    MISMATCH_DETAIL = "mismatch_detail"
    NO_ISSUES = "no_issues"


class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MismatchData:
    file1_value: str
    file2_value: str
    count: int
    rows: List[int]


class IFailurePatternDetector(ABC):
    """Interface for detecting specific failure patterns in data mismatches."""
    
    @abstractmethod
    def detect(self, file1_value: str, file2_value: str) -> bool:
        """Detect if the mismatch follows this specific pattern."""
        pass
    
    @abstractmethod
    def get_pattern_name(self) -> str:
        """Get the name of the failure pattern."""
        pass


class IKeyAnalyzer(ABC):
    """Interface for analyzing join keys and detecting mismatches."""
    
    @abstractmethod
    def analyze_key(self, df: pd.DataFrame, key_name: str, file1_col: str, file2_col: str) -> Dict[str, Any]:
        """Analyze a specific join key for mismatches and patterns."""
        pass


class IMismatchRowCreator(ABC):
    """Interface for creating detailed mismatch rows."""
    
    @abstractmethod
    def create_mismatch_rows(self, mismatch_data: List[MismatchData], left_key_name: str, right_key_name: str, file1_col: str, file2_col: str) -> List[Dict[str, Any]]:
        """Create detailed mismatch rows from mismatch data."""
        pass


class IJoinAnalysisGenerator(ABC):
    """Interface for generating detailed join analysis."""
    
    @abstractmethod
    def generate_join_analysis(self, validation_df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Generate detailed join analysis focusing on mismatches."""
        pass


class IJoinAnalysisConfigValidator(ABC):
    """Interface for validating join analysis configuration."""
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate join analysis configuration parameters."""
        pass


class IJoinAnalysisConfigExtractor(ABC):
    """Interface for extracting join analysis configuration."""
    
    @abstractmethod
    def extract_join_analysis_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract join analysis specific configuration."""
        pass


class IJoinAnalysisResultValidator(ABC):
    """Interface for validating join analysis results."""
    
    @abstractmethod
    def validate_result(self, result_df: pd.DataFrame) -> None:
        """Validate join analysis result dataframe."""
        pass
