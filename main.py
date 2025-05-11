#!/usr/bin/env python3

import argparse
import logging
import sys

from result import RES
from utils import find_match_lines
from registry import Registry

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


def search_variable(pattern, file=None, directory=None):
    logger.info(
        f"[var] Searching variable for '{pattern}' in "
        f"{file or ('directory: ' + directory) if directory else 'codebase'}"
    )
    word_pattern = f"\\b{pattern}\\b"
    lines = find_match_lines(word_pattern, file=file)
    RES.add_list(lines)


def main():
    parser = argparse.ArgumentParser(
        prog='s',
        description='Smart code search tool'
    )

    parser.add_argument(
        'target',
        choices=['def', 'wrap', 'tree', 'type', 'var'],
        help='Target action: def | wrap | tree | type | var'
    )
    parser.add_argument(
        '-d', '--dir',
        nargs='?',
        const='.',
        help='Search in a directory (default: current)'
    )
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Search in a specific file'
    )
    parser.add_argument(
        'pattern',
        nargs='?',
        help='Pattern to match (required for def and wrap)'
    )

    args = parser.parse_args()

    # Dispatch
    if args.target == 'tree':
        list_tree(file=args.file, directory=args.dir)
    elif args.target == 'def':
        if not args.pattern:
            print("Error: 'def' target requires a pattern.")
            sys.exit(1)
        search_definitions(args.pattern, file=args.file, directory=args.dir)
    elif args.target == 'wrap':
        if not args.pattern:
            print("Error: 'wrap' target requires a pattern.")
            sys.exit(1)
        search_wrappers(args.pattern, file=args.file, directory=args.dir)
    elif args.target == 'var':
        if not args.pattern:
            print("Error: 'var' target requires a pattern.")
            sys.exit(1)
        search_variable(args.pattern, file=args.file, directory=args.dir)

    RES.show()


if __name__ == '__main__':
    main()
