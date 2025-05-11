import unittest
from io import StringIO
import sys

from line import Line
from result import Result


class TestResult(unittest.TestCase):
    def setUp(self):
        self.line1 = Line("file.txt", 0, "First line\n")
        self.line2 = Line("file.txt", 1, "Second line\n")
        self.line3 = Line("file.txt", 1, "Second line\n", highlight="*")
        self.line4 = Line("file.txt", 2, "Third line\n")

    def test_add_unique_lines(self):
        result = Result()
        result.add(self.line1)
        result.add(self.line2)

        self.assertEqual(len(result.lines), 2)
        self.assertIn(("file.txt", 0), result.lines)
        self.assertIn(("file.txt", 1), result.lines)

    def test_add_duplicate_line_no_highlight(self):
        result = Result()
        result.add(self.line2)  # no highlight
        result.add(self.line2)  # same line again

        self.assertEqual(len(result.lines), 1)
        self.assertEqual(result.lines[("file.txt", 1)], self.line2)

    def test_add_duplicate_prefers_highlight(self):
        result = Result()
        result.add(self.line2)  # no highlight
        result.add(self.line3)  # same line with highlight

        # Should keep the highlighted version
        self.assertEqual(len(result.lines), 1)
        self.assertEqual(result.lines[("file.txt", 1)], self.line3)

    def test_add_highlight_then_normal_should_not_replace(self):
        result = Result()
        result.add(self.line3)  # highlighted
        result.add(self.line2)  # normal

        # Should still keep the highlighted version
        self.assertEqual(result.lines[("file.txt", 1)], self.line3)

    def test_show_prints_sorted_lines(self):
        result = Result()
        result.add(self.line2)
        result.add(self.line1)
        result.add(self.line4)

        # Capture output of show()
        captured_output = StringIO()
        sys.stdout = captured_output

        result.show()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue().strip().splitlines()

        expected_output = [
            self.line1.format(),
            self.line2.format(),
            self.line4.format(),
        ]

        self.assertEqual(output, expected_output)


if __name__ == "__main__":
    unittest.main()
