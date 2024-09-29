#!/bin/bash

# Function to display the help information
function display_help() {
    echo "Usage: $0 [options] <search_string>"
    echo "Options:"
    echo "  -F, --search-func   Search for function definitions containing the given string (default)"
    echo "  -S, --search-struct Search for defined structures containing the given string"
    echo "  -f, --find-func     Search for the definition of a specific function"
    echo "  -s, --find-struct   Search for the definition of a specific structure"
    echo "  -g, --find-global   Search for the declaration of a specific global variable"
    echo "  -m, --find-macro    Search for the definition of a specific macro"
    echo "  -a, --all           Search for string in all .c and .h files"
    echo "  -d, --directory DIR Specify the directory to search for C source files (default: current directory)"
    echo "  -r, --recursive     Search for C source files recursively in subdirectories"
    echo "  -v, --verbose       Enable verbose mode to display detailed output"
    echo "  -h, --help          Display this help information"
}

# Format highlight search target
COLOR='\033[0;31m'
NC='\033[0m' # No Color

# Function to search for defined structures containing the given string
function search_struct() {
    #>typedef struct struct_name {
    #>    ....
    #>} struct_other_name;

    #>struct struct_name {
    #>   ...
    #>};

    find $DIRECTORY -name "*.[ch]" | xargs \
    awk -v string=$1 '/^\s*(typedef )?struct[^=]*{/, /}/ {
        if (/^\s*(typedef )?struct[^=]*{/) {
            start_struct = "\n" FILENAME " +" FNR ":" $0
            has_string = 0
        } else if ($0 ~ string) {
            if (has_string == 0) {
                print start_struct
            }
            print FILENAME " +" FNR ":" $0
            has_string = 1
        } else if (/}/) {
            if (has_string == 1) {
                print FILENAME " +" FNR ":" $0
            }
        }
    }'
}

# Function to search for function definitions containing the given string
function search_func() {
    echo "" > /tmp/sc_out.txt
    search_string="$1"

    source_files=$(find $DIRECTORY -name "*.[ch]")
    for source_file in $source_files; do

        grep_results=$(grep -n -E "$search_string" "$source_file")
        [ -z "$grep_results" ] && continue

        echo "$grep_results" | while IFS=: read -r line_number _; do

            awk -v line=$line_number -v COLOR="$COLOR" -v NC="$NC" -v search_str="$search_string" '
            BEGIN {
                in_function = 0;
                block_stack_size = 0;
            }
            NR <= line {

                # End blocks
                if ($0 ~ /\s+}/) {
                    if (block_stack_size > 0) {

                        if (block_stack[block_stack_size - 1] ~ /if/) {
                            # if may continue
                            block_stack[block_stack_size] = FILENAME " +" FNR ":" $0;
                            #print "Add "  block_stack[block_stack_size]
                            block_stack_size++;
                        }
                        else if (block_stack[block_stack_size - 1] ~ /break/) {
                            # remove switch block
                            while ((block_stack_size > 0) && (block_stack[block_stack_size - 1] ~ /break|case|default/)) {
                                block_stack_size--;
                                #print "Remove "  block_stack[block_stack_size]
                            }
                            block_stack_size--; # remove switch
                            #print "Remove "  block_stack[block_stack_size]
                        }
                        else if (block_stack[block_stack_size - 1] ~ /else\s*{?\s*$/) {
                            # remove if block
                            while ((block_stack_size > 0) && (block_stack[block_stack_size - 1] ~ /}/)) {
                                block_stack_size--;
                                #print "Remove not if"  block_stack[block_stack_size];
                                if (block_stack[block_stack_size - 1] ~ /:\s*if\s*\(.*\)\s*{/) {
                                    block_stack_size--;
                                    #print "Remove "  block_stack[block_stack_size];
                                }
                            }
                        }
                        else {
                            block_stack_size--;
                            #print "Remove "  block_stack[block_stack_size];
                        }
                    }
                }

                # Start block
                if ($0 ~ /^\s*(if|for|while|switch)\s*\(.*\)\s*{/) {

                    # If previous is an if block and has }, end the if block
                    while ((block_stack_size > 0) && (block_stack[block_stack_size - 1] ~ /}\s*$/)) {
                        block_stack_size--;
                        #print "Remove "  block_stack[block_stack_size];
                        #if (block_stack[block_stack_size - 1] ~ /^\s*if\s*\(.*\)\s*{/) {
                        if (block_stack[block_stack_size - 1] ~ /:\s*if\s*\(.*\)\s*{/) {
                            block_stack_size--;
                            #print "Remove "  block_stack[block_stack_size];
                        }
                    }

                    block_stack[block_stack_size] = FILENAME " +" FNR ":" $0;
                    #print "Add "  block_stack[block_stack_size]
                    block_stack_size++;
                }

                if ($0 ~ /case\s+.*:|default:|^\s*else\s*{?\s*$|break/) {
                    block_stack[block_stack_size] = FILENAME " +" FNR ":" $0;
                    #print "Add " block_stack[block_stack_size]
                    block_stack_size++;
                }

                if (NR == line) {
                    print func_name
                    if (block_stack[block_stack_size - 1] ~ /case/) {
                        i = block_stack_size - 2
                        while (block_stack[i] ~ /(case|break)/) {
                            block_stack[i] = "";
                            i--;
                        }
                    }
                    for (i = 0; i < block_stack_size; i++) {
                        print block_stack[i];
                    }
                    sub(search_str, COLOR "&" NC, $0)
                    print FILENAME " +" FNR ":" $0;
                }

                if ($0 ~ /^[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*\)\s*{/) {
                    in_function = 1;
                    func_name = FILENAME " +" FNR ":" $0;
                }

                # End function of block when reach "}"
                if ($0 ~ /^}/) {
                    if (block_stack_size > 0) {
                        block_stack_size = 0;
                    } else if (in_function) {
                        in_function = 0;
                    }
                }
            }
            ($0 ~ /^}/) && in_function && (NR > line) {
                in_function = 0;
                print FILENAME " +" FNR ":" $0;
            }' "$source_file" >> /tmp/sc_out.txt
        done
    done
    cat /tmp/sc_out.txt | sort | uniq
}

function find_call() {
    find $DIRECTORY -name "*.[ch]" | xargs \
    awk -v string="$1" '/^(static\s+)?(\w+\s+)(\*\s*)?\w+\s*\([^=<>]*(\))?\s*({)?\s*$/ && !/\selse\s/, /^}/ {
        if (/^(static\s+)?(\w+\s+)(\*\s*)?\w+\s*\([^=<>]*(\))?\s*({)?\s*$/ && !/\selse\s/) {
            if (/^(static\s+)?(\w+\s+)(\*\s*)?\w+\s*\([^=<>]*(\))?\s*({)?\s*$/ && !/\selse\s/) {
                start_string = "\n" FILENAME " +" FNR ":" $0
                
    }'
}

# Function to search for the definition of a specific function
function find_func() {
    #[static] [type] [*] function_name(...)[{] 
    find $DIRECTORY -name "*.[ch]" | xargs \
    awk -v string="$1" -v content="$VERBOSE" '/^(static\s+)?(\w+\s+)(\*\s*)?\w+\s*\([^=<>]*\)\s*{?\s*$/, /^}/ {
        if (/^(static\s+)?(\w+\s+)(\*\s*)?\w+\s*\([^=<>]*\)\s*{?\s*$/ && $0 ~ string && !/;/ && /\(.*\)/) {
            print "\n" FILENAME " +" FNR ":" $0
            has_string = 1
        }
        else if (/^}/ && has_string == 1) {
            print FILENAME " +" FNR ":" $0
            has_string = 0
        }
        else if (has_string == 1 && content == "true") {
            print FILENAME " +" FNR ":" $0
        }
    }
    '
}

# Function to search for the definition of a specific structure
function find_struct() {
    find $DIRECTORY -name "*.[ch]" | xargs \
    awk -v string=$1 -v content="$VERBOSE" '/^(typedef )?struct[^=]*{/, /^}/ {
        if (/^(typedef )?struct[^=]*{/) {
            struct = "\n" FILENAME " +" FNR ":" $0
            if ($0 ~ string) {
                has_string = 1
            }
        } else if (/^}/ && ((has_string == 1) || ($0 ~ string ))) {
            print struct
            print FILENAME " +" FNR ":" $0
            has_string = 0
        } else if (content == "true") {
            struct = struct "\n" FILENAME " +" FNR ":" $0
        }
    }'
}

# Function to search for the declaration of a specific global variable
function find_global() {
    find $DIRECTORY -name "*.[ch]" | xargs \
    awk -v name=$1 '$0 ~ name && $0 !~ /\(/ && $0 !~ /\{/{
        if (/^\w.*/) {
            print FILENAME " +" FNR ":" $0
        }
    }'
}

# Function to search for the definition of a specific macro
function find_macro() {
    find $DIRECTORY -name "*.[ch]" | xargs \
    awk -v macro=$1 '/^[\s\t]*#[\s\t]*define[\s\t]*/ && $0 ~ macro {
        definition = FILENAME " +" FNR ":" $0
        while (/\\$/) {
            getline
            definition = definition "\n" FILENAME " +" FNR ":"  $0
        }
        print definition
        exit
    }'
}

# Function to search all string in all .h and .c files
function find_all() {
    find $DIRECTORY -name "*.[ch]" | xargs \
    awk -v string=$1 '$0 ~ string {print FILENAME " +" FNR ":" $0}'
}

# Check if there are no arguments provided, or if the help option is specified
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    display_help
    exit 0
fi

# Default values for optional parameters
[ -f /tmp/csearch.tmp ] && DIRECTORY=`cat /tmp/csearch.tmp`
[ "$DIRECTORY" == "" ] && DIRECTORY='./'
RECURSIVE="-maxdepth 1"
VERBOSE=false

# Parse the command-line arguments
if [[ $# -eq 1 ]] ; then
    search_func "$1"
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --search-struct|-S)
            search_struct "$2"
            exit 0
            ;;
        --search-func|-F|"")
            search_func "$2"
            exit 0
            ;;
        --find-func|-f)
            find_func "$2"
            exit 0
            ;;
        --find-struct|-s)
            find_struct "$2"
            exit 0
            ;;
        --find-call|-c)
            find_call "$2"
            exit 0
           ;;
        --find-global|-g)
            find_global "$2"
            exit 0
            ;;
        --find-macro|-m)
            find_macro "$2"
            exit 0
            ;;
        --find-all|-a)
            find_all "$2"
            exit 0
            ;;
        --directory|-d)
            is_set_directory=1
            DIRECTORY="$2"
            shift
            ;;
        --recursive|-r)
            RECURSIVE=
            ;;
        --verbose|-v)
            VERBOSE=true
            ;;
        *)
            display_help
            exit 1
            ;;
    esac
    shift
done

[ "$is_set_directory" == "1" ] && echo $DIRECTORY > /tmp/csearch.tmp && exit 0

# If no valid option is provided, display the help
display_help
exit 1

