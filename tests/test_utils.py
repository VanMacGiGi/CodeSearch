import unittest
from unittest.mock import patch, MagicMock
from utils import find_match_lines
from line import Line


class TestUtils(unittest.TestCase):

    @patch("utils.subprocess.run")
    def test_find_match_lines_parses_correctly(self, mock_run):
        pattern = "TODO"
        extensions = ["py", "js"]

        # Simulate grep output
        mock_run.return_value = MagicMock(
            stdout=(
                "./foo.py:12:# TODO: clean this up\n"
                "./bar.js:45:// TODO: refactor this function\n"
            )
        )

        result = find_match_lines(pattern, extensions)

        expected = [
            Line(
                file_name="./foo.py",
                index=11,
                content="# TODO: clean this up\n",
                highlight="TODO"
            ),
            Line(
                file_name="./bar.js",
                index=44,
                content="// TODO: refactor this function\n",
                highlight="TODO"
            )
        ]

        # Check type and values
        self.assertEqual(len(result), 2)
        for res_line, expected_line in zip(result, expected):
            self.assertIsInstance(res_line, Line)
            self.assertEqual(res_line.file_name, expected_line.file_name)
            self.assertEqual(res_line.index, expected_line.index)
            self.assertEqual(res_line.content, expected_line.content)
            self.assertEqual(res_line.highlight, expected_line.highlight)

        # Optionally verify subprocess was called correctly
        expected_command = (
            "find . -name '*.py' -name '*.js' | "
            "xargs grep -E -H -n --color=never 'TODO'"
        )
        mock_run.assert_called_once_with(
            expected_command,
            shell=True,
            capture_output=True,
            text=True
        )


if __name__ == "__main__":
    unittest.main()
