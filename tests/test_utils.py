import unittest
from unittest.mock import patch, MagicMock
from utils import find_match_lines
from line import Line
from utils import get_wrapper_block
from lang_c_plus import C_Plus
import os


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

    def setUp(self):
        self.file_name = "temp_utils_test.cpp"
        self.lines = [
            "void process_data() {",
            "    if (data_available) {",
            "        parse_data();",
            "        if (is_valid) {",
            "            process_valid_data();",
            "        }",
            "    }",
            "}"
        ]

        with open(self.file_name, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines))

    def test_get_wrapper_block(self):
        # Create Line objects for the file
        line_objects = []
        for i, content in enumerate(self.lines):
            line_objects.append(Line(self.file_name, i, content))

        # Test finding a wrapper for the inner if block
        inner_if_block = [line_objects[3], line_objects[4], line_objects[5]]
        wrapper = get_wrapper_block(inner_if_block, C_Plus)

        # Should find the outer if block as wrapper
        self.assertIsNotNone(wrapper)
        self.assertEqual(len(wrapper), 3)  # outer if and its body (brief mode)
        self.assertTrue(wrapper[0].content.strip().startswith("if"))
        self.assertEqual(wrapper[0].index, 1)  # Index of outer if

        # Test finding a wrapper for the outer if block
        outer_if_block = wrapper
        wrapper = get_wrapper_block(outer_if_block, C_Plus)

        # Should find the function as wrapper
        self.assertIsNotNone(wrapper)
        self.assertEqual(len(wrapper), 2)
        self.assertTrue(
            wrapper[0].content.strip().startswith("void process_data"))

        # Test with no wrapper
        function_block = wrapper
        wrapper = get_wrapper_block(function_block, C_Plus)

        # Should find no wrapper
        self.assertEqual(wrapper, [])

    def test_get_wrapper_block_empty_input(self):
        # Test with empty block
        wrapper = get_wrapper_block([], C_Plus)
        self.assertEqual(wrapper, [])

    def tearDown(self):
        os.remove(self.file_name)


if __name__ == "__main__":
    unittest.main()
