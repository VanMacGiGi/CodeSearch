import re
import logging

logger = logging.getLogger("line")


def load_file(file_name):
    """Utility function to load file content as a list of lines."""
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.readlines()


class Line:
    """
    Represents a single line from a file, with functionality to get neighboring
    lines, match patterns, and format output.

    Class Attributes:
        fname (str): Name of the currently loaded file.
        fdata (list): Content of the currently loaded file as list of lines.

    Instance Attributes:
        file_name (str): The file this line is from.
        index (int): Line index in the file (0-based).
        content (str): The actual content of the line.
        highlight (optional): Highlight information or metadata.
    """

    fname = None
    fdata = None

    def __init__(self, file_name, index, content, highlight=None):
        """
        Initializes a Line object.

        Args:
            file_name (str): Name of the file.
            index (int): Index of the line in the file (0-based).
            content (str): The line content.
            highlight (optional): Optional highlight metadata.
        """
        self.file_name = file_name
        self.index = index
        self.content = content.rstrip()
        self.highlight = highlight

    def get_prev(self):
        """
        Returns the previous line in the same file.

        Returns:
            Line or None: A Line object representing the previous line,
                         or None if at start.
        """
        if self.index == 0:
            return None

        if Line.fname != self.file_name:
            Line.fname = self.file_name
            Line.fdata = load_file(self.file_name)

        return Line(Line.fname, self.index - 1, Line.fdata[self.index - 1])

    def get_next(self):
        """
        Returns the next line in the same file.

        Returns:
            Line or None: A Line object representing the next line,
                         or None if at end.
        """
        if Line.fname != self.file_name:
            Line.fname = self.file_name
            Line.fdata = load_file(self.file_name)

        if self.index + 1 >= len(Line.fdata):
            return None
        logger.debug(
            f"{Line.fname} +{self.index}: {Line.fdata[self.index].strip()}\n"
            f" ==> {Line.fname} +{self.index+1}: "
            f"{Line.fdata[self.index + 1].strip()}"
        )
        return Line(Line.fname, self.index + 1, Line.fdata[self.index + 1])

    def match(self, pattern):
        """
        Checks if the line content matches a given pattern.

        Args:
            pattern (str or re.Pattern): The pattern to match.

        Returns:
            bool: True if content matches the pattern, False otherwise.
        """
        return bool(re.search(pattern, self.content))

    def format(self):
        """
        Formats the line for display.

        Returns:
            str: Formatted string with file name, line number, and content.
        """
        RED = "\033[0;31m"
        RESET = "\033[0m"
        if self.highlight:
            content = re.sub(
                self.highlight,
                f"{RED}\\g<0>{RESET}",
                self.content
            )
        else:
            content = self.content

        return f"{self.file_name} +{self.index + 1:<5}: {content}"
