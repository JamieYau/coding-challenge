# Coding Challenge

## Overview

This project implements a simple in-memory database with a custom query language, designed to load and query vessel data from JSON files without using external database libraries.

## Problems

1. Getting an error when trying to load the json file. Only happens with the `var vessels =` in the json file. Fixed by removing the `var vessels =` and the semicolon from the json file.

2. Error when using single quotes (‘’) in the query. Fixed by adding in the regex pattern and removing the quotes from the value.

3. Old Regex pattern `(\w+)\s*(=|!=|<=|>=|<|>)\s*([\'"‘]?[\w\s]+[\'"’]?)` cut off queries at the first `.`.

Updated the regex pattern from `[\w\s]`+ to `[^"\']`+:

- `[\w\s]+` only matched word characters and spaces
- `[^"\']+` matches any character except quotes, which includes periods, hyphens, etc.

## Approach

1. **Load Data**

```
def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    # Clean JavaScript-style content if needed
    # Parse JSON into list of dictionaries
    # Return the parsed data
```

- Handles JavaScript-style JSON content with cleaning functions
- Uses standard Python data structures `(List[Dict])` as the in-memory database
- Includes robust error handling for file operations

2. **Query Parser**

```
def parse_condition(condition: str) -> Tuple[str, str, Any]:
    pattern = r'(\w+)\s*(=|!=|<=|>=|<|>)\s*([\'"']?[^"\']+[\'"']?)'
    # Extract field, operator, and value
    # Convert values to appropriate types
```

- Uses regex to parse query conditions in the format "field operator value"
- Handles string values with different quote styles
- Converts numeric values to appropriate Python types

3. **Query Evaluation**

```
def evaluate_condition(record: Dict[str, Any], field: str, operator: str, value: Any) -> bool:
    # Check if field exists in record
    # Handle type conversion for numeric comparisons
    # Apply the appropriate operator comparison
```

- Supports multiple comparison operators `(=, <, >, !=, <=, >=)`
- Handles type conversion for numeric comparisons
- Uses operator mapping for clean implementation

4. **Query Execution**

```
def query_vessels(vessels: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    # Split query into conditions
    # Apply conditions to each vessel record
    # Return matching vessels
```

- Parses `WHERE` clause and splits on `AND`
- Evaluates each condition against each record
- Implements logical AND between conditions

5. **Result Display**
   Multiple output formats using an enum approach:

- Simple: Basic vessel information
- Detailed: All vessel fields
- Table: Using pandas DataFrame
- JSON: Export to file

## Design Decisions

- **Data Structure**: Simple List[Dict] approach provides flexibility and matches JSON structure
- **Separation of Concerns**: Modular functions for loading, parsing, evaluating, and displaying
- **Error Handling**: Comprehensive error handling with descriptive messages
- **Extensibility**: Supporting multiple operators and output formats
