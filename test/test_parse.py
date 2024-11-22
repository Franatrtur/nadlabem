import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.compiler import Compiler
from src.config import CompilationConfig

PROGRAM = """
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
"""

if __name__ == "__main__":
    compiler = Compiler(CompilationConfig())
    #print(f"{compiler=}")
    compiler.load(PROGRAM)
    #print(f"{compiler.source_code=}")
    compiler.tokenize()
    #print(f"{compiler.tokens=}")
    compiler.parse()
    print(compiler.tree)
    # compiler.translate()
    # print(f"{compiler.machine_code=}")