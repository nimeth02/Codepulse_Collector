import logging

def setup_logging():
    """Configure logging with timestamps."""
    logging.basicConfig(
        filename="source_provider_tool.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO
    )
    logging.info("Application started")