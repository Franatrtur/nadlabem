kolik81 DB 0 
        MVI d,1 
        MVI c,0 
        LDA kolik81 
        MVI B,0
        CMP B
        JZ if1
        JMP out1
if1     NOP
        JMP konec7e 
out1    NOP
loop    NOP  
        LDA kolik81 
        MOV B,A
        MVI A,1
        CMA
        INR A
        ADD B
        STA kolik81

        MVI m,164 

        MOV a,l ; pricteme jednicku k h a l
        ADD d 
        MOV l,a 
        MOV a,h 
        ADC c 
        MOV h,a 
        LDA kolik81 
        MVI B,0
        CMP B
        JNZ if2
        JMP out2
if2     NOP
        JMP loop 
out2    NOP
konec7e HLT  