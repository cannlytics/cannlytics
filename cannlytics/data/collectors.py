"""
Data Collectors | Cannlytics
Copyright (c) 2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/8/2024
Updated: 12/10/2024
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
import os
from typing import Optional, Union

# External imports:
import pandas as pd

# Internal imports:
from cannlytics.data.cache import Bogart
from cannlytics.logs import initialize_logs
from cannlytics.data.web import initialize_selenium


class COACollector:
    """Base collector for certificates of analysis (COAs)."""

    def __init__(
            self,
            data_dir: str,
            pdf_dir: str,
            cache_path: Optional[str] = None,
            log_dir: Optional[Union[str, bool]] = 'D:\\data\\.logs',
            log_name: Optional[str] = 'get_results',
            max_retries: int = 3,
            pause_time: float = 3.33
        ):
        """Initialize the collector with configuration."""
        self.data_dir = data_dir
        self.pdf_dir = pdf_dir
        self.datasets_dir = os.path.join(data_dir, 'datasets')
        self.cache = Bogart(cache_path) if cache_path else Bogart()
        self.max_retries = max_retries
        self.pause_time = pause_time
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.datasets_dir, exist_ok=True)
        self.logger = initialize_logs(
            log_name,
            prefix=log_name.split('.')[0].replace('_', '-'),
            log_dir=log_dir,
        )

    def _init_selenium(
            self,
            download_dir: Optional[str] = None,
            headless: bool = True,
        ) -> None:
        """Initialize Selenium driver with proper configuration."""
        download_dir = download_dir or self.pdf_dir
        self.driver = initialize_selenium(
            headless=headless,
            download_dir=download_dir
        )
    
    def _quit_driver(self):
        """Close the Selenium driver."""
        if self.driver:
            self.driver.quit()
    
    def _save_results(self, df: pd.DataFrame, prefix: str) -> str:
        """Save results to a CSV file with a timestamp."""
        timestamp = pd.Timestamp.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename = f'{prefix}-{timestamp}.csv'
        outfile = os.path.join(self.datasets_dir, filename)
        df.to_csv(outfile, index=False)
        self.logger.info(f'Saved {len(df)} records to {outfile}')
        return outfile

    def get_results(self) -> pd.DataFrame:
        """Get results from a specific source, implemented by subclass."""
        raise NotImplementedError
