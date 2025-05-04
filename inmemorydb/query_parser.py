import re
from typing import Any, Dict, List, Tuple, Union


class QueryParser:
    """Parses and evaluates database query conditions."""

    CONDITION_PATTERN = r'(\w+)\s*(=|!=|<=|>=|<|>)\s*([\'"‘]?[^"\']+[\'"’]?)'
    SUPPORTED_OPERATORS = {
        "=": lambda x, y: x == y,
        "!=": lambda x, y: x != y,
        "<": lambda x, y: x < y,
        ">": lambda x, y: x > y,
        "<=": lambda x, y: x <= y,
        ">=": lambda x, y: x >= y,
    }

    @classmethod
    def parse_query(cls, query: str) -> List[Tuple[str, str, Any]]:
        """
        Parse a complete query string into individual conditions.
        Args:
            query: Query string in format "WHERE condition [AND condition...]"
        Returns:
            List of (field, operator, value) tuples
        Raises:
            ValueError: If query format is invalid
        """
        if not query.strip().upper().startswith("WHERE"):
            raise ValueError("Query must start with 'WHERE'")

        # Remove WHERE and split conditions
        conditions_str = query[5:].strip()
        if not conditions_str:
            raise ValueError("No conditions after WHERE")

        return [
            cls.parse_condition(cond) for cond in cls.split_conditions(conditions_str)
        ]

    @classmethod
    def split_conditions(cls, conditions_str: str) -> List[str]:
        """Split conditions string by AND (case insensitive, handles multiple spaces)."""
        return [
            cond.strip()
            for cond in re.split(r"\s+AND\s+", conditions_str, flags=re.IGNORECASE)
        ]

    @classmethod
    def parse_condition(cls, condition: str) -> Tuple[str, str, Any]:
        """
        Parse a single condition into field, operator, value.
        Args:
            condition: Condition string (e.g. "Z13_STATUS_CODE = 4")
        Returns:
            Tuple of (field, operator, parsed_value)
        Raises:
            ValueError: If condition format is invalid
        """
        match = re.match(cls.CONDITION_PATTERN, condition.strip())
        if not match:
            raise ValueError(f"Invalid condition format: {condition}")

        field, operator, value = match.groups()

        if operator not in cls.SUPPORTED_OPERATORS:
            raise ValueError(f"Unsupported operator: {operator}")

        return field, operator, cls.parse_value(value)

    @classmethod
    def parse_value(cls, value: str) -> Union[str, float]:
        """Parse and convert the value from string to appropriate type."""
        # Remove surrounding quotes if present
        if value.startswith(("'", '"', "‘")) and value.endswith(("'", '"', "’")):
            return value[1:-1]

        # Try numeric conversion
        try:
            return float(value)
        except ValueError:
            return value

    @classmethod
    def evaluate_record(
        cls, record: Dict[str, Any], conditions: List[Tuple[str, str, Any]]
    ) -> bool:
        """
        Evaluate whether a record matches all conditions.
        Args:
            record: The record to evaluate
            conditions: List of (field, operator, value) tuples
        Returns:
            bool: True if record matches all conditions
        """
        return all(cls.evaluate_condition(record, *cond) for cond in conditions)

    @classmethod
    def evaluate_condition(
        cls, record: Dict[str, Any], field: str, operator: str, value: Any
    ) -> bool:
        """
        Evaluate a single condition against a record.
        Args:
            record: The record to evaluate
            field: Field name to check
            operator: Comparison operator
            value: Value to compare against
        Returns:
            bool: True if condition is met
        """
        if field not in record:
            return False

        record_value = record[field]

        # Handle type conversion for numeric comparisons
        if isinstance(value, (int, float)) and isinstance(record_value, str):
            try:
                record_value = float(record_value)
            except ValueError:
                return False

        return cls.SUPPORTED_OPERATORS[operator](record_value, value)
