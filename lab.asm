; << Generated by NadLabem >>
; the open source brandejs-to-assembly compiler

cpu 8086
segment code
..start mov bx, heap
        mov ds, bx
        mov es, bx
        mov bx, stack
        mov ss, bx
        mov sp, dno
        mov bp, sp

        lea ax, [_str]           ;print(*"Ahoj") (10)
        push ax
        call print
        mov ax, 2                ;a: int = 5 + 2 (12)
        push ax
        mov ax, 5
        pop bx
        add ax, bx
        mov word[a], ax
exit:
ok      hlt
error   hlt

print:
        push bp                  ;def print(string: @char[]) -> void { (1)
        mov bp, sp
        sub sp, 2
        mov ax, 0                ;    for(i: int = 0, i == 10, i = i + 1){ (2)
        mov word[bp - 2], ax
for     nop 
        mov ax, 10
        push ax
        mov ax, word[bp - 2]
        pop bx
        cmp ax, bx
        pushf 
        pop ax
        and ax, 64
        mov cl, 6
        shr al, cl
        jz fout
        mov ax, word[bp - 2]     ;        printchar(string[i]) (3)
        mov si, ax
        lea bx, [bp + 4]
        mov ax, 0
        mov al, byte[bx + si]
        push ax
        call printchar
        jmp for
fout    nop 
rtn     mov sp, bp
        pop bp
        ret 2

printchar:
        push bp                  ;def printchar(byte: char) -> void { (6)
        mov bp, sp
        sub sp, 0
        nop                      ;    pass (7)
rtn1    mov sp, bp
        pop bp
        ret 2

segment heap
stack   resw 1024
dno     db ?

_str    db "Ahoj", 0
a       resb 2                   ;default