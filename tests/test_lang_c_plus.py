import os
import unittest
from lang_c_plus import C_Plus
from line import Line


class TestCPlus(unittest.TestCase):
    def setUp(self):
        self.file_name = "temp_test.cpp"
        self.lines = [
            "#define MAX(a, b) \\",
            "    ((a) > (b) ? (a) : (b))",
            "",
            "typedef int myint;",
            "",
            "class MyClass {",
            "public:",
            "    void method();",
            "};",
            "",
            "int add(int a,",
            "        int b) {",
            "    return a + b;",
            "}",
            "",
            "// comment line",
            "inline int square(int x);",
            "template <typename T> struct Wrapper { T value; };"
        ]

        with open(self.file_name, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines))

    def create_line(self, index):
        return Line(self.file_name, index, self.lines[index])

    # --- Tests for is_definition_start ---

    def test_is_definition_start_macro(self):
        self.assertTrue(C_Plus.is_definition_start(self.lines[0]))

    def test_is_definition_start_typedef(self):
        self.assertTrue(C_Plus.is_definition_start(self.lines[3]))

    def test_is_definition_start_class(self):
        self.assertTrue(C_Plus.is_definition_start(self.lines[5]))

    def test_is_definition_start_function(self):
        self.assertTrue(C_Plus.is_definition_start(self.lines[10]))

    def test_is_definition_start_comment(self):
        self.assertFalse(C_Plus.is_definition_start(self.lines[14]))

    def test_is_definition_start_blank(self):
        self.assertFalse(C_Plus.is_definition_start(""))

    def test_is_definition_start_template_struct(self):
        self.assertTrue(C_Plus.is_definition_start(self.lines[17]))

    def test_not_definition_if(self):
        self.assertFalse(C_Plus.is_definition_start("if (x > 0) {"))

    def test_not_definition_for(self):
        self.assertFalse(C_Plus.is_definition_start(
            "for (int i = 0; i < 10; ++i) {"))

    def test_not_definition_while(self):
        self.assertFalse(C_Plus.is_definition_start("while (true) {"))

    def test_not_definition_switch(self):
        self.assertFalse(C_Plus.is_definition_start("switch (x) {"))

    # --- Tests for get_definition_block ---

    def test_macro_block(self):
        line = self.create_line(0)
        result = C_Plus.get_definition_block(line)
        self.assertEqual(len(result), 2)
        self.assertIn("MAX", result[0].content)

    def test_typedef_block(self):
        line = self.create_line(3)
        result = C_Plus.get_definition_block(line)
        self.assertEqual(len(result), 1)
        self.assertIn("typedef", result[0].content)

    def test_class_block(self):
        line = self.create_line(5)
        result = C_Plus.get_definition_block(line)
        self.assertEqual(len(result), 4)
        self.assertTrue(result[0].content.strip().startswith("class"))

    def test_function_block(self):
        line = self.create_line(10)
        result = C_Plus.get_definition_block(line)
        self.assertEqual(len(result), 4)
        self.assertIn("add", result[0].content)

    def test_inline_function_declaration(self):
        line = self.create_line(16)
        result = C_Plus.get_definition_block(line)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].content.strip().startswith("inline"))

    def test_template_struct(self):
        line = self.create_line(17)
        result = C_Plus.get_definition_block(line)
        self.assertGreaterEqual(len(result), 1)
        self.assertIn("template", result[0].content)

    def test_is_definition_start(self):
        test_cases = [
            ("struct MyStruct {", True),
            ("enum Colors {", True),
            ("union Data {", True),
            ("#define MAX 100", True),
            ("int add(int a, int b) {", True),
            ("void hello_world();", False),  # prototype
            ("int multiply(int a, int b)", True),
            ("    ", False),
            ("// comment", False),
            ("/* comment", False),
            ("#include <stdio.h>", False),
        ]

        for line, expected in test_cases:
            with self.subTest(line=line):
                self.assertEqual(C_Plus.is_definition_start(line), expected)

    def test_is_block_start(self):
        test_cases = [
            ("if (a > b) {", True),
            ("else if (x == y)", True),
            ("else", True),
            ("switch (val)", True),
            ("case 1:", True),
            ("default:", True),
            ("while (true) {", True),
            ("do", True),
            ("for (int i = 0; i < 10; i++)", True),
            ("return 0;", False),
            ("int a = 10;", False),
            ("#define LOOP 10", False),
        ]

        for line, expected in test_cases:
            with self.subTest(line=line):
                self.assertEqual(C_Plus.is_block_start(line), expected)

    def tearDown(self):
        os.remove(self.file_name)


if __name__ == "__main__":
    unittest.main()
