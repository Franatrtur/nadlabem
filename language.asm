;ignore all lines not ending with ";"
x	db 2
y	db 42h

	;1) saving literals to vars
    ;
	y=5;

    ;2) saving vars to vars
    y=x;

	;3) plus
	y=x+y;

	;4) simulated minus
	y=x-y;	

	;5) arithmetic, constants tooLDA 100h
	y=x+4;
	x=2-y;

	;if statement
	if x<0 end navesti_ano else navesti_ne;
	if x>0 then navesti_ano else navesti_ne;
	if x=0 then navesti_ano else navesti_ne;

	
	if x>=0 then navesti_ano else navesti_ne ;tohle neprijmeme
	if x<0 then navesti_ne else navesti_ano ;tohle ano


	;while loop (navesti_loop)
	while x<0 then navesti_loop else loop_end_navesti


	;simulated arithmetic
	y=x*5;
	y=x/5;
  