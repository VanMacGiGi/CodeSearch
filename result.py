class Result:
    """
    Collects and manages a set of Line objects, ensuring order and uniqueness.

    Attributes:
        lines (dict): Stores Line objects keyed by (file_name, index).
    """

    def __init__(self):
        """Initializes an empty Result object."""
        self.lines = {}

    def add(self, line):
        """
        Adds a Line object to the result set, ensuring uniqueness and order.

        If a line with the same (file_name, index) exists:
        - If the new line has highlight and existing doesn't, replace it.
        - Otherwise, keep the existing line.

        Args:
            line (Line): The Line object to add.
        """
        key = (line.file_name, line.index)

        existing = self.lines.get(key)
        if existing:
            if existing.highlight is None and line.highlight is not None:
                self.lines[key] = line  # Prefer line with highlight
        else:
            self.lines[key] = line  # Add new line

    def add_list(self, lines):
        """
        Adds a list of line objects.

        Args:
            lines (List[Line]): The list of Line objects to add.
        """
        [self.add(line) for line in lines]

    def show(self):
        """
        Displays all stored lines in order, using their formatted output.
        """
        # Sort by (file_name, index) for ordered output
        for key in sorted(self.lines):
            print(self.lines[key].format())


RES = Result()
