import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.compiler import Compiler
from src.config import CompilationConfig

PROGRAM = """


int x = 2
int* y = *x  ; y now references the same part of memory as x, as we defined it not by value, but by pointer
int* x = 2  ; we load 2 as the pointer, but should throw errow when strict 

y = y+1     ; x is also now 3
y = y[0]    ; no change, but should throw errow when strict 
y = y[1]    ; no telling what might happen as we load the byte after y, but should throw errow when strict 

int* z = y+1; once again loads y as the address, but should throw errow when strict

array[int] arr = [1,2,3,x]
x = arr[1]  ; x=2
y = array   ; because y is int, it reads an int (1), but should throw errow when strict
x = arr[5]  ; no telling what might happen, but should throw errow when strict ?

;two ways of doing the same thing:
int a = arr[1]      ; we check that item type of arr is int when strict
int a = &(*arr + 1) ; we just give up on type checking here, warn when strict


;arguments by val vs by ref(pointer):
int myfunc(int* ref, int val){
    val = ref   ; no outside change
    ref = val   ;modifies the original
    return *ref ; actually we can return a pointer as its an int
}
int* b = myfunc(x, a) ; x might change, a will not

; side note:  *int func(...){...} ; should throw error  always


;wild shit:
array[int] mixed_array = [*arr, *x, *y] ; array of ints - pointers to arr, to x, and to y
; should we somehow check the types there? probably not, too complicated

array[int]* arr_view = mixed_array[0] ; we view the pointer to arr as an array again (dereference)
z = &mixed_array[1]                     ; set z to x



{
    int x = 2;
    x=1
}
"""

if __name__ == "__main__":
    compiler = Compiler(CompilationConfig())
    print(f"{compiler=}")
    compiler.load(PROGRAM)
    print(f"{compiler.source_code=}")
    compiler.tokenize()
    print(f"{compiler.tokens=}")
    compiler.parse()
    print(compiler.tree)
    # compiler.translate()
    # print(f"{compiler.machine_code=}")