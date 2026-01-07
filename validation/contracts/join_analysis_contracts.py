"""
Contracts for join analysis functionality.
Defines interfaces following SOLID principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
from dataclasses import dataclass
from enum import Enum


class JoinAnalysisStatus(Enum):
    """Status of join analysis."""
    MATCH = "match"
    MISMATCH = "mismatch"
    MISSING_LEFT = "missing_left"
    MISSING_RIGHT = "missing_right"


@dataclass
class JoinAnalysisResult:
    """Result of join analysis for a single key pair."""
    left_key: str
    right_key: str
    status: JoinAnalysisStatus
    left_value: Any
    right_value: Any
    mismatch_reason: Optional[str] = None


class IJoinAnalysisConfigValidator(ABC):
    """Interface for validating join analysis configuration."""
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate join analysis configuration."""
        pass


class IJoinAnalysisConfigExtractor(ABC):
    """Interface for extracting join analysis configuration."""
    
    @abstractmethod
    def extract_join_analysis_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract join analysis configuration from main config."""
        pass


class IJoinAnalysisGenerator(ABC):
    """Interface for generating join analysis."""
    
    @abstractmethod
    def generate_join_analysis(self, validation_df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Generate join analysis DataFrame."""
        pass


class IJoinAnalysisResultValidator(ABC):
    """Interface for validating join analysis results."""
    
    @abstractmethod
    def validate_result(self, result_df: pd.DataFrame) -> None:
        """Validate join analysis result."""
        pass


class IJoinAnalysisOutputHandler(ABC):
    """Interface for handling join analysis output."""
    
    @abstractmethod
    def handle_join_analysis_output(self, join_analysis_df: pd.DataFrame, 
                                  output_settings: Dict[str, Any]) -> None:
        """Handle join analysis output based on file type."""
        pass
