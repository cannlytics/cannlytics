# Cannlytics Utility SDK

SDK reference for the `cannlytics.utils` module.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Function</th>
      <th>Description</th>
      <th>Args</th>
      <th>Returns</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>`camel_to_snake`</td>
      <td>Turn a camel-case string to a snake-case string. This function handles CamelCase better than `snake_case`. The function does not do well with all caps, e.g. "APP_ID".</td>
      <td>string (str): The string to convert to snake-case.</td>
      <td>(str): Returns the string in snake_case.</td>
    </tr>
    <tr>
      <td>`camelcase`</td>
      <td>Turn a given string to CamelCase.</td>
      <td>string (str): A given string to turn to CamelCase.</td>
      <td>(str): A string in CamelCase.</td>
    </tr>
    <tr>
      <td>`clean_column_strings`</td>
      <td>Clean the column names of a given DataFrame.</td>
      <td>data (DataFrame): A DataFrame with any column names.    column (str): The column of the DataFrame to clean.</td>
      <td>(DataFrame): A DataFrame with snake_case column names.</td>
    </tr>
    <tr>
      <td>`clean_dictionary`</td>
      <td>Format dictionary keys with given function, snake case by default.</td>
      <td>d (dict): A dictionary to clean.    function (function): A function to apply to each key.</td>
      <td>(dict): Returns the input dictionary with a function applied to the keys.</td>
    </tr>
    <tr>
      <td>`clean_nested_dictionary`</td>
      <td>Format nested (at most 2 levels) dictionary keys with a given function, snake case by default.</td>
      <td>d (dict): A dictionary to clean, allowing dictionaries as values.    function (function): A function to apply to each key.</td>
      <td>(dict): Returns the input dictionary with cleaned keys.</td>
    </tr>
    <tr>
      <td>`convert_month_year_to_date`</td>
      <td>Convert a month, year series to datetime. E.g. `'April 2022'`.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`convert_to_numeric`</td>
      <td>Convert a string to numeric, optionally replacing non-numeric characters.</td>
      <td>string (str): The string to attempt to parse to a number.</td>
      <td>(float): Returns either the original or the parsed number.</td>
    </tr>
    <tr>
      <td>`decode_pdf`</td>
      <td>Save an base-64 encoded string as a PDF.</td>
      <td>data (str): Base-64 encoded string representing a PDF.    destination (str): The destination for the PDF file.</td>
      <td></td>
    </tr>
    <tr>
      <td>`download_file_from_url`</td>
      <td>Download a file from a URL to a given directory. Author: H S Umer farooq <https://stackoverflow.com/a/53153505> License: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`dump_column`</td>
      <td>Turn a column from JSON to dictionaries, handling errors.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`encode_pdf`</td>
      <td>Open a PDF file in binary mode.</td>
      <td>filename (str): The full file path of a PDF to encode.</td>
      <td>(str): A string encoded in base-64.</td>
    </tr>
    <tr>
      <td>`end_of_month`</td>
      <td>Format a datetime as an ISO formatted date at the end of the month.</td>
      <td>value (datetime): A datetime value to transform into an ISO date.</td>
      <td>(str): An ISO formatted date.</td>
    </tr>
    <tr>
      <td>`end_of_period_timeseries`</td>
      <td>Convert a DataFrame from beginning-of-the-period to end-of-the-period timeseries.</td>
      <td>data (DataFrame): The DataFrame to adjust timestamps.    period (str): The period of the time series, monthly "M" by default.</td>
      <td>(DataFrame): The adjusted DataFrame, with end-of-the-month timestamps.</td>
    </tr>
    <tr>
      <td>`end_of_year`</td>
      <td>Format a datetime as an ISO formatted date at the end of the year.</td>
      <td>value (datetime): A datetime value to transform into an ISO date.</td>
      <td>(str): An ISO formatted date.</td>
    </tr>
    <tr>
      <td>`format_billions`</td>
      <td>The two args are the value and tick position.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`format_iso_date`</td>
      <td>Format a human-written date into an ISO formatted date. Ags:     date (str): A human-written date.     sep (str): The separating character, '/' by default (optional).</td>
      <td></td>
      <td>(str): An ISO formatted date string.</td>
    </tr>
    <tr>
      <td>`format_millions`</td>
      <td>The two args are the value and tick position.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`format_thousands`</td>
      <td>The two args are the value and tick position.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`get_directory_files`</td>
      <td>Get all of the files of a specified type in a given directory.</td>
      <td>target_dir (str): The directory containing the files.    file_type (str): The file type extension, 'pdf' by default (optional).</td>
      <td>Returns:</td>
    </tr>
    <tr>
      <td>`get_keywords`</td>
      <td>Get keywords for a given string.</td>
      <td>string (str): A string to get keywords for.</td>
      <td>(list): A list of keywords.</td>
    </tr>
    <tr>
      <td>`get_number_of_lines`</td>
      <td>Read the number of lines in a large file, such as a .csv or .tsv file.</td>
      <td>file_name (str): The file to count the lines, expecting a .csv file.    encoding (str): The encoding of the file, "utf-16" by default (optional).    errors (str): How to handle the errors, "ignore" by default (optional).    verbose (bool): Whether or not to print the count, `False` by        default (optional).</td>
      <td>(int): The number of lines of the file.\nCredit: glglgl, SU3 <https://stackoverflow.com/a/9631635/5021266>\nLicense: CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0/></td>
    </tr>
    <tr>
      <td>`get_random_string`</td>
      <td>Return a securely generated random string.  The bit length of the returned value can be calculated with the formula:     log_2(len(allowed_chars)^length)  For example, with default `allowed_chars` (26+26+10), this gives:   * length: 12, bit length =~ 71 bits   * length: 22, bit length =~ 131 bits  Copyright (c) Django Software Foundation and individual contributors. All rights reserved.  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:      1. Redistributions of source code must retain the above copyright notice,        this list of conditions and the following disclaimer.      2. Redistributions in binary form must reproduce the above copyright        notice, this list of conditions and the following disclaimer in the        documentation and/or other materials provided with the distribution.      3. Neither the name of Django nor the names of its contributors may be used        to endorse or promote products derived from this software without        specific prior written permission.  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`get_timestamp`</td>
      <td>Get an ISO formatted timestamp.</td>
      <td>date (str): An optional date to pin the timestamp to a specific time.    past (int): Number of minutes in the past to get a timestamp.    future (int): Number of minutes into the future to get a timestamp.    zone (str): A specific timezone or US state abbreviation, e.g. CA.</td>
      <td>(str): An ISO formatted date/time string in the specified time zone,\n        UTC by default.</td>
    </tr>
    <tr>
      <td>`kebab_case`</td>
      <td>Turn a string into a kebab-case string.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`months_elapsed`</td>
      <td>Calculate the months elapsed between two datetimes, returning 0 if a negative time span.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`remove_dict_fields`</td>
      <td>Remove multiple keys from a dictionary.</td>
      <td>data (dict): The dictionary to clean.    fields (list): A list of keys (str) to remove.</td>
      <td>(dict): Returns the dictionary with the keys removed.</td>
    </tr>
    <tr>
      <td>`remove_dict_nulls`</td>
      <td>Return a shallow copy of a dictionary with all `None` values excluded.</td>
      <td>data (dict): The dictionary to reduce.</td>
      <td>(dict): Returns the dictionary with the keys with\n        null values removed.</td>
    </tr>
    <tr>
      <td>`reorder_columns`</td>
      <td>Re-order a DataFrame given a specific order of columns. Remaining columns will be appended to the end of the DataFrame.</td>
      <td>data (DataFrame): A DataFrame to be re-ordered.    columns (list): A list of columns in desired order.</td>
      <td>(DataFrame): Returns the re-ordered DataFrame</td>
    </tr>
    <tr>
      <td>`reverse_dataframe`</td>
      <td>Reverse the ordering of a DataFrame.</td>
      <td>data (DataFrame): A DataFrame to re-order.</td>
      <td>(DataFrame): The re-ordered DataFrame.</td>
    </tr>
    <tr>
      <td>`rmerge`</td>
      <td>Perform a merge using pandas with optional removal of overlapping column names not associated with the join.  Though I suspect this does not adhere to the spirit of pandas merge command, I find it useful because re-executing IPython notebook cells containing a merge command does not result in the replacement of existing columns if the name of the resulting DataFrame is the same as one of the two merged DataFrames, i.e. data = pa.merge(data, df). I prefer this command over pandas df.combine_first() method because it has more flexible join options.  The column removal is controlled by the 'replace' flag which is 'left' (default) or 'right' to remove overlapping columns in either the left or right DataFrame. If 'replace' is set to None, the default pandas behavior will be used. All other parameters are the same as pandas merge command.  Author: Michelle Gill Source: https://gist.github.com/mlgill/11334821  Examples -------- >>> left       >>> right    a  b   c       a  c   d 0  1  4   9    0  1  7  13 1  2  5  10    1  2  8  14 2  3  6  11    2  3  9  15 3  4  7  12  >>> rmerge(left, right, on='a')    a  b  c   d 0  1  4  7  13 1  2  5  8  14 2  3  6  9  15  >>> rmerge(left, right, on='a', how='left')    a  b   c   d 0  1  4   7  13 1  2  5   8  14 2  3  6   9  15 3  4  7 NaN NaN  >>> rmerge(left, right, on='a', how='left', replace='right')    a  b   c   d 0  1  4   9  13 1  2  5  10  14 2  3  6  11  15 3  4  7  12 NaN  >>> rmerge(left, right, on='a', how='left', replace=None)    a  b  c_x  c_y   d 0  1  4    9    7  13 1  2  5   10    8  14 2  3  6   11    9  15 3  4  7   12  NaN NaN</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`sandwich_list`</td>
      <td>Create a range that cycles from start to the end to the middle. Credit: Norman <https://stackoverflow.com/a/36533868/5021266> License: CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0/></td>
      <td>a (str): The iterable to sandwich.</td>
      <td>(list): The sandwich index.</td>
    </tr>
    <tr>
      <td>`set_training_period`</td>
      <td>Helper function to restrict a series to the desired training time period.</td>
      <td>series (Series): The series to clean.    date_start (str): An ISO date to mark the beginning of the training period.    date_end (str): An ISO date to mark the end of the training period.Returns    (Series): The series restricted to the desired time period.</td>
      <td></td>
    </tr>
    <tr>
      <td>`snake_case`</td>
      <td>Turn a given string to snake case. Handles CamelCase, replaces known special characters with preferred namespaces, replaces spaces with underscores, and removes all other nuisance characters.</td>
      <td>string (str): The string to turn to snake case.</td>
      <td>(str): A snake case string.</td>
    </tr>
    <tr>
      <td>`sorted_nicely`</td>
      <td>Sort the given iterable in the way that humans expect. Credit: Mark Byers <https://stackoverflow.com/a/2669120/5021266> License: CC BY-SA 2.5 <https://creativecommons.org/licenses/by-sa/2.5/></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`strip_whitespace`</td>
      <td>Strip whitespace from a string.</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`unzip_files`</td>
      <td>Unzip all files in a specified folder. Alternatively, pass a .zip file to extract that file. Author: nlavr https://stackoverflow.com/a/69101930 License: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>`update_dict`</td>
      <td>Update dictionary with keyword arguments.</td>
      <td>context (dict): A dictionary of context to update.    function (function): Function to apply to final dictionary keys.    kwargs (*args): Key/value arguments to update in the dictionary.</td>
      <td>(dict): Returns the dictionary with updated keys.</td>
    </tr>
  </tbody>
</table>
