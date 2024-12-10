# NadLabem Assembly compiler
Our Brandejs language is a C-like Python-like language with support for inline assembly that targets the 16bit i8086 processor. Our NadLabem transpiler is the corresponding translator.  
 - It compiles Brandejs to regular i8086 assembly.
 - It is written in python.
 - It is open source.
 - It has no external dependencies.

### Brandejs source code example
```brandejs
def fact(num: int) -> int {
    if (num == 0) {  ; base case
        return 1
    }

	return num * fact(num - 1)  ; recursion
}

x: int = fact(5)
```

### Usage
1) Install nadlabem
2) run `python main.py --help` to see relevant flags and instructions
3) run main.py and pass in a file (ending in `.brandejs`)

### Language

See language.asm for currently planned abstractions and structures.

### Maintainers
 - Franatrtur
 - chickenien