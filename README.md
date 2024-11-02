# NadLabem Assembly transpiler
Our Brandejs language is a superset of assembly that targets the 8bit i8080 processor. Our NadLabem transpiler is the corresponding translator.  
 - It translates to regular assembly.
 - It is written in python.
 - It is open source.
 - It has no external dependencies.

### Brandejs source code example
```
x = 5
y = 10 - x ; comment

if(x != 5){
    z = 0
}else{
    z = 1
}
    LDA z
    HLT ; program end
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