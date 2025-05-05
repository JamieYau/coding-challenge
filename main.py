import logging
from inmemorydb.database import Database
from inmemorydb.output_formatter import OutputFormatter


def setup_logging():
    """Configure logging settings."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main():
    """Main application entry point."""
    setup_logging()

    try:
        # Initialize database
        db = Database.from_json_file("Dataset/vessels.json")
        print(f"\nDatabase loaded with {db.count()} vessels")

        # Interactive query loop
        while True:
            try:
                print("\nEnter a query (or 'quit' to exit):")
                print(
                    "Example: WHERE Z13_STATUS_CODE = 4 AND BUILDER_GROUP = 'Guoyu Logistics'"
                )
                query = input("> ").strip()

                if query.lower() == "quit":
                    break

                # Execute query
                results = db.query(query)

                # Format and display results
                format_choice = OutputFormatter.prompt_format()
                OutputFormatter.display(results, format_choice)

            except ValueError as e:
                print(f"Error: {str(e)}")
            except Exception as e:
                logging.error(f"Unexpected error: {str(e)}")
                print("An unexpected error occurred. Please try again.")

    except Exception as e:
        logging.critical(f"Application failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
