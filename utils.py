import logging
import subprocess
from typing import List

from line import Line

logger = logging.getLogger(__name__)


def find_match_lines(pattern, extensions=["*"], dir=".", file=None):
    command = f"grep -E -H -n --color=never '{pattern}'"
    if not file:
        name_patterns = [f"-name '*.{x}'" for x in extensions]
        command = f"find {dir} {' '.join(name_patterns)} | xargs {command}"
    else:
        command += f" {file}"

    logger.debug(f"Command: {command}")

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    lines = []
    for line_text in result.stdout.splitlines(True):
        # line is './filename:line_number:content'
        logger.info(f"Found: {line_text.strip()}")

        parts = line_text.split(":", 2)
        if len(parts) == 3:
            file_name = parts[0]
            line_number = int(parts[1])
            content = parts[2]
            line = Line(file_name, line_number - 1, content, pattern)
            lines.append(line)

    return lines


def get_wrapper_block(block: List[Line], lang):
    """
    Extracts a full C++ control block that wraps the given block, the given
    block is a list of lines.
    Handles if, else, switch, while, do, for, case, default.
    """

    if not block:
        return []

    start_line = block[0]
    end_line = block[-1]
    current = start_line.get_prev()
    logger.info(f"Searching for wrapper block for {start_line.content}")

    while current:
        if lang.is_control_block_start(current.content):
            logger.info(f"Found control block start: {current.content}")
            wrapper_block = lang.get_control_block(current, brief=True)
            # Check if wrapper block contains our target block by index
            if (
                wrapper_block
                and wrapper_block[0].index <= start_line.index
                and wrapper_block[-1].index >= end_line.index
            ):
                return wrapper_block
        elif lang.is_definition_start(current.content):
            wrapper_block = lang.get_definition_block(current, brief=True)
            # Check if wrapper block contains our target block by index
            if (
                wrapper_block
                and wrapper_block[0].index <= start_line.index
                and wrapper_block[-1].index >= end_line.index
            ):
                return wrapper_block
        current = current.get_prev()

    # No wrapping block found
    return []
