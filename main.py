#!/usr/bin/env python3

import argparse
import logging
from log_config import setup_logging

from result import RES
from utils import find_match_lines, get_wrapper_block
from registry import Registry

# Import to register it with Registry
from lang_c_plus import C_Plus  # noqa: F401

setup_logging()

logger = logging.getLogger("main")


def list_tree(file=None, directory=None):
    logger.info(
        f"[class] Listing classes in "
        f"{file or ('directory: ' + directory) if directory else 'codebase'}"
    )


def search_definitions(pattern, file=None, directory=None):
    logger.info(
        f"[def] Searching definitions for '{pattern}' in "
        f"{file or directory or 'codebase'}"
    )
    lines = find_match_lines(pattern, file=file)
    for line in lines:
        lang = Registry.get_lang_for(line.file_name)
        if not lang:  # Skip if no language handler is found
            continue
        if lang.is_definition_start(line.content, name_pattern=pattern):
            content = lang.get_definition_block(line)
            RES.add_list(content)


def search_wrappers(pattern, file=None, directory=None):
    logger.info(
        f"[wrap] Searching wrappers for '{pattern}' in "
        f"{file or ('directory: ' + directory) if directory else 'codebase'}"
    )
    lines = find_match_lines(pattern, file=file)
    for line in lines:
        lang = Registry.get_lang_for(line.file_name)
        if not lang:  # Skip if no language handler is found
            continue
        RES.add(line)
        content = [line]
        if lang.is_definition_start(line.content):
            content = lang.get_definition_block(line, brief=True)
        else:
            if lang.is_control_block_start(line.content):
                content = lang.get_definition_block(line, brief=True)
        while content:
            RES.add_list(content)
            if lang.is_definition_start(content[0].content):
                logger.info(f"Found definition start: {content[0].content}")
                break
            content = get_wrapper_block(content, lang)


def search_variable(pattern, file=None, directory=None):
    logger.info(
        f"[var] Searching variable for '{pattern}' in "
        f"{file or ('directory: ' + directory) if directory else 'codebase'}"
    )
    word_pattern = f"\\b{pattern}\\b"
    search_wrappers(word_pattern, file, directory)


def main():
    parser = argparse.ArgumentParser(prog="s", description="Smart code search tool")

    parser.add_argument(
        "target",
        nargs="?",
        default="wrap",
        help="Target action (def|wrap|tree|type|var), defaults to wrap",
    )
    parser.add_argument(
        "-d",
        "--dir",
        nargs="?",
        const=".",
        help="Search in a directory (default: current)",
    )
    parser.add_argument("-f", "--file", type=str, help="Search in a specific file")
    parser.add_argument("pattern", help="Pattern to search for")

    args = parser.parse_args()

    # Check if target is a valid target
    valid_targets = ["def", "wrap", "tree", "type", "var"]
    if args.target in valid_targets:
        args.target = args.target
    else:
        args.pattern = args.target
        args.target = "wrap"

    # Dispatch
    if args.target == "tree":
        list_tree(file=args.file, directory=args.dir)
    elif args.target == "def":
        search_definitions(args.pattern, file=args.file, directory=args.dir)
    elif args.target == "wrap":
        search_wrappers(args.pattern, file=args.file, directory=args.dir)
    elif args.target == "var":
        search_variable(args.pattern, file=args.file, directory=args.dir)

    RES.show()


if __name__ == "__main__":
    main()
