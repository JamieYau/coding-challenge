from enum import Enum
from typing import List, Dict, Any
import pandas as pd
import json


class OutputFormat(Enum):
    SIMPLE = "simple"
    DETAILED = "detailed"
    TABLE = "table"
    JSON = "json"


class OutputFormatter:
    """Handles formatting and displaying query results in various formats."""

    @classmethod
    def display(
        cls, vessels: List[Dict[str, Any]], format: OutputFormat = OutputFormat.SIMPLE
    ) -> None:
        """Main display method that routes to specific formatters."""
        if not vessels:
            print("No vessels found matching the query.")
            return

        print(f"\nFound {len(vessels)} matching vessels")

        formatter = {
            OutputFormat.SIMPLE: cls._format_simple,
            OutputFormat.DETAILED: cls._format_detailed,
            OutputFormat.TABLE: cls._format_table,
            OutputFormat.JSON: cls._format_json,
        }.get(format, cls._format_simple)

        formatter(vessels)

    @staticmethod
    def _format_simple(vessels: List[Dict[str, Any]]) -> None:
        """Format simple output showing key fields."""
        vessel = vessels[0]
        print("\nVessel Information:")
        print("-" * 50)
        print(f"Name: {vessel.get('Z01_CURRENT_NAME', 'Unknown')}")
        print(f"Type: {vessel.get('P36_VESSEL_TYPE', 'Unknown')}")
        if len(vessels) > 1:
            print(f"\n... and {len(vessels) - 1} more vessels")

    @staticmethod
    def _format_detailed(vessels: List[Dict[str, Any]]) -> None:
        """Format detailed output showing all fields for each vessel."""
        for i, vessel in enumerate(vessels, 1):
            print(f"\nVessel {i}/{len(vessels)}:")
            print("-" * 80)
            for key, value in sorted(vessel.items()):
                print(f"{key}: {value}")

    @staticmethod
    def _format_table(vessels: List[Dict[str, Any]]) -> None:
        """Format output as a table using pandas."""
        print(pd.DataFrame(vessels))

    @staticmethod
    def _format_json(vessels: List[Dict[str, Any]]) -> None:
        """Save output to JSON file."""
        with open("results.json", "w") as f:
            json.dump(vessels, f, indent=2)

    @classmethod
    def prompt_format(cls) -> OutputFormat:
        """Prompt user to select output format."""
        print("\nAvailable output formats:")
        for fmt in OutputFormat:
            print(f"- {fmt.value}")

        while True:
            choice = input("Choose format (default: simple): ").strip().lower()
            if not choice:
                return OutputFormat.SIMPLE
            try:
                return OutputFormat(choice)
            except ValueError:
                print("Invalid format. Please choose from the available options.")
