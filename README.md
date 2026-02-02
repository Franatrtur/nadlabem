<div align="center">

# NadLabem i8086 Compiler

A modern language for a vintage processor.

</div>

The NadLabem compiler translates **Brandejs**, a language with a familiar C-like and Python-like syntax, into assembly for the 16-bit Intel 8086 processor. It's designed to be powerful, easy to use, and to bring modern programming conveniences to a classic architecture.

## Features

- **Hybrid Syntax:** Enjoy a comfortable mix of C-style blocks and Python-style function definitions.
- **Static Typing:** Catch errors early with type checking for variables and function signatures.
- **Modern Constructs:** Use `for` loops, `while` loops, `if/else` statements, `break`, and `continue`.
- **Modules and Namespacing:** Organize your code with a clean and simple module system.
- **Pointers and References:** Full control over memory with pointers, references, and pointer arithmetic.
- **Inline Assembly:** Drop down to raw assembly with `$` prefixed instructions to get closer to the hardware.
- **Rich Standard Library:** A growing library provides essentials for I/O, string manipulation, math, time, and more.
- **Compiler Power:**
    - **Optimization:** Minify and obfuscate your code for smaller, tighter assembly.
    - **AST Export:** Visualize your program's structure with `.dot` file exports of the Abstract Syntax Tree. *(planned feature)*
    - **No Dependencies:** Written in pure Python, it runs anywhere with no external libraries needed.
- **Open Source:** Fork it, fix it, improve it!

## Usage

Get up and running with the NadLabem compiler in a few steps.

1.  **Clone the Repository**
    ```sh
    git clone https://github.com/Franatrtur/nadlabem.git
    cd nadlabem
    ```
2.  **Write your code** in a file (e.g., `my_program.brandejs`). If you use VSCodium (VSCode), download our [Brandejs highlight](https://open-vsx.org/extension/NadLabemproject/brandejs-highlight) extension!
3.  **Compile it** from the command line:
    ```sh
    python main.py my_program.brandejs
    ```
4.  **Run the asm output** in an i8086 [emulator](https://is.muni.cz/auth/edutools/brandejs/cpu_emu?cpu=8086). By default, this will create `my_program.asm`.

### Useful Compiler Flags

-   `--output <file>`: Specify a different output file name.
-   `--print`: Print the generated assembly directly to the console.
-   `--minify`: Apply optimizations to make the code smaller.
-   `--help`: See all available compiler options.


## Full Example: Factorial

Here's a classic recursive factorial function in Brandejs. This example shows off functions, recursion, and how to print results to the console. Just copy this code into a file like `factorial.brandejs` in the project root and run it!

```brandejs
include "std/io.brandejs" as io

; Calculates the factorial of a number.
def fact(num: int) -> int {
    if (num <= 1) {
        return 1
    }
    return num * fact(num - 1)
}

; Calculate factorial of 5.
result: int = fact(5)

; Print the result to the output.
io.print(*"Factorial of 5 is: ")
io.print_decimal(result)
io.println(*"")
```

## Showcase

Get a feel for the Brandejs language with these quick examples.

#### Variables and Types
```brandejs
; Declare and initialize variables with their types.
x: int = 10
is_active: bool = true
initial: char = 'F'
message: char[]* = *"Hello, Brandejs!"
```

#### Functions
```brandejs
; Define functions with typed arguments and return values.
def add(a: int, b: int) -> int {
    return a + b
}

; Call a function.
result: int = add(5, 7) ; result is 12
```

#### Modules and Imports

Brandejs supports modules for namespacing and code organization.

**1. Named Imports (Recommended)**

You can include a file and give it a local alias. This is the safest way to manage dependencies.

```brandejs
include "std/io.brandejs" as io

; Now you can call functions from the module using the 'io' alias.
io.println(*"Hello from a module!")
```

**2. In-File Modules**

Use the `module` keyword to create a namespace within the current file.

```brandejs
module math {
    PI: int = 3 ; An approximation :)
    def square(n: int) -> int {
        return n * n
    }
}

; Access module members using the dot notation.
squared: int = math.square(4) ; squared is 16
```

#### Character Literals
```brandejs
; You can specify number literals as characters, which is useful
; for non-printable ASCII values.
null_char: char = 0c  ; The null character
val_5: char = 5c    ; The character with ASCII value 5
```

#### Signed vs. Unsigned Comparisons
```brandejs
; Brandejs supports two types of integer comparisons.
; Unsigned (default): <, >, <=, >=
is_greater: bool = 5 > 3 ; true

; Signed: <+, +>, <~, ~>
; Use these when comparing numbers that could be negative.
is_truly_less: bool = -10 <+ 0 ; true
```

#### Pointers and References
```brandejs
; Work with pointers for more advanced memory manipulation.
message: char[]* = *"A string literal pointer"

; Pass a char array by reference.
def print_it(str: @char[]) -> void {
    println(*str)
}

; Assign by reference (both variables point to the same memory).
line1: @char[] =@= get_line()
line2: @char[] =@= line1

; Pointer arithmetic (advances the pointer, doesn't modify data).
line2 =@= *line2 + 1 :: char[]* ; Skips the first character
```

#### Standard Library Highlights
```brandejs
; The standard library is full of useful tools.
include "std/str.brandejs" as str
include "std/lib.brandejs" as lib
include "std/time.brandejs" as time

; Get the length of a string.
len: int = str.strlen(*"hello")

; Compare two strings.
are_equal: bool = str.strcmp(*"a", *"b") == 0

; Get the current time from the system.
time.Time.load()
hour: char = time.Time.hour

; Exit the program immediately with a status code.
lib.exit()
```


## How It Works

The NadLabem compiler is a classic multi-pass compiler written entirely in Python. Here’s a brief overview of its journey from your Brandejs code to executable i8086 assembly.

1.  **Tokenization**: The process starts in `src/tokenizer/tokenize.py`. The tokenizer reads your source code and breaks it down into a flat list of "tokens"—the smallest meaningful units of the language, like `def`, `my_variable`, `+`, `123`, etc.

2.  **Parsing & AST Construction**: The list of tokens is fed to the parser (`src/parser/`). It consumes the tokens and builds an Abstract Syntax Tree (AST), a hierarchical representation of your program's structure. Each element of your code, like a function definition or a loop, becomes a "node" in this tree (defined in `src/nodes/`). This is also the stage where `include` statements are processed, and other source files are tokenized and parsed into the main AST.

3.  **Translation**: This is where the magic happens. The `Compiler` (`src/compiler.py`) initiates the translation process, which is handled by the target-specific `ProgramI8086Translator` (`src/i8086/program.py`). This master translator walks the AST node by node. For each node type (e.g., `IfNode`, `ForNode`, `OperationNode`), it invokes a specialized sub-translator from the `src/i8086/` directory. Each sub-translator's job is to output the specific i8086 assembly instructions required to implement that node's functionality.

4.  **Code Generation & Optimization**: As the translators produce assembly instructions, they are collected into a list. The `ProgramI8086Translator` adds the necessary boilerplate, such as segment definitions (`code`, `data`), stack setup, and global variable declarations. Finally, if enabled, an optimization pass (`src/i8086/optimize.py`) runs over the generated code to apply simplifications and reduce the final assembly size. The result is the complete `.asm` file ready for emulation.

### Maintainers
 - Franatrtur
 - chramiq
