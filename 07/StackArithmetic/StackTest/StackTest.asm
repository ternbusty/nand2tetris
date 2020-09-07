@17
D = A
@SP
A = M
M = D
@SP
M = M + 1
@17
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
D;JEQ
@SP
A = M - 1
M = 0
(BACK0)
@17
D = A
@SP
A = M
M = D
@SP
M = M + 1
@16
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
@TRUE1
D;JEQ
@SP
A = M - 1
M = 0
(BACK1)
@16
D = A
@SP
A = M
M = D
@SP
M = M + 1
@17
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
@TRUE2
D;JEQ
@SP
A = M - 1
M = 0
(BACK2)
@892
D = A
@SP
A = M
M = D
@SP
M = M + 1
@891
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
@TRUE3
D;JLT
@SP
A = M - 1
M = 0
(BACK3)
@891
D = A
@SP
A = M
M = D
@SP
M = M + 1
@892
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
@TRUE4
D;JLT
@SP
A = M - 1
M = 0
(BACK4)
@891
D = A
@SP
A = M
M = D
@SP
M = M + 1
@891
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
@TRUE5
D;JLT
@SP
A = M - 1
M = 0
(BACK5)
@32767
D = A
@SP
A = M
M = D
@SP
M = M + 1
@32766
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
@TRUE6
D;JGT
@SP
A = M - 1
M = 0
(BACK6)
@32766
D = A
@SP
A = M
M = D
@SP
M = M + 1
@32767
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
@TRUE7
D;JGT
@SP
A = M - 1
M = 0
(BACK7)
@32766
D = A
@SP
A = M
M = D
@SP
M = M + 1
@32766
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
@TRUE8
D;JGT
@SP
A = M - 1
M = 0
(BACK8)
@57
D = A
@SP
A = M
M = D
@SP
M = M + 1
@31
D = A
@SP
A = M
M = D
@SP
M = M + 1
@53
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
M = M + D
@112
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
@SP
A = M
A = A - 1
M = -M
@SP
M = M - 1
@SP
A = M
D = M
A = A - 1
M = D & M
@82
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
M = D | M
@SP
A = M
A = A - 1
M = !M
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
A = M - 1
M = -1
@BACK1
0;JMP
(TRUE2)
@SP
A = M - 1
M = -1
@BACK2
0;JMP
(TRUE3)
@SP
A = M - 1
M = -1
@BACK3
0;JMP
(TRUE4)
@SP
A = M - 1
M = -1
@BACK4
0;JMP
(TRUE5)
@SP
A = M - 1
M = -1
@BACK5
0;JMP
(TRUE6)
@SP
A = M - 1
M = -1
@BACK6
0;JMP
(TRUE7)
@SP
A = M - 1
M = -1
@BACK7
0;JMP
(TRUE8)
@SP
A = M - 1
M = -1
@BACK8
0;JMP
(END)
