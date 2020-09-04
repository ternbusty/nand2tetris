// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(LOOP)
    @24576
    D = M
    @WHITE
    D;JGT // if D > 0, jump to WHITE
(BLACK)
    @i
    M = 0 // i = 0
(BLACKLOOP)
    @i
    D = M // D = i
    @8191
    D = D - A // D = D - 8191
    @BLACKEND
    D;JGT // if D > 0, jump to END
    @i
    D = M // D = i
    @SCREEN
    D = A + D // D = SCREEN + i
    @idx
    M = D // idx = SCREEN + i
    @32767
    D = A // D = 32767
    D = D + A // D = 65534
    D = D + 1 // D = 65535
    @idx
    A = M // A = SCREEN + i
    M = D // paint to black
    @i
    M = M + 1 // i = i + 1
    @BLACKLOOP
    0;JMP
(BLACKEND)
    @LOOP
    0;JMP
(WHITE)
    @j
    M = 0
(WHITELOOP)
    @j
    D = M // D = j
    @8191
    D = D - A // D = D - 8192
    @WHITEEND
    D;JGT // if D > 0, jump to END
    @j
    D = M // D = j
    @SCREEN
    A = A + D // A = SCREEN + j
    M = 0 // paint to white
    @j
    M = M + 1 // j = j + 1
    @WHITELOOP
    0;JMP
(WHITEEND)
    @LOOP
    0;JMP
