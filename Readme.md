Command line tool to support developer during searching in the code base to understand it.

Developer do different actions to get just one target, with this tool, for each target developer only do one action to aquire.

Example:
- To know all conditions needed to hit a code line, developer will look around the code line for the conditions. With this tool, they only run: `s '<code pattern>'` then it will print:
    - Functions and code block wrap the code line.
    - The call flow from entry function to the function contain the code line pattern.

The tool designed to work with all propramming language code base.

The tool is designed for performance.

# Features
- Support languages: C, C++
- Get definition of an object `s def <name_pattern>`

## Todo
- List all entry points. Entry points are functions/methods that is not called by other functions/method in current searching scrope.


