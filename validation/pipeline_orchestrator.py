from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
from dataclasses import dataclass

from validation.exceptions import PipelineExecutionError, InvalidConfigurationError, FileNotFoundError
from validation.data_preparer import IDataPreparer
from validation.data_joiner import IDataJoiner
from validation.data_aggregator import IAggregator
from validation.data_comparer import IDataComparer
from validation.output_writer import IOutputWriter
from validation.join_analysis import JoinAnalysisGenerator, JoinAnalysisOutputHandler
from config_ops import IConfigurationService
from services.logging import get_logger


@dataclass
class PipelineResult:
    success: bool
    final_dataframe: Optional[pd.DataFrame] = None
    error_message: Optional[str] = None
    execution_summary: Optional[Dict[str, Any]] = None


class IPipelineOrchestrator(ABC):
    @abstractmethod
    def execute_pipeline(self, config_path: str) -> PipelineResult:
        pass


class ValidationPipelineOrchestrator(IPipelineOrchestrator):
    """
    Orchestrates the data validation pipeline execution.
    Coordinates all pipeline stages: preparation, aggregation, joining, comparison, and output.
    """
    
    def __init__(
        self,
        data_preparer: IDataPreparer,
        data_joiner: IDataJoiner,
        data_aggregator: IAggregator,
        data_comparer: IDataComparer,
        output_writer: IOutputWriter,
        config_processor: IConfigurationService
    ):
        self._data_preparer = data_preparer
        self._data_joiner = data_joiner
        self._data_aggregator = data_aggregator
        self._data_comparer = data_comparer
        self._output_writer = output_writer
        self._config_processor = config_processor
        self._join_analysis_generator = JoinAnalysisGenerator()
        self._join_analysis_output_handler = JoinAnalysisOutputHandler()
        self._logger = get_logger(self.__class__.__name__)
    
    def execute_pipeline(self, config_path: str) -> PipelineResult:
        """
        Execute the complete data validation pipeline.
        
        Args:
            config_path: Path to the configuration file
        
        Returns:
            PipelineResult containing success status, final dataframe, and execution summary
        """
        try:
            execution_summary = {}
            
            self._logger.info("Starting pipeline execution")
            self._logger.info("Processing configuration...")
            config = self._config_processor.process_configuration(config_path)
            execution_summary['config_processed'] = True
            execution_summary['config'] = config
            self._logger.info("Configuration processing successful")
            
            self._logger.info("Preparing data frames...")
            df1, df2 = self._data_preparer.prepare_data_frames(config)
            execution_summary['data_prepared'] = True
            execution_summary['df1_shape'] = df1.shape
            execution_summary['df2_shape'] = df2.shape
            self._logger.info(f"Data preparation successful - df1: {df1.shape}, df2: {df2.shape}")
            
            self._logger.info("Join key types detection completed during data preparation")
            execution_summary['join_key_types_detected'] = True
            execution_summary['detected_types'] = {}
            
            self._logger.info("Applying file1 aggregation...")
            df1 = self._data_aggregator.apply_file1_aggregation(df1, config)
            execution_summary['file1_aggregated'] = True
            execution_summary['df1_shape_after_agg'] = df1.shape
            self._logger.info(f"File1 aggregation completed - shape: {df1.shape}")
            
            self._logger.info("Applying file2 aggregation...")
            df2 = self._data_aggregator.apply_file2_aggregation(df2, config)
            execution_summary['file2_aggregated'] = True
            execution_summary['df2_shape_after_agg'] = df2.shape
            self._logger.info(f"File2 aggregation completed - shape: {df2.shape}")
            
            self._logger.info("Joining data frames...")
            joined_df = self._data_joiner.join_dataframes(df1, df2, config)
            execution_summary['data_joined'] = True
            execution_summary['joined_df_shape'] = joined_df.shape
            self._logger.info(f"Data joining successful - shape: {joined_df.shape}")
            
            self._logger.info("Applying final aggregation...")
            aggregated_df = self._data_aggregator.apply_final_aggregation(joined_df, config)
            execution_summary['data_aggregated'] = True
            execution_summary['aggregated_df_shape'] = aggregated_df.shape
            self._logger.info(f"Final aggregation successful - shape: {aggregated_df.shape}")
            
            self._logger.info("Applying comparison...")
            compared_df = self._data_comparer.compare_mapped_columns(aggregated_df, config)
            execution_summary['data_compared'] = True
            execution_summary['compared_df_shape'] = compared_df.shape
            self._logger.info(f"Data comparison successful - shape: {compared_df.shape}")
            
            self._logger.info("Writing output file...")
            self._output_writer.write_output(compared_df, config)
            execution_summary['output_written'] = True
            self._logger.info("Output file written successfully")
            
            self._logger.info("Generating join analysis...")
            join_analysis_df = self._join_analysis_generator.generate_join_analysis(compared_df, config)
            if not join_analysis_df.empty:
                output_settings = {
                    'output_path': config.get('output_path', ''),
                    'output_sheet': config.get('output_sheet', 'ValidationSummary')
                }
                self._join_analysis_output_handler.handle_join_analysis_output(join_analysis_df, output_settings)
                execution_summary['join_analysis_generated'] = True
                execution_summary['join_analysis_shape'] = join_analysis_df.shape
                self._logger.info(f"Join analysis completed - {len(join_analysis_df)} records")
            else:
                execution_summary['join_analysis_generated'] = False
                self._logger.info("No join analysis required")
            
            execution_summary['final_shape'] = compared_df.shape
            execution_summary['comparison_columns'] = [
                col for col in compared_df.columns if 'diff' in col or 'delta' in col
            ]
            
            self._logger.info("Pipeline execution completed successfully")
            return PipelineResult(
                success=True,
                final_dataframe=compared_df,
                execution_summary=execution_summary
            )
            
        except (PipelineExecutionError, FileNotFoundError, InvalidConfigurationError) as e:
            error_msg = f"Pipeline execution failed: {str(e)}"
            self._logger.error(error_msg, exception=e)
            return PipelineResult(
                success=False,
                error_message=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error during pipeline execution: {str(e)}"
            self._logger.error(error_msg, exception=e)
            return PipelineResult(
                success=False,
                error_message=error_msg
            )
    
    def print_pipeline_summary(self, result: PipelineResult, config: Dict[str, Any]) -> None:
        """
        Print a summary of the pipeline execution results.
        
        Args:
            result: The pipeline execution result
            config: The configuration dictionary
        """
        if not result.success:
            return
        
        self._logger.info("=" * 80)
        self._logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        self._logger.info("=" * 80)
        self._logger.info(f"Final Results:")
        self._logger.info(f"  Input files: {config.get('file1_path')}, {config.get('file2_path', 'N/A')}")
        self._logger.info(f"  Output file: {config.get('output_path')}")
        if result.final_dataframe is not None:
            self._logger.info(f"  Final dataframe: {result.final_dataframe.shape[0]} rows × {result.final_dataframe.shape[1]} columns")
        
        comparison_cols = result.execution_summary.get('comparison_columns', []) if result.execution_summary else []
        self._logger.info(f"  Comparison columns: {len(comparison_cols)}")
        self._logger.info("Data validation completed successfully!") 