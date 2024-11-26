# NadLabem Assembly compiler
Our Brandejs language is a C-like Python-like language with support for inline assembly that targets the 16bit i8086 processor. Our NadLabem transpiler is the corresponding translator.  
 - It compiles Brandejs to regular i8086 assembly.
 - It is written in python.
 - It is open source.
 - It has no external dependencies.

### Brandejs source code example
```
# cpu 8086
# mov ax, 5
char[16][1]* acu = 0+["aa", "aaa"][0][0]
char[] mystring = "Hello World!"; comment

def bool compare(int* a, int b) return a + 1 >= b % 1000

def int main(){
    if(compare(*mystring, 5)){
        return 0+mystring[len(mystring) - 1];
    } else {
        return fib(5);
    }
}

def int fib(int i){
    if(i < 2){
        return i;
    } else {
        return fib(i - 1) + fib(i - 2);
    }
}
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