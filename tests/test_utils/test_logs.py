"""
Tests for cannlytics.utils.logs
=================================
Covers: initialize_logs with various configurations.
"""
import logging
import os

import pytest

from cannlytics.utils.logs import initialize_logs

class TestInitializeLogs:

    def test_returns_logger(self):
        logger = initialize_logs('test_logger', log_dir=False)
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger'

    def test_console_only(self):
        logger = initialize_logs('console_test', log_dir=False)
        assert len(logger.handlers) == 1  # Console only.
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_file_logging(self, tmp_path):
        log_dir = str(tmp_path / 'logs')
        logger = initialize_logs('file_test', log_dir=log_dir)
        assert len(logger.handlers) == 2  # Console + file.
        assert os.path.isdir(log_dir)
        log_files = os.listdir(log_dir)
        assert len(log_files) == 1
        assert log_files[0].endswith('.log')

    def test_temp_dir_logging(self):
        logger = initialize_logs('temp_test', use_temp=True, log_dir='ignored')
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1

    def test_default_log_dir_is_none(self):
        """Default should be console-only (no Windows D: path)."""
        logger = initialize_logs('default_test')
        # With default log_dir=None, should only have console handler.
        assert len(logger.handlers) == 1

    def test_custom_prefix(self, tmp_path):
        log_dir = str(tmp_path / 'logs')
        logger = initialize_logs('prefix_test', log_dir=log_dir, prefix='myapp')
        log_files = os.listdir(log_dir)
        assert any('myapp' in f for f in log_files)

    def test_log_level(self):
        logger = initialize_logs('level_test', log_dir=False, level=logging.WARNING)
        assert logger.level == logging.WARNING
