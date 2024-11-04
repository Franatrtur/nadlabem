xe94    DB 0 
ycf1    DB 0 

        LDA xe94 
        MOV B,A 
        LDA ycf1 
        CMP B 
        JZ if1 
        JMP out1
if1     NOP  
        INR D 
out1    NOP  

konec86 HLT  