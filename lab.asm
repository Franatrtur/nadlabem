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

        hlt                   ;$ hlt (1)
exit:
        hlt 


segment heap
stack   resw 1024
dno     db ?

