import unittest
from unittest import mock
import sys
from main import main


class TestMainCLI(unittest.TestCase):

    @mock.patch("main.search_definitions")
    @mock.patch("main.RES.show")
    @mock.patch("sys.argv", ["s", "def", "my_func"])
    def test_def_with_pattern(self, mock_show, mock_search):
        main()
        mock_search.assert_called_once_with(
            "my_func",
            file=None,
            directory=None
        )
        mock_show.assert_called_once()

    @mock.patch("main.search_wrappers")
    @mock.patch("main.RES.show")
    @mock.patch("sys.argv", ["s", "wrap", "my_wrapper"])
    def test_wrap_with_pattern(self, mock_show, mock_search):
        main()
        mock_search.assert_called_once_with(
            "my_wrapper",
            file=None,
            directory=None
        )
        mock_show.assert_called_once()

    @mock.patch("main.list_tree")
    @mock.patch("main.RES.show")
    @mock.patch("sys.argv", ["s", "tree"])
    def test_tree_mode(self, mock_show, mock_tree):
        main()
        mock_tree.assert_called_once_with(file=None, directory=None)
        mock_show.assert_called_once()

    @mock.patch("sys.stdout", new_callable=lambda: sys.stderr)
    @mock.patch("sys.argv", ["s", "def"])  # Missing pattern
    def test_def_missing_pattern(self, mock_stdout):
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)

    @mock.patch("sys.stdout", new_callable=lambda: sys.stderr)
    @mock.patch("sys.argv", ["s", "wrap"])  # Missing pattern
    def test_wrap_missing_pattern(self, mock_stdout):
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
