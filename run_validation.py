import os
import sys
import json
import argparse
import time
from typing import Dict, Any

from validation.dependency_container import get_pipeline_orchestrator
from validation.pipeline_orchestrator import PipelineResult
from services.user_interaction.console import ConsoleUserInputProvider
from services.user_interaction.interaction import UserInteraction
from services.logging.logger_service import LoggerService
from config_ops.sample_configuration import get_sample_configuration
from constants import (
    PIPELINE_HEADER, PIPELINE_BORDER_WIDTH, SAMPLE_CONFIG_HEADER, 
    SAMPLE_CONFIG_BORDER_WIDTH, SAMPLE_CONFIG_FOOTER, INTERACTIVE_MODE_HEADER,
    INTERACTIVE_MODE_BORDER_WIDTH, EXIT_MESSAGE, CONFIG_FILE_NOT_FOUND,
    VALIDATION_ERROR, LOG_LEVEL_ENV, LOG_DIR_ENV, DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_DIR, EXIT_SUCCESS, EXIT_ERROR, HELP_DESCRIPTION, HELP_EXAMPLES
)


def run_validation_pipeline(config_path: str) -> PipelineResult:
    logger = LoggerService("main_pipeline")
    start_time = time.time()
    
    try:
        print("=" * PIPELINE_BORDER_WIDTH)
        print(PIPELINE_HEADER)
        print("=" * PIPELINE_BORDER_WIDTH)
        
        LoggerService.log_session_start(config_path)
        logger.log_operation_start("validation_pipeline", {"config_path": config_path})
        
        with logger.performance_context("pipeline_execution"):
            orchestrator = get_pipeline_orchestrator()
            result = orchestrator.execute_pipeline(config_path)
        
        if result.success:
            config = result.execution_summary.get('config', {})
            orchestrator.print_pipeline_summary(result, config)
            
            execution_duration = time.time() - start_time
            logger.log_operation_success("validation_pipeline", execution_duration)
            LoggerService.log_session_end(True, execution_duration)
        else:
            execution_duration = time.time() - start_time
            logger.log_operation_failure("validation_pipeline", Exception(result.error_message))
            LoggerService.log_session_end(False, execution_duration)
        
        return result
        
    except Exception as e:
        execution_duration = time.time() - start_time
        logger.critical(f"Critical error during validation pipeline", e)
        LoggerService.log_session_end(False, execution_duration)
        
        print(f"\n❌ {VALIDATION_ERROR} {e}")
        return PipelineResult(
            success=False,
            error_message=str(e)
        )


def main():
    LoggerService.setup_application_logging(
        log_level=os.getenv(LOG_LEVEL_ENV, DEFAULT_LOG_LEVEL),
        log_dir=os.getenv(LOG_DIR_ENV, DEFAULT_LOG_DIR),
        enable_console=True
    )
    
    parser = argparse.ArgumentParser(
        description=HELP_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=HELP_EXAMPLES
    )
    
    parser.add_argument(
        '--config', 
        help='Path to configuration JSON file'
    )
    
    parser.add_argument(
        '--sample-config', 
        action='store_true',
        help='Display sample configuration format'
    )
    
    parser.add_argument(
        '--interactive', 
        action='store_true',
        help='Run in interactive mode (default when no arguments provided)'
    )
    
    args = parser.parse_args()
    
    if args.sample_config:
        print(SAMPLE_CONFIG_HEADER)
        print("=" * SAMPLE_CONFIG_BORDER_WIDTH)
        print(json.dumps(get_sample_configuration(), indent=2))
        print(f"\n{SAMPLE_CONFIG_FOOTER}")
        return
    
    if not args.config:
        print(INTERACTIVE_MODE_HEADER)
        print("=" * INTERACTIVE_MODE_BORDER_WIDTH)
        
        user_interaction = UserInteraction(ConsoleUserInputProvider())
        result = user_interaction.get_input_files()
        
        if not result or not result[0]:
            print(EXIT_MESSAGE)
            sys.exit(EXIT_SUCCESS)
        
        config_file = result[0]
        
        if not os.path.exists(config_file):
            print(f"❌ {CONFIG_FILE_NOT_FOUND} {config_file}")
            sys.exit(EXIT_ERROR)
        
        result = run_validation_pipeline(config_file)
        if not result.success:
            sys.exit(EXIT_ERROR)
    else:
        if not os.path.exists(args.config):
            print(f"❌ {CONFIG_FILE_NOT_FOUND} {args.config}")
            sys.exit(EXIT_ERROR)
        
        result = run_validation_pipeline(args.config)
        if not result.success:
            sys.exit(EXIT_ERROR)


if __name__ == '__main__':
    main() 