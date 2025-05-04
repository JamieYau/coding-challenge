import json
from typing import List, Dict, Any, Tuple
import re
from enum import Enum
import pandas as pd

class OutputFormat(Enum):
    """Available output formats for query results."""

    SIMPLE = "simple"  # Basic vessel info
    DETAILED = "detailed"  # All vessel fields
    TABLE = "table"  # Tabular format
    JSON = "json"  # Raw JSON


def clean_js_content(content: str) -> str:
    # Remove JavaScript variable assignment
    if content.startswith("var vessels ="):
        content = content[14:]  # Remove 'var vessels ='

    # Remove trailing semicolon if present
    if content.endswith(";"):
        content = content[:-1]

    return content.strip()


def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    try:
        print(f"Loading file: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Clean the content if it's JavaScript-style
        cleaned_content = clean_js_content(content)

        # Parse the JSON
        data = json.loads(cleaned_content)

        print(f"Successfully loaded {len(data)} records")
        return data

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format in {file_path}: {str(e)}")
        raise
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        raise


# Parse a query condition into field, operator, and value.
def parse_condition(condition: str) -> Tuple[str, str, Any]:
    pattern = r'(\w+)\s*(=|!=|<=|>=|<|>)\s*([\'"‘]?[^"\']+[\'"’]?)'
    match = re.match(pattern, condition.strip())

    if not match:
        raise ValueError(f"Invalid condition format: {condition}")

    field, operator, value = match.groups()

    # Remove quotes from string values
    if value.startswith(("'", '"', "‘")) and value.endswith(("'", '"', "’")):
        value = value[1:-1]
    else:
        # Try to convert to number if possible
        try:
            value = float(value)
        except ValueError:
            pass

    return field, operator, value


# Evaluate a condition against a particular record.
def evaluate_condition(
    record: Dict[str, Any], field: str, operator: str, value: Any
) -> bool:
    if field not in record:
        return False

    record_value = record[field]

    # Handle type conversion for numeric comparisons
    if isinstance(value, (int, float)) and isinstance(record_value, str):
        try:
            record_value = float(record_value)
        except ValueError:
            return False

    operators = {
        "=": lambda x, y: x == y,
        "<": lambda x, y: x < y,
        ">": lambda x, y: x > y,
        "<=": lambda x, y: x <= y,
        ">=": lambda x, y: x >= y,
        "!=": lambda x, y: x != y,
    }

    return operators[operator](record_value, value)


# Query the vessels data based on the given query string.
def query_vessels(vessels: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    if not query.startswith("WHERE"):
        raise ValueError("Query must start with 'WHERE'")

    # Remove 'WHERE' and split conditions by 'AND'
    conditions = query[5:].strip().split("AND")

    results = []
    for vessel in vessels:
        matches_all = True
        for condition in conditions:
            field, operator, value = parse_condition(condition)
            if not evaluate_condition(vessel, field, operator, value):
                matches_all = False
                break

        if matches_all:
            results.append(vessel)

    return results


def print_vessel_simple(vessel: Dict[str, Any]) -> None:
    """Print basic vessel information."""
    print("\nVessel Information:")
    print("-" * 50)
    print(f"Name: {vessel.get('Z01_CURRENT_NAME', 'Unknown')}")
    print(f"Type: {vessel.get('P36_VESSEL_TYPE', 'Unknown')}")
    print(f"Built: {vessel.get('ZR1_BUILT', 'Unknown')}")
    print(f"Z13 Status Code: {vessel.get('Z13_STATUS_CODE', 'Unknown')}")
    print(f"Builder Group: {vessel.get('BUILDER_GROUP', 'Unknown')}")
    print("-" * 50)


def print_vessel_detailed(vessel: Dict[str, Any]) -> None:
    """Print all vessel fields in a structured format."""
    print("\nDetailed Vessel Information:")
    print("-" * 80)
    for key, value in sorted(vessel.items()):
        print(f"{key}: {value}")
    print("-" * 80)


def print_vessel_table(vessels: List[Dict[str, Any]]) -> None:
    """Print vessels in a tabular format."""
    df = pd.DataFrame(vessels)
    print(df)


def save_vessel_json(vessels: List[Dict[str, Any]]) -> None:
    """Save vessels in JSON format to a new file."""
    with open("results.json", "w") as f:
        json.dump(vessels, f, indent=2)


def display_results(
    vessels: List[Dict[str, Any]], format: OutputFormat = OutputFormat.SIMPLE
) -> None:
    if not vessels:
        print("No vessels found matching the query.")
        return

    print(f"\nFound {len(vessels)} matching vessels")

    if format == OutputFormat.SIMPLE:
        print_vessel_simple(vessels[0])
        if len(vessels) > 1:
            print(f"\n... and {len(vessels) - 1} more vessels")

    elif format == OutputFormat.DETAILED:
        for i, vessel in enumerate(vessels, 1):
            print(f"\nVessel {i}/{len(vessels)}:")
            print_vessel_detailed(vessel)

    elif format == OutputFormat.TABLE:
        print_vessel_table(vessels)

    elif format == OutputFormat.JSON:
        save_vessel_json(vessels)


def get_output_format() -> OutputFormat:
    print("\nAvailable output formats:")
    for format in OutputFormat:
        print(f"- {format.value}")

    while True:
        choice = input("\nChoose output format (default: simple): ").strip().lower()
        if not choice:
            return OutputFormat.SIMPLE
        try:
            return OutputFormat(choice)
        except ValueError:
            print("Invalid format. Please choose from the available options.")


def main() -> None:
    try:
        # Load the vessels data
        vessels = load_json_file("Dataset/vessels.json")

        # Print total number of vessels
        print(f"\nTotal vessels in database: {len(vessels)}")

        # Interactive query loop
        while True:
            print("\nEnter a query (or 'quit' to exit):")
            print(
                "Example: WHERE Z13_STATUS_CODE = 4 AND BUILDER_GROUP = 'Guoyu Logistics'"
            )
            query = input("> ").strip()

            if query.lower() == "quit":
                break

            try:
                results = query_vessels(vessels, query)

                # Get output format
                output_format = get_output_format()

                # Display results
                display_results(results, output_format)

            except ValueError as e:
                print(f"Error: {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")

    except Exception as e:
        print(f"Program failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
