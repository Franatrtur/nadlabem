; << Generated by NadLabem >>
; the open source brandejs-to-assembly compiler

cpu 8086
segment code
..start mov bx, heap
        mov ds, bx
        mov bx, stack
        mov ss, bx
        mov sp, dno
        mov bp, sp

        mov ax, 1             ;x: int = fact(1) (9)
        push ax
        call fact
        mov word[x], ax
exit:
ok      hlt 
error   hlt 

fact:
        push bp               ;def fact(num: int) -> int { (1)
        mov bp, sp
        sub sp, 0

        mov ax, word[bp + 4]  ;    if (num == 0) { (2)
        push ax
        mov ax, 0
        mov bx, ax
        pop ax
        cmp ax, bx
        pushf 
        pop ax
        and ax, 64
        mov cl, 6
        shr al, cl
        jz ifout

        mov ax, 1             ;        return 1 (3)
        jmp rtn
ifout   mov ax, word[bp + 4]  ;	return num * fact(num - 1) (6)
        push ax
        mov ax, word[bp + 4]
        push ax
        mov ax, 1
        mov bx, ax
        pop ax
        sub ax, bx
        push ax
        call fact
        mov bx, ax
        pop ax
        mul bx
        jmp rtn
rtn     mov sp, bp
        pop bp
        ret 2

segment heap
stack   resw 1024
dno     db ?

x       resw 1
