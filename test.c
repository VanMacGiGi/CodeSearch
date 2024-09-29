#include <stdio.h>

#define MAX 10 // Define a macro
#define PRINT_VAR(var) printf("Variable: %d\n", var) // Macro to print a variable

// Define a structure
struct Data {
    int id;
    char name[50];
};

// Function declarations
void processData(struct Data d, int isVi);
void checkCondition(int x);
int calculate(int a, int b);

// Main function
int main() {
    struct Data data = {1, "Test Data"};
    processData(data, 1); // Call to processData function
    
    int result = calculate(5, 3); // Call to calculate function
    PRINT_VAR(result); // Macro to print the result
    return 0;
}

// Function to process data
void processData(struct Data d, int isVi) {
    printf("Processing data: %s with id: %d\n", d.name, d.id);

    if (isVi) {
        for (int i = 0; i < MAX; i++) { // Nested for loop
            if (i % 2 == 0) {
                printf("So chan: %d\n", i);
            } else {
                printf("So le: %d\n", i);
            }
        }
    }
    else {
        for (int i = 0; i < MAX; i++) { // Nested for loop
            if (i % 2 == 0) {
                printf("Even number: %d\n", i);
            } else {
                printf("Odd number: %d\n", i);
            }
        }
    }
    checkCondition(d.id); // Call to checkCondition function
}

// Function to check conditions
void checkCondition(int x) {
    if (x < 0) {
        printf("x is negative");
        return;
    }
    if (x > 5) {
        printf("x is greater than 5\n");
    } else if (x == 5) {
        printf("x is equal to 5\n");
    } else {
        switch (x) {
            case 1:
                printf("x is 1\n");
                break;
            case 2:
                printf("x is 2\n");
                break;
            default:
                printf("x is less than 5\n");
                break;
        }
    }

    // Target string to search for in the script
    printf("Target string: found_string\n");
}

// Function to perform a simple calculation
int calculate(int a, int b) {
    return a + b;
}

