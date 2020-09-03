// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

    @i
    M = 1 // i = 1
    @R2
    M = 0
(LOOP)
    @i
    D = M // D = i
    @R1
    D = D - M // D = D - R1 (i = i - R1)
    @END
    D;JGT // if D > 0, jump to END
    @R0
    D = M // D = R0
    @R2
    M = D + M // M = D + R0 (R2 = R0 + R2)
    @i
    M = M + 1 // i = i + 1
    @LOOP
    0;JMP
(END)
    @END
    0;JMP
