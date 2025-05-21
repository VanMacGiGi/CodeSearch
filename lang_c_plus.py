import re
import logging
from registry import Registry


logger = logging.getLogger("lang")


@Registry.register(["cpp", "hpp", "cc", "hh", "c", "h"])
class C_Plus:
    @staticmethod
    def is_definition_start(line: str, name_pattern="") -> bool:
        if not line or line.startswith("//") or line.startswith("/*"):
            return False

        # First check if it's a control block - if so, it's not a definition
        if C_Plus.is_control_block_start(line):
            return False

        # Skip lines that are continuations of conditions or expressions
        line_content = line.strip()
        if (
            line_content.startswith(")")
            or line_content.startswith("&&")
            or line_content.startswith("||")
            or "==" in line_content  # Skip comparison operations
            or "!=" in line_content
            or ">=" in line_content
            or "<=" in line_content
            or " > " in line_content
            or " < " in line_content
        ):
            return False

        # Check for unbalanced parentheses - likely part of a condition
        open_parens = line_content.count("(")
        close_parens = line_content.count(")")
        if (
            close_parens > open_parens
        ):  # More closing than opening parentheses indicates a continuation
            return False

        patterns = [
            # class Foo, struct Bar
            r"^(template\s*<.*>)?\s*(class|struct|enum|union)\s+\w+",
            # ReturnType func(args) { - complete function definition
            (
                r"^(inline\s+)?(const\s+)?(virtual\s+)?(static\s+)?"
                r"[\w:<>\*&\s]+\s+[\w:]*[\*&]?[\w:]+\s*\([^=!<>]*\)\s*"
                r"(const|override|final|noexcept)?\s*({)?(?<!;)$"
            ),
            # Multi-line function declaration that continues on next line
            # static const char* func_name(const char* param1, const char* param2
            (
                r"^(inline\s+)?(const\s+)?(virtual\s+)?(static\s+)?"
                r"[\w:<>\*&\s]+\s+[\w:]*[\*&]?[\w:]+\s*\([^=!<>;{})]*$"
            ),
            # define MACRO
            r"^#\s*define\s+\w+",
            # typedef
            r"^typedef\s+.+",
        ]

        for pattern in patterns:
            if re.match(pattern, line):
                if not name_pattern or not re.search(
                    r"\(.*" + re.escape(name_pattern), line
                ):
                    return True

        return False

    @staticmethod
    def is_control_block_start(line: str) -> bool:
        line = line.strip()

        # Remove trailing '{' if present for pattern matching
        line = line.rstrip("{").strip()

        block_keywords = [
            r"^if\s*\(.*\)$",
            r"^else\s+if\s*\(.*\)$",
            r"^else$",
            r"^switch\s*\(.*\)$",
            r"^while\s*\(.*\)$",
            r"^do$",
            r"^for\s*\(.*\)$",
        ]

        return any(re.match(p, line) for p in block_keywords)

    def get_definition_block(start_line, brief=False):
        """
        Extracts a full C++ definition block starting from the given line.
        Handles macros, functions, classes, structs, and typedefs.

        Args:
            start_line (Line): The starting line of the definition.
            brief (bool): If True, only returns the signature and end line,
                          omitting the body.

        Returns:
            List[Line]: Lines that make up the full definition.
        """
        lines = [start_line]
        current = start_line

        # Case 1: Macro with backslashes
        if current.content.lstrip().startswith("#define"):
            while current.content.rstrip().endswith("\\"):
                current = current.get_next()
                if current is None:
                    break
                lines.append(current)
            logger.info(f"Get macro: {lines[0].content}")
            return lines

        # Case 2: Block with curly braces
        if "{" in current.content:
            brace_count = current.content.count("{") - current.content.count("}")

            while brace_count > 0:
                current = current.get_next()
                if current is None:
                    break
                brace_count += current.content.count("{") - current.content.count("}")
                if not brief:
                    lines.append(current)
                elif brace_count == 0:  # Only include closing brace in brief mode
                    lines.append(current)
            logger.info(f"Get definition with {{: {lines[0].content}")
            return lines

        # Case 3: Ends with semicolon (e.g., typedefs, one-line declarations)
        if current.content.rstrip().endswith(";"):
            logger.info(f"Get one line definition: {lines[0].content}")
            return lines

        # Case 4: Multi-line function signature or declaration
        while not current.content.rstrip().endswith(
            ";"
        ) and not current.content.rstrip().endswith("{"):
            current = current.get_next()
            if current is None:
                break
            lines.append(current)

            if current.content.strip().endswith("{"):
                # Start tracking braces now
                brace_count = 1
                while brace_count > 0:
                    current = current.get_next()
                    if current is None:
                        break
                    brace_count += current.content.count("{") - current.content.count(
                        "}"
                    )
                    if not brief:
                        lines.append(current)
                    elif brace_count == 0:  # Only include closing brace in brief mode
                        lines.append(current)
                break

        logger.info(f"Get definition: {lines[0].content}")
        return lines

    def get_control_block(start_line, brief=False):
        """
        Extracts a full C++ control block starting from the given line.
        Handles if, else, switch, while, do, for, case, default.
        If brief=True, returns only the head lines and main block braces.
        For switch blocks in brief mode, also includes case, default and break lines.
        """
        lines = [start_line]
        current = start_line

        # Handle do-while blocks first since they end with semicolon
        if current.content.strip().startswith("do"):
            brace_count = current.content.count("{") - current.content.count("}")

            # Get the body
            while brace_count > 0:
                current = current.get_next()
                if current is None:
                    break
                brace_count += current.content.count("{") - current.content.count("}")
                if not brief:
                    lines.append(current)
                elif current == start_line.get_next():  # Opening brace
                    lines.append(current)
                elif brace_count == 0:  # Closing brace
                    lines.append(current)

            # Get the while part and semicolon
            while not current.content.strip().endswith(";"):
                current = current.get_next()
                if current is None:
                    break
                lines.append(current)

            logger.info(f"Get do-while block: {lines[0].content}")
            return lines

        # Handle other control blocks
        # First get any continuation of the condition
        while not current.content.strip().endswith("{"):
            current = current.get_next()
            if current is None:
                break
            lines.append(current)

        # Then get the body
        if current and "{" in current.content:
            brace_count = current.content.count("{") - current.content.count("}")
            lines.append(current)  # Always include opening brace

            while brace_count > 0:
                current = current.get_next()
                if current is None:
                    break
                brace_count += current.content.count("{") - current.content.count("}")
                if not brief:
                    lines.append(current)
                elif brief and start_line.content.strip().startswith("switch"):
                    # For switch blocks in brief mode, include case, default and break
                    if (
                        current.content.strip().startswith("case")
                        or current.content.strip().startswith("default")
                        or current.content.strip().startswith("break")
                    ):
                        lines.append(current)
                    elif brace_count == 0:  # Include closing brace
                        lines.append(current)
                elif (
                    brace_count == 0
                ):  # Only include closing brace for non-switch blocks
                    lines.append(current)

        # For if blocks, also get any else clauses
        if start_line.content.strip().startswith("if"):
            current = current.get_next()
            if current and current.content.strip().startswith("else"):
                lines.append(current)

                # Get else body if it has braces
                if "{" in current.content:
                    brace_count = current.content.count("{") - current.content.count(
                        "}"
                    )
                    lines.append(current)  # Always include opening brace

                    while brace_count > 0:
                        current = current.get_next()
                        if current is None:
                            break
                        brace_count += current.content.count(
                            "{"
                        ) - current.content.count("}")
                        if not brief:
                            lines.append(current)
                        elif brace_count == 0:  # Only include closing brace
                            lines.append(current)

        logger.info(f"Get control block: {lines[0].content}")

        return lines
