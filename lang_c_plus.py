import re
import logging
from registry import Registry


logger = logging.getLogger("lang")


@Registry.register(["cpp", "hpp", "cc", "hh", "c", "h"])
class C_Plus:

    def is_definition_start(line: str, name_pattern="") -> bool:
        if not line or line.startswith("//") or line.startswith("/*"):
            return False

        patterns = [
            # class Foo, struct Bar
            r"^(template\s*<.*>)?\s*(class|struct|enum|union)\s+\w+",
            # ReturnType func(args) {
            (r"^(inline\s+)?[\w:<>\*&\s]+\s+\**\w+\s*\([^;]*\)?\s*"
             r"(const)?\s*({)?(?<!;)$"),
            # define MACRO
            r"^#\s*define\s+\w+",
            # typedef
            r"^typedef\s+.+",
        ]

        for pattern in patterns:
            if re.match(pattern, line):
                if (not name_pattern or
                        not re.search(
                            r"\(.*" + re.escape(name_pattern), line
                        )):
                    return True

        return False

    @staticmethod
    def is_block_start(line: str) -> bool:
        line = line.strip()

        # Remove trailing '{' if present for pattern matching
        line = line.rstrip('{').strip()

        block_keywords = [
            r'^if\s*\(.*\)$',
            r'^else\s+if\s*\(.*\)$',
            r'^else$',
            r'^switch\s*\(.*\)$',
            r'^case\s+.*:$',
            r'^default\s*:$',
            r'^while\s*\(.*\)$',
            r'^do$',
            r'^for\s*\(.*\)$',
        ]

        return any(re.match(p, line) for p in block_keywords)

    def get_definition_block(start_line):
        """
        Extracts a full C++ definition block starting from the given line.
        Handles macros, functions, classes, structs, and typedefs.

        Args:
            start_line (Line): The starting line of the definition.

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
            brace_count = (current.content.count("{") -
                           current.content.count("}"))

            while brace_count > 0:
                current = current.get_next()
                if current is None:
                    break
                brace_count += (current.content.count("{") -
                                current.content.count("}"))
                lines.append(current)
            logger.info(f"Get definition with {{: {lines[0].content}")
            return lines

        # Case 3: Ends with semicolon (e.g., typedefs, one-line declarations)
        if current.content.rstrip().endswith(";"):
            logger.info(f"Get one line definition: {lines[0].content}")
            return lines

        # Case 4: Multi-line function signature or declaration
        while (not current.content.rstrip().endswith(";") and
               not current.content.rstrip().endswith("{")):
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
                    brace_count += (current.content.count("{") -
                                    current.content.count("}"))
                    lines.append(current)
                break

        logger.info(f"Get definition: {lines[0].content}")
        return lines
