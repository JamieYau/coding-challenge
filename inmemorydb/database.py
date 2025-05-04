from typing import List, Dict, Any
import json
import logging
from .query_parser import QueryParser


class Database:
    """In-memory database with query capabilities."""

    def __init__(self, data: List[Dict[str, Any]]):
        """
        Initialize database with data.
        Args:
            data: List of records (dictionaries)
        """
        self.data = data
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Database initialized with {len(data)} records")

    @staticmethod
    def _clean_js_content(content: str) -> str:
        """
        Clean JavaScript-style content to make it valid JSON.
        Args:
            content: Raw content from the file
        Returns:
            Cleaned content that can be parsed as JSON
        """
        if content.startswith("var "):
            content = content[content.index("[") : content.rindex(";")]

        return content.strip()

    @classmethod
    def from_json_file(cls, file_path: str):
        """
        Create database from JSON file. Factory method.
        Args:
            file_path: Path to JSON file
        Returns:
            Database instance
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid
        """
        try:
            with open(file_path, "r") as f:
                content = f.read()

            cleaned_content = cls._clean_js_content(content)

            data = json.loads(cleaned_content)
            return cls(data)
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON: {str(e)}")
            raise ValueError(f"Invalid JSON in {file_path}") from e

    def query(self, query_str: str) -> List[Dict[str, Any]]:
        """
        Execute query against the database.
        Args:
            query_str: Query string (e.g., "WHERE field = value AND field2 > 10")
        Returns:
            List of matching records
        Raises:
            ValueError: If query is invalid
        """
        try:
            conditions = QueryParser.parse_query(query_str)
            return [
                record
                for record in self.data
                if QueryParser.evaluate_record(record, conditions)
            ]
        except ValueError as e:
            self.logger.error(f"Query failed: {str(e)}")
            raise ValueError(f"Invalid query: {str(e)}") from e

    def count(self) -> int:
        """Return total number of records."""
        return len(self.data)
