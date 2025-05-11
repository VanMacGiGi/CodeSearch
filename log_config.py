import logging
import os


def setup_logging(default_level=logging.WARNING):
    logging.basicConfig(
        level=default_level,
        format="%(name)-10s - %(levelname)-5s - %(message)s"
    )

    # Example: LOG_LEVELS="module_a=DEBUG,module_b=INFO"
    raw_levels = os.getenv("LOG_LEVELS", "")
    for entry in raw_levels.split(","):
        if "=" in entry:
            module, level_str = entry.split("=", 1)
            level = getattr(logging, level_str.upper(), None)
            if not isinstance(level, int):
                continue

            if module.strip() == "*":
                logging.getLogger().setLevel(level)
            else:
                logging.getLogger(module).setLevel(level)


setup_logging()
