import unittest
from unittest.mock import patch

from line import Line


class TestLine(unittest.TestCase):
    def setUp(self):
        self.test_lines = [
            "First line\n",
            "Second line\n",
            "Third line\n"
        ]
        self.file_name = "test_file.txt"

    @patch('line.load_file')
    def test_get_prev(self, mock_load_file):
        mock_load_file.return_value = self.test_lines

        current = Line(self.file_name, 1, self.test_lines[1])
        prev = current.get_prev()

        self.assertIsNotNone(prev)
        self.assertEqual(prev.index, 0)
        self.assertEqual(prev.content, self.test_lines[0].rstrip())

    @patch('line.load_file')
    def test_get_prev_none(self, mock_load_file):
        mock_load_file.return_value = self.test_lines

        current = Line(self.file_name, 0, self.test_lines[0].rstrip())
        prev = current.get_prev()

        self.assertIsNone(prev)

    @patch('line.load_file')
    def test_get_next(self, mock_load_file):
        mock_load_file.return_value = self.test_lines

        current = Line(self.file_name, 1, self.test_lines[1])
        next_line = current.get_next()

        self.assertIsNotNone(next_line)
        self.assertEqual(next_line.index, 2)
        self.assertEqual(next_line.content, self.test_lines[2].rstrip())

    @patch('line.load_file')
    def test_get_next_none(self, mock_load_file):
        mock_load_file.return_value = self.test_lines

        current = Line(self.file_name, 2, self.test_lines[2])
        next_line = current.get_next()

        self.assertIsNone(next_line)

    def test_match(self):
        line = Line(self.file_name, 0, "This is a test line.\n")
        self.assertTrue(line.match("test"))
        self.assertFalse(line.match("nonexistent"))

    def test_format(self):
        line = Line(self.file_name, 1, "Formatted line\n")
        expected = f"{self.file_name}:{2:<5}: Formatted line"
        self.assertEqual(line.format(), expected)


if __name__ == "__main__":
    unittest.main()
