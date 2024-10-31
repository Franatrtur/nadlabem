;ignore all lines not ending with ";"
x	db 2
y	db 42h

	;1) saving literals to vars
    ;
	y=5;

    ;2) saving vars to vars
    y=x;

	;3) arithmetic, vars only
	x=x+y;
	y=x-y;

	;4) arithmetic, constants too
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

	mov b,a
	lda y
	add b
	inr b
	cma
	hlt
  