"""
PDP-11 Assembly Code:

MOV    R0,-(SP)     ; saves register r0
MOV    #0,R0        ; zero it
ADD    R0, 4(SP) 
ADD    R0, 6(SP)

MOV	  (SP)+,R1         ; restore registers
	   MOV	  (SP)+,R0
	   RTS	  PC               ; Return from subroutine



"""

int add(int a, int b) {
    return a + b;
}