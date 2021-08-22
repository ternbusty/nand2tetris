@256
D = A
@SP
M = D
@return_address_0
D = A
@SP
A = M
M = D
@SP
M = M + 1
@LCL
D = M
@SP
A = M
M = D
@SP
M = M + 1
@ARG
D = M
@SP
A = M
M = D
@SP
M = M + 1
@THIS
D = M
@SP
A = M
M = D
@SP
M = M + 1
@THAT
D = M
@SP
A = M
M = D
@SP
M = M + 1
@SP
D = M
D = D - 1
D = D - 1
D = D - 1
D = D - 1
D = D - 1
@ARG
M = D
@SP
D = M
@LCL
M = D
@Sys.init
0;JMP
(return_address_0)
(Main.fibonacci)
@0
D = A
@ARG
A = M + D
D = M
@SP
A = M
M = D
@SP
M = M + 1
@2
D = A
@SP
A = M
M = D
@SP
M = M + 1
@SP
M = M - 1
@SP
A = M
D = M
A = A - 1
D = M - D
@TRUE0
D;JLT
@SP
A = M - 1
M = 0
(BACK0)
@SP
A = M - 1
D = M
@TRUE1
D;JNE
@SP
M = M - 1
@IF_FALSE
0;JMP
(IF_TRUE)
@0
D = A
@ARG
A = M + D
D = M
@SP
A = M
M = D
@SP
M = M + 1
@LCL
A = M
A = A - 1
A = A - 1
A = A - 1
A = A - 1
A = A - 1
D = M
@ret0
M = D
@SP
M = M - 1
@SP
A = M
D = M
@ARG
A = M
M = D
@ARG
D = M + 1
@SP
M = D
@LCL
A = M
A = A - 1
D = M
@THAT
M = D
@LCL
A = M
A = A - 1
A = A - 1
D = M
@THIS
M = D
@LCL
A = M
A = A - 1
A = A - 1
A = A - 1
D = M
@ARG
M = D
@LCL
A = M
A = A - 1
A = A - 1
A = A - 1
A = A - 1
D = M
@LCL
M = D
@ret0
A = M
0;JMP
(IF_FALSE)
@0
D = A
@ARG
A = M + D
D = M
@SP
A = M
M = D
@SP
M = M + 1
@2
D = A
@SP
A = M
M = D
@SP
M = M + 1
@SP
M = M - 1
@SP
A = M
D = M
A = A - 1
M = M - D
@return_address_1
D = A
@SP
A = M
M = D
@SP
M = M + 1
@LCL
D = M
@SP
A = M
M = D
@SP
M = M + 1
@ARG
D = M
@SP
A = M
M = D
@SP
M = M + 1
@THIS
D = M
@SP
A = M
M = D
@SP
M = M + 1
@THAT
D = M
@SP
A = M
M = D
@SP
M = M + 1
@SP
D = M
D = D - 1
D = D - 1
D = D - 1
D = D - 1
D = D - 1
D = D - 1
@ARG
M = D
@SP
D = M
@LCL
M = D
@Main.fibonacci
0;JMP
(return_address_1)
@0
D = A
@ARG
A = M + D
D = M
@SP
A = M
M = D
@SP
M = M + 1
@1
D = A
@SP
A = M
M = D
@SP
M = M + 1
@SP
M = M - 1
@SP
A = M
D = M
A = A - 1
M = M - D
@return_address_2
D = A
@SP
A = M
M = D
@SP
M = M + 1
@LCL
D = M
@SP
A = M
M = D
@SP
M = M + 1
@ARG
D = M
@SP
A = M
M = D
@SP
M = M + 1
@THIS
D = M
@SP
A = M
M = D
@SP
M = M + 1
@THAT
D = M
@SP
A = M
M = D
@SP
M = M + 1
@SP
D = M
D = D - 1
D = D - 1
D = D - 1
D = D - 1
D = D - 1
D = D - 1
@ARG
M = D
@SP
D = M
@LCL
M = D
@Main.fibonacci
0;JMP
(return_address_2)
@SP
M = M - 1
@SP
A = M
D = M
A = A - 1
M = M + D
@LCL
A = M
A = A - 1
A = A - 1
A = A - 1
A = A - 1
A = A - 1
D = M
@ret1
M = D
@SP
M = M - 1
@SP
A = M
D = M
@ARG
A = M
M = D
@ARG
D = M + 1
@SP
M = D
@LCL
A = M
A = A - 1
D = M
@THAT
M = D
@LCL
A = M
A = A - 1
A = A - 1
D = M
@THIS
M = D
@LCL
A = M
A = A - 1
A = A - 1
A = A - 1
D = M
@ARG
M = D
@LCL
A = M
A = A - 1
A = A - 1
A = A - 1
A = A - 1
D = M
@LCL
M = D
@ret1
A = M
0;JMP
(Sys.init)
@4
D = A
@SP
A = M
M = D
@SP
M = M + 1
@return_address_3
D = A
@SP
A = M
M = D
@SP
M = M + 1
@LCL
D = M
@SP
A = M
M = D
@SP
M = M + 1
@ARG
D = M
@SP
A = M
M = D
@SP
M = M + 1
@THIS
D = M
@SP
A = M
M = D
@SP
M = M + 1
@THAT
D = M
@SP
A = M
M = D
@SP
M = M + 1
@SP
D = M
D = D - 1
D = D - 1
D = D - 1
D = D - 1
D = D - 1
D = D - 1
@ARG
M = D
@SP
D = M
@LCL
M = D
@Main.fibonacci
0;JMP
(return_address_3)
(WHILE)
@WHILE
0;JMP
@END
0;JMP
(TRUE0)
@SP
A = M - 1
M = -1
@BACK0
0;JMP
(TRUE1)
@SP
M = M - 1
@IF_TRUE
0;JMP
(END)
