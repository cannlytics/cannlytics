"""
Export Logs
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 10/24/2023
Updated: 10/24/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
import google.auth
from google.cloud import logging_v2
from google.cloud.logging_v2 import DESCENDING
from datetime import datetime, timedelta
import pandas as pd


def get_logs(
        function_name,
        project_id=None,
        service_type='cloud_function',
        start_time=None,
        end_time=None,
    ):
    """
    Retrieves logs from a specific Cloud Function or Cloud Run service
    within a specified time range and organizes them into a DataFrame.

    Args:
        function_name (str): Name of the service to filter logs.
        project_id (str, optional): Project ID of the service.
        service_type (str, optional): Type of service to filter logs. Defaults to "cloud_function". Specify any other value to get Cloud Run services.
        start_time (datetime, optional): Datetime object representing the start time 
            to begin fetching logs. Defaults to None, which will be interpreted as 
            24 hours before the current time.
        end_time (datetime, optional): Datetime object representing the end time to 
            stop fetching logs. Defaults to None, which will be interpreted as the 
            current time.
            
    Returns:
        DataFrame: A pandas DataFrame containing the logs with necessary information 
            such as timestamp, protocol, latency, etc.
    """
    # Initialize the Cloud Logging Client.
    client = logging_v2.Client()
    if project_id is None:
        _, project_id = google.auth.default()

    # Define the time range.
    if not start_time:
        start_time = datetime.now() - timedelta(days=1)
    if not end_time:
        end_time = datetime.now()

    # Convert times to strings.
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Define the filter based on service type.
    if service_type == 'cloud_function':
        filter_str = f"resource.type=\"cloud_function\" AND resource.labels.function_name=\"{function_name}\" AND timestamp >= \"{start_str}\" AND timestamp <= \"{end_str}\""
    else:
        filter_str = f"resource.labels.service_name = \"{function_name}\" AND timestamp >= \"{start_str}\" AND timestamp <= \"{end_str}\""
    
    # Fetch and process logs.
    entries = list(client.list_entries(order_by=DESCENDING, filter_=filter_str))
    
    # Extract pertinent log information.
    logs_data = []
    for entry in entries:
        http_request = entry.http_request or {}
        logs_data.append({
            'timestamp': entry.timestamp,
            'text': entry.payload,
            'protocol': http_request.get('protocol'),
            'latency': http_request.get('latency'),
            'remote_ip': http_request.get('remoteIp'),
            'user_agent': http_request.get('userAgent'),
            'response_size': http_request.get('responseSize'),
            'request_size': http_request.get('requestSize'),
            'method': http_request.get('requestMethod'),
            'url': http_request.get('requestUrl').replace('https://cannlytics-website-deeuhexjlq-uc.a.run.app', '') if http_request.get('requestUrl') else None,
        })
        
    # Return as DataFrame
    return pd.DataFrame(logs_data)


# Get website logs.
df = get_logs(
    'cannlytics-website',
    service_type='cloud_run',
    start_time=datetime(2023, 10, 24),
    end_time=datetime(2023, 10, 24, 6),
)
print(df)

# Get sign up cloud function logs.
df = get_logs(
    'auth_signup',
    start_time=datetime(2023, 10, 20),
    end_time=datetime(2023, 10, 22),
)
print(df)

# Get parse COA jobs cloud function logs.
df = get_logs(
    'parse_coa_jobs',
    start_time=datetime(2023, 10, 16),
    end_time=datetime(2023, 10, 18),
)
print(df)
