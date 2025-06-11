# p-Chip8
## History of the Chip 8 System:
The Chip 8 system was developed in 1977 for the COSMAC VIP as a simple way to write programs and games for the computer. It utilized hexadecimal instructions, instead of machine language, which could be easily interpreted by the system. The Chip 8 spread to other systems, but eventually petered out by 1984. In 1990, newer versions of the system, like the Chip 48 and the SUPER-Chip extension saw use.

## System Hardware:
The Chip 8 system is generally used as a first introduction to emulation, usually because of its simplistic hardware design that can reflect the way most systems work, while skipping out on more complex items like graphics and audio.
The Chip 8 consists of:
- 4 kB of RAM
- a 64 x 32 monochrome display
- A program counter (PC) for pointing at the current instruction in memory
- A 16-bit index register for pointing at locations in memory
- A stack for 16-bit addresses
- An 8-bit delay and sound timer
- 16 8-bit registers from 0 to F, or V0 to VF (VF is often used as a flag register, for cases such as carry flags)

## Emulation:
An emulator is designed to emulate hardware through the use of a higher level programming language, which enables the execution of ROM files, or files of machine code that were designed for interpretation by the original hardware. This enables a variety of different uses, such as reverse engineering, testing functionality and processes, preserving history, and more.
The p-Chip8 emulator is designed to emulate the Chip 8 system using Python, with the Pygame library used to create a visual interface. 

The emulator "visualizes" the real hardware through the use of class attributes. Opcodes are defined as class methods and set in a reference table that is partially sorted by matching initial 4 bits. The emulator reads ROM files and then runs the information in the file through the emulated hardware (instanced with an object of the created Chip8 class), which enables execution of the ROM file without the use of the actual hardware.

**NOTE:** The p-Chip8 emulator does **NOT** come with built in audio support. Additionally, it does not come with a User Interface, so any usage or execution of ROM files must be done through direct interaction with the source code (which is freely provided). Please note that the code is not without its issues, and may be unable to perfectly execute some ROM files as would be seen with the original hardware. Finally, the p-Chip8 emulator does **NOT** provide any ROM files, as those may be considered copyright material. 
The emulator and any individuals associated with its creation do **NOT** support or condone piracy or the illegal acquisition of ROM files or any copyrighted material. This project is made strictly for educational purposes alone.
