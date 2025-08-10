from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
from dataclasses import dataclass

from validation.exceptions import PipelineExecutionError
from validation.data_preparer import IDataPreparer
from validation.data_joiner import IDataJoiner
from validation.data_aggregator import IAggregator
from validation.data_comparer import IDataComparer
from validation.output_writer import IOutputWriter
from config_ops import IConfigurationService


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
    
    def execute_pipeline(self, config_path: str) -> PipelineResult:
        try:
            execution_summary = {}
            
            print("\n1. Processing configuration...")
            config = self._config_processor.process_configuration(config_path)
            execution_summary['config_processed'] = True
            execution_summary['config'] = config
            print(f"✓ Configuration processing successful!")
            
            print("\n2. Preparing data frames...")
            df1, df2 = self._data_preparer.prepare_data_frames(config)
            execution_summary['data_prepared'] = True
            execution_summary['df1_shape'] = df1.shape
            execution_summary['df2_shape'] = df2.shape
            print(f"✓ Data preparation successful!")
            print(f"  df1 shape: {df1.shape}")
            print(f"  df2 shape: {df2.shape}")
            
            print("\n2.5. Detecting join key types...")
            print("✓ Join key types detection completed during data preparation")
            execution_summary['join_key_types_detected'] = True
            execution_summary['detected_types'] = {}
            print(f"✓ Join key type detection completed!")
            
            print("\n3. Joining data frames...")
            joined_df = self._data_joiner.join_dataframes(df1, df2, config)
            execution_summary['data_joined'] = True
            execution_summary['joined_df_shape'] = joined_df.shape
            print(f"✓ Data joining successful!")
            print(f"  Joined df shape: {joined_df.shape}")
            
            print("\n4. Applying aggregation...")
            aggregated_df = self._data_aggregator.apply_aggregation(joined_df, config)
            execution_summary['data_aggregated'] = True
            execution_summary['aggregated_df_shape'] = aggregated_df.shape
            print(f"✓ Data aggregation successful!")
            print(f"  Aggregated df shape: {aggregated_df.shape}")
            
            print("\n5. Applying comparison...")
            compared_df = self._data_comparer.compare_mapped_columns(aggregated_df, config)
            execution_summary['data_compared'] = True
            execution_summary['compared_df_shape'] = compared_df.shape
            print(f"✓ Data comparison successful!")
            print(f"  Compared df shape: {compared_df.shape}")
            
            print("\n6. Writing output file...")
            self._output_writer.write_output(compared_df, config)
            execution_summary['output_written'] = True
            print(f"✓ Output writing successful!")
            
            execution_summary['final_shape'] = compared_df.shape
            execution_summary['comparison_columns'] = [
                col for col in compared_df.columns if 'diff' in col or 'delta' in col
            ]
            
            return PipelineResult(
                success=True,
                final_dataframe=compared_df,
                execution_summary=execution_summary
            )
            
        except Exception as e:
            error_msg = f"Pipeline execution failed: {str(e)}"
            print(f"\n❌ {error_msg}")
            return PipelineResult(
                success=False,
                error_message=error_msg
            )
    
    def print_pipeline_summary(self, result: PipelineResult, config: Dict[str, Any]) -> None:
        if not result.success:
            return
        
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"📊 Final Results:")
        print(f"  Input files: {config.get('file1_path')}, {config.get('file2_path', 'N/A')}")
        print(f"  Output file: {config.get('output_path')}")
        print(f"  Final dataframe: {result.final_dataframe.shape[0]} rows × {result.final_dataframe.shape[1]} columns")
        
        comparison_cols = result.execution_summary.get('comparison_columns', [])
        print(f"  Comparison columns: {len(comparison_cols)}")
        
        print(f"\n✅ Data validation completed successfully!") 