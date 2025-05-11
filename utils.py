import logging
import subprocess

from line import Line

logger = logging.getLogger(__name__)


def find_match_lines(pattern, extensions=['*'], dir='.', file=None):
    command = f"grep -E -H -n --color=never '{pattern}'"
    if not file:
        name_patterns = [f"-name '*.{x}'" for x in extensions]
        command = (
            f"find {dir} {' '.join(name_patterns)} | "
            f"xargs {command}"
        )
    else:
        command += f" {file}"

    logger.debug(f"Command: {command}")

    result = subprocess.run(
        command, shell=True, capture_output=True, text=True
    )

    lines = []
    for line_text in result.stdout.splitlines(True):
        # line is './filename:line_number:content'
        logger.info(f"Found: {line_text}")

        parts = line_text.split(":", 2)
        if len(parts) == 3:
            file_name = parts[0]
            line_number = int(parts[1])
            content = parts[2]
            line = Line(file_name, line_number - 1, content, pattern)
            lines.append(line)

    return lines
