#!/usr/bin/env python3
"""
Test runner script to run all tests in the project.
"""

import os
import sys
import unittest

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Run all tests in the project."""
    # Discover and run all tests from unit, integration, and user_interaction directories
    loader = unittest.TestLoader()
    test_dirs = ['unit', 'integration', 'user_interaction']
    suite = unittest.TestSuite()
    
    for test_dir in test_dirs:
        dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), test_dir)
        if os.path.exists(dir_path):
            dir_suite = loader.discover(dir_path, pattern='test_*.py', top_level_dir=os.path.dirname(os.path.abspath(__file__)))
            suite.addTest(dir_suite)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_unit_tests():
    """Run only unit tests."""
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unit')
    suite = loader.discover(start_dir, pattern='test_*.py', top_level_dir=start_dir)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_integration_tests():
    """Run only integration tests."""
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'integration')
    suite = loader.discover(start_dir, pattern='test_*.py', top_level_dir=start_dir)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_user_interaction_tests():
    """Run only user interaction tests."""
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_interaction')
    suite = loader.discover(start_dir, pattern='test_*.py', top_level_dir=start_dir)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run tests for the data validation project')
    parser.add_argument('--type', choices=['all', 'unit', 'integration', 'user'], 
                       default='all', help='Type of tests to run')
    
    args = parser.parse_args()
    
    if args.type == 'all':
        success = run_all_tests()
    elif args.type == 'unit':
        success = run_unit_tests()
    elif args.type == 'integration':
        success = run_integration_tests()
    elif args.type == 'user':
        success = run_user_interaction_tests()
    
    sys.exit(0 if success else 1) 