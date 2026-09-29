# Cannlytics Utilities

The `cannlytics.utils` module contains constants and general utility functions for working with cannabis data. Due to the use of `zoneinfo` for managing time, Python 3.9+ is recommended.

## Constants

There are a number of useful constants in the `cannlytics.data.constants` submodule that you can use for standardizing data.

| Constant | Description |
|----------|-------------|
| `ANALYSES` | A map of encountered analyses to their standardized analysis. |
| `ANALYTES` | A map of encountered analytes to their standardized analyte. |
| `STANDARD_ANALYSES` | Standard analysis key map. |
| `STANDARD_FIELDS` | A map of encountered fields to their standardized field. |
| `STANDARD_UNITS` | A map of standard units by analysis to use when no units are obtainable. |
| `PRODUCT_TYPES` | A map of encountered product types to their standardized product type. |
| `STRAINS` | A map of encountered strains to their standardized strain name. |
| `CODINGS` | Standard value codings. |
| `DECARB` | Cannabinoid decarboxylation rate. |
| `DEFAULT_HEADERS` | Default headers to use for HTTP requests, because we are AI and should not be treated as a bot. |
| `RANDOM_STRING_CHARS` | Random characters to use in password generation. |
| `states` | A map of state abbreviations to state names. |
| `state_names` | A map of state names to state abbreviations. |
| `state_time_zones` | A map of state abbreviations to timezone. |

## Utility Functions

*String Utilities*

| Function | Description |
|----------|-------------|
| `camelcase(string)` | Turn a given string to CamelCase. |
| `camel_to_snake(string)` | Turn a camel-case string to a snake-case string. This function handles CamelCase better than `snake_case`. The function does not do well with all caps, e.g. "APP_ID".|
| `kebab_case(string)` | Turn a string into a kebab-case string. |
| `get_keywords(string)` | Get keywords for a given string. |
| `get_random_string(length, allowed_chars=RANDOM_STRING_CHARS)` | Return a securely generated random string. |
| `snake_case(string)` | Turn a given string to snake case. Handles CamelCase, replaces known special characters with preferred namespaces, replaces spaces with underscores, and removes all other nuisance characters. |
| `strip_whitespace(string)` | Strip whitespace from a string. |

*Number Utilities*

| Function | Description |
|----------|-------------|
| `convert_to_numeric(string, strip=False)` | Convert a string to numeric, optionally replacing non-numeric characters. |

*List Utilities*

| Function | Description |
|----------|-------------|
| `sorted_nicely(a)` | Sort the given iterable in the way that humans expect. |
| `split_list(a, at_index=None)` | Split a list in half or at a given index. |

*Dictionary Utilities*

| Function | Description |
|----------|-------------|
| `clean_dictionary(data, function=snake_case)` | Format dictionary keys with given function, snake case by default. |
| `clean_nested_dictionary(data, function=snake_case)` | Format nested (at most 2 levels) dictionary keys with a given function, snake case by default. |
| `remove_dict_fields(data, fields)` | Remove multiple keys from a dictionary. |
| `remove_dict_nulls(data)` | Return a shallow copy of a dictionary with all `None` values excluded. |
| `update_dict(context, function=camel_to_snake, **kwargs)` | Update dictionary with keyword arguments. |

*DataFrame Utilities*

| Function | Description |
|----------|-------------|
| `clean_column_strings(data, columns)` | Clean the column names of a given DataFrame. |
| `nonzero_columns(data)` | Return the non-zero column names of a DataFrame. |
| `nonzero_rows(data)` | Return the non-zero row keys of a DataFrame. |
| `rmerge(left, right, **kwargs)` | Perform a merge using pandas with optional removal of overlapping column names not associated with the join. |
| `to_excel_with_style(data, file_name, index=False, sheet_name='Sheet1', style=None)` | Save a DataFrame to Excel with no style. |

*Time Utilities*

| Function | Description |
|----------|-------------|
| `format_iso_date(date, sep='/')` | Format a human-written date into an ISO formatted date. |
| `get_timestamp(date, past=0, future=0, zone='utc)` | Get an ISO formatted timestamp. |

*File Utilities*

| Function | Description |
|----------|-------------|
| `get_directory_files(target_dir, file_type)` | Get all of the files of a specified type in a given directory. |
