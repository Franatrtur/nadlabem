## Organization
 - add a standard contribution procedure
 - CREATE A DEV BRANCH

## Options for output of intermediate steps
 - add flags for outputting an ast -> print to console or ! output a graphviz file  
! + options for doing it before/after pruning, with/without types
 - add flags for disabling optimization and/or pruning  
 - add flags for verbally describing pruning

## Small things
 - add string as alias for char[] (or char[]* ?)
 - add byte as alias for char and word as alias for int
 - REDO FOR statement to increment even on continue. (not sure if i did this already?)

## Standard library

### stdio (Standard Input/Output)
Handles user input and output.  

print(str: char*): Outputs a string to the console.  
println(str: char*): Outputs a string followed by a newline.  
read_char() -> char: Reads a single character from the input.  
read_line() -> char*: Reads a line of text from the input.  
### stdlib (Standard Utilities)
General-purpose functions.  

exit(code: int): Terminates the program with an exit code.  
malloc(size: int) -> void*: Allocates memory.  
free(ptr: void*): Frees allocated memory.  
memcmp(ptr1: void*, ptr2: void*, size: int) -> int: Compares memory blocks.  
memcpy(dest: void*, src: void*, size: int): Copies memory blocks.  
### stdnum (Numeric Operations)
Handles number-specific operations.  

abs(x: int) -> int: Returns the absolute value.  
max(a: int, b: int) -> int: Returns the larger of two numbers.  
min(a: int, b: int) -> int: Returns the smaller of two numbers.  
pow(base: int, exp: int) -> int: Computes base raised to exp.  

### stdstr (String Manipulation)
Functions for working with strings.

strlen(s: char*) -> int: Returns the length of a string.  
strcmp(s1: char*, s2: char*) -> int: Compares two strings.  
strcpy(dest: char*, src: char*) -> void: Copies a string.  
strcat(dest: char*, src: char*) -> void: Concatenates two strings.

### stdmath (Mathematics)
Advanced mathematical functions.

min  
max  
pow  
fact  

### stdtime (Time Utilities)
Handles time and date.  

time_now() -> int: Returns the current timestamp.  
sleep(ms: int): Pauses execution for the specified milliseconds.  
format_time(timestamp: int, format: char*) -> char*: Formats a timestamp.  

## Tests
 - tests
 - tests, tests, ... pls