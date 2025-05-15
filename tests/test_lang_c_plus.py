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
            "template <typename T> struct Wrapper { T value; };",
            "",
            "if (a > b) {",
            "    doSomething();",
            "}",
            "",
            "static const char* getName(const char* prefix,",
            "                          const char* suffix) {",
            "    return strcat(prefix, suffix);",
            "}",
            "",
            "virtual void process() override {",
            "    // implementation",
            "}",
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
        self.assertFalse(C_Plus.is_definition_start("for (int i = 0; i < 10; ++i) {"))

    def test_not_definition_while(self):
        self.assertFalse(C_Plus.is_definition_start("while (true) {"))

    def test_not_definition_switch(self):
        self.assertFalse(C_Plus.is_definition_start("switch (x) {"))

    def test_not_definition_expression_continuation(self):
        self.assertFalse(C_Plus.is_definition_start(") {"))
        self.assertFalse(C_Plus.is_definition_start("&& condition"))
        self.assertFalse(C_Plus.is_definition_start("|| finalCheck()"))

    def test_not_definition_comparisons(self):
        self.assertFalse(C_Plus.is_definition_start("if (a == b)"))
        self.assertFalse(C_Plus.is_definition_start("while (x != y)"))
        self.assertFalse(C_Plus.is_definition_start("if (count >= 10)"))
        self.assertFalse(C_Plus.is_definition_start("if (value <= threshold)"))
        self.assertFalse(C_Plus.is_definition_start("if (a > b)"))
        self.assertFalse(C_Plus.is_definition_start("if (a < b)"))

    def test_multiline_function_declaration(self):
        self.assertTrue(C_Plus.is_definition_start(self.lines[23]))

    def test_function_with_qualifiers(self):
        self.assertTrue(C_Plus.is_definition_start(self.lines[28]))

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

    def test_brief_function_block(self):
        line = self.create_line(10)
        result = C_Plus.get_definition_block(line, brief=True)
        # First line, content lines, and closing brace
        self.assertEqual(len(result), 3)
        self.assertIn("add", result[0].content)
        self.assertIn("}", result[-1].content)

    def test_brief_class_block(self):
        line = self.create_line(5)
        result = C_Plus.get_definition_block(line, brief=True)
        # signature and closing brace
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0].content.strip().startswith("class"))
        self.assertIn("}", result[-1].content)

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
            ("static const char* getName(", True),  # Multi-line function
            ("virtual void process() override {", True),  # Function with qualifiers
            ("const int* getValues() const {", True),  # Const function
        ]

        for line, expected in test_cases:
            with self.subTest(line=line):
                self.assertEqual(C_Plus.is_definition_start(line), expected)

    def test_is_control_block_start(self):
        test_cases = [
            ("if (a > b) {", True),
            ("else if (x == y)", True),
            ("else", True),
            ("switch (val)", True),
            ("while (true) {", True),
            ("do", True),
            ("for (int i = 0; i < 10; i++)", True),
            ("return 0;", False),
            ("int a = 10;", False),
            ("#define LOOP 10", False),
        ]

        for line, expected in test_cases:
            with self.subTest(line=line):
                self.assertEqual(C_Plus.is_control_block_start(line), expected)

    # --- Tests for get_control_block ---

    def test_if_block(self):
        line = self.create_line(19)
        result = C_Plus.get_control_block(line)
        self.assertGreaterEqual(len(result), 3)  # if line, body, closing brace
        self.assertTrue(result[0].content.strip().startswith("if"))

    def test_brief_if_block(self):
        line = self.create_line(19)
        result = C_Plus.get_control_block(line, brief=True)
        self.assertEqual(len(result), 3)  # if line, body, and closing brace
        self.assertTrue(result[0].content.strip().startswith("if"))
        self.assertIn("}", result[-1].content)

    def test_if_else_block(self):
        # Create a file with if-else block for testing
        if_else_file = "temp_if_else.cpp"
        if_else_content = [
            "if (condition) {",
            "    doSomething();",
            "}",
            "else {",
            "    doSomethingElse();",
            "}",
        ]

        with open(if_else_file, "w", encoding="utf-8") as f:
            f.write("\n".join(if_else_content))

        # Create Line objects
        if_line = Line(if_else_file, 0, if_else_content[0])

        try:
            result = C_Plus.get_control_block(if_line)
            self.assertEqual(
                len(result), 8
            )  # All lines in if-else block, including any extras from structure
            self.assertTrue(result[0].content.strip().startswith("if"))

            # Find the else line
            else_line_found = False
            for line in result:
                if line.content.strip().startswith("else"):
                    else_line_found = True
                    break
            self.assertTrue(else_line_found)

            # Test brief version
            result_brief = C_Plus.get_control_block(if_line, brief=True)
            # if line, else line, closing braces
            self.assertGreaterEqual(len(result_brief), 3)
            self.assertTrue(result_brief[0].content.strip().startswith("if"))

            # Find the else in brief result
            else_line_found = False
            for line in result_brief:
                if line.content.strip().startswith("else"):
                    else_line_found = True
                    break
            self.assertTrue(else_line_found)
        finally:
            os.remove(if_else_file)

    def test_do_while_block(self):
        # Create a file with do-while block for testing
        do_while_file = "temp_do_while.cpp"
        do_while_content = ["do {", "    process();", "} while (condition);"]

        with open(do_while_file, "w", encoding="utf-8") as f:
            f.write("\n".join(do_while_content))

        # Create Line objects
        do_line = Line(do_while_file, 0, do_while_content[0])

        try:
            result = C_Plus.get_control_block(do_line)
            self.assertEqual(len(result), 3)  # All lines in do-while block
            self.assertTrue(result[0].content.strip().startswith("do"))
            self.assertTrue(result[-1].content.strip().endswith(";"))

            # Test brief version
            result_brief = C_Plus.get_control_block(do_line, brief=True)
            self.assertEqual(len(result_brief), 2)  # do and while (no body)
            self.assertTrue(result_brief[0].content.strip().startswith("do"))
            self.assertTrue(result_brief[-1].content.strip().endswith(";"))
        finally:
            os.remove(do_while_file)

    def tearDown(self):
        os.remove(self.file_name)


if __name__ == "__main__":
    unittest.main()
