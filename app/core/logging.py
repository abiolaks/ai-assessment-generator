import logging
import logging.config
import yaml
from pathlib import Path


def setup_logging():
    """Setup logging configuration from logging.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "logging.yaml"

    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                if config:  # Only apply if config is not empty
                    logging.config.dictConfig(config)
                else:
                    # Default minimal logging setup if YAML is empty
                    logging.basicConfig(
                        level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    )
        except Exception as e:
            print(f"Error loading logging config: {e}")
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
    else:
        # Default minimal logging setup
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
