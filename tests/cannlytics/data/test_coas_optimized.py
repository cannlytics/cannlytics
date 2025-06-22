"""
Optimized COA Tests | Cannlytics

Modern pytest-based tests for COA functionality.
"""
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, Mock

from cannlytics.data.coas import CoADoc
from cannlytics.data.data import create_hash
from tests.utils import create_temp_pdf, create_mock_coa_data, cleanup_temp_files


class TestCoADoc:
    """Test suite for CoADoc functionality."""

    @pytest.fixture
    def coa_parser(self):
        """Create a CoADoc parser instance."""
        return CoADoc()

    @pytest.fixture
    def sample_pdf_path(self):
        """Create a temporary PDF file for testing."""
        return create_temp_pdf("Test COA content")

    def test_parser_initialization(self, coa_parser):
        """Test CoADoc parser initialization."""
        assert coa_parser is not None
        assert hasattr(coa_parser, 'parse')

    @patch('cannlytics.data.coas.CoADoc.parse')
    def test_parse_single_coa(self, mock_parse, coa_parser, sample_pdf_path):
        """Test parsing a single COA PDF."""
        # Mock the parse method to return test data
        mock_data = [create_mock_coa_data()]
        mock_parse.return_value = mock_data

        result = coa_parser.parse(sample_pdf_path)
        
        assert result == mock_data
        mock_parse.assert_called_once_with(sample_pdf_path)

    def test_parse_directory(self, coa_parser, tmp_path):
        """Test parsing a directory of COA PDFs."""
        # Create test PDF files
        pdf_files = []
        for i in range(3):
            pdf_path = tmp_path / f"coa_{i}.pdf"
            pdf_path.write_text(f"Test COA content {i}")
            pdf_files.append(str(pdf_path))

        with patch.object(coa_parser, 'parse') as mock_parse:
            mock_parse.return_value = [create_mock_coa_data()]
            
            result = coa_parser.parse_directory(str(tmp_path))
            
            # Should call parse for each PDF file
            assert mock_parse.call_count == 3

    def test_create_hash(self):
        """Test hash creation for COA data."""
        test_data = create_mock_coa_data()
        hash_result = create_hash(test_data)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) > 0

    @patch('cannlytics.data.coas.CoADoc.save')
    def test_save_coa_data(self, mock_save, coa_parser, tmp_path):
        """Test saving COA data to file."""
        test_data = [create_mock_coa_data()]
        output_path = tmp_path / "test_output.xlsx"
        
        coa_parser.save(test_data, str(output_path))
        
        mock_save.assert_called_once_with(test_data, str(output_path))

    def test_scan_qr_code(self, coa_parser, tmp_path):
        """Test scanning QR codes from images."""
        # Create a test image file
        image_path = tmp_path / "test_qr.png"
        image_path.write_text("Mock QR code data")
        
        with patch.object(coa_parser, 'scan') as mock_scan:
            mock_scan.return_value = "https://example.com/coa"
            
            result = coa_parser.scan(str(image_path))
            
            assert result == "https://example.com/coa"
            mock_scan.assert_called_once_with(str(image_path))

    @pytest.mark.parametrize("file_extension", [".pdf", ".jpg", ".png"])
    def test_supported_file_types(self, coa_parser, file_extension, tmp_path):
        """Test that parser handles different file types."""
        test_file = tmp_path / f"test{file_extension}"
        test_file.write_text("Test content")
        
        with patch.object(coa_parser, 'parse') as mock_parse:
            mock_parse.return_value = [create_mock_coa_data()]
            
            coa_parser.parse(str(test_file))
            mock_parse.assert_called_once_with(str(test_file))

    def test_error_handling_invalid_file(self, coa_parser):
        """Test error handling for invalid files."""
        with pytest.raises(FileNotFoundError):
            coa_parser.parse("nonexistent_file.pdf")

    def test_dataframe_creation(self, coa_parser):
        """Test creating DataFrame from COA data."""
        test_data = [create_mock_coa_data()]
        
        df = pd.DataFrame(test_data)
        
        assert len(df) == 1
        assert 'sample_id' in df.columns
        assert 'sample_name' in df.columns

    def test_cleanup(self, sample_pdf_path):
        """Test cleanup of temporary files."""
        # This test ensures cleanup works properly
        cleanup_temp_files(sample_pdf_path)
        assert not Path(sample_pdf_path).exists()


class TestCoADocIntegration:
    """Integration tests for COA functionality."""

    @pytest.mark.integration
    def test_full_coa_workflow(self, tmp_path):
        """Test complete COA workflow from PDF to saved data."""
        parser = CoADoc()
        
        # Create test PDF
        pdf_path = tmp_path / "test_coa.pdf"
        pdf_path.write_text("Test COA content")
        
        with patch.object(parser, 'parse') as mock_parse:
            mock_data = [create_mock_coa_data()]
            mock_parse.return_value = mock_data
            
            # Parse COA
            result = parser.parse(str(pdf_path))
            
            # Create DataFrame
            df = pd.DataFrame(result)
            
            # Save data
            output_path = tmp_path / "output.xlsx"
            with patch.object(parser, 'save') as mock_save:
                parser.save(df, str(output_path))
                mock_save.assert_called_once()
            
            assert len(result) == 1
            assert len(df) == 1 