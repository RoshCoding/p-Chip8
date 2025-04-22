import pygame
import sys
import ctypes
import random
import time

random.seed(time.time_ns())

START_ADDRESS = 0x200
FONTSET_START_ADDRESS = 0x50
FONTSET_SIZE = 80

# Define the Chip8 class
class Chip8():
    def __init__(self):
        self.registers = [0] * 16  
        self.memory = [0] * 4096 
        self.index = 0
        self.pc = START_ADDRESS
        self.stack = [0] * 16 
        self.stack_pointer = 0
        self.delay_timer = 0
        self.sound_timer = 0
        self.keypad = [0] * 16  
        self.display = [0] * (64 * 32)  
        self.opcode = 0

        self.table = {
            0x0: self.table0,
            0x1: self.OP_1NNN,
            0x2: self.OP_2NNN,
            0x3: self.OP_3xkk,
            0x4: self.OP_4xkk,
            0x5: self.OP_5xy0,
            0x6: self.OP_6xkk,
            0x7: self.OP_7xkk,
            0x8: self.table8,
            0x9: self.OP_9xy0,
            0xA: self.OP_Annn,
            0xB: self.OP_Bnnn,
            0xC: self.OP_Cxkk,
            0xD: self.OP_Dxyn,
            0xE: self.tableE,
            0xF: self.tableF
        }

        self.table0 = {i: self.op_null for i in range(0x10)}
        self.table8 = {i: self.op_null for i in range(0x10)}
        self.tableE = {i: self.op_null for i in range(0x10)}
        self.tableF = {i: self.op_null for i in range(0x100)}
    
    
        self.table0[0xE0] = self.OP_00E0
        self.table0[0xEE] = self.OP_00EE   
        
        self.table8[0x00] = self.OP_8xy0
        self.table8[0x01] = self.OP_8xy1
        self.table8[0x02] = self.OP_8xy2
        self.table8[0x03] = self.OP_8xy3
        self.table8[0x04] = self.OP_8xy4
        self.table8[0x05] = self.OP_8xy5
        self.table8[0x06] = self.OP_8xy6
        self.table8[0x07] = self.OP_8xy7
        self.table8[0x0E] = self.OP_8xyE
        

        self.tableE[0x9E] = self.OP_Ex9E
        self.tableE[0xA1] = self.OP_ExA1

        
        self.tableF[0x07] = self.OP_Fx07
        self.tableF[0x0A] = self.OP_Fx0A
        self.tableF[0x15] = self.OP_Fx15
        self.tableF[0x18] = self.OP_Fx18
        self.tableF[0x1E] = self.OP_Fx1E
        self.tableF[0x29] = self.OP_Fx29
        self.tableF[0x33] = self.OP_Fx33
        self.tableF[0x55] = self.OP_Fx55
        self.tableF[0x65] = self.OP_Fx65
        

    def table0(self, opcode):
        sub_opcode = opcode & 0x00FF
        return self.table0.get(sub_opcode, self.op_null)


    def table8(self, opcode):
        sub_opcode = opcode & 0x000F
        return self.table8.get(sub_opcode, self.op_null)


    def tableE(self, opcode):
        sub_opcode = opcode & 0x00FF
        return self.tableE.get(sub_opcode, self.op_null)

        
    def tableF(self, opcode):
        sub_opcode = opcode & 0x00FF
        return self.tableF.get(sub_opcode, self.op_null)


        
    def op_null(self, opcode):
        # Do nothing
        pass
        

    # Loads the rom binary into the memory
    def load_rom(self, rom_path):
        with open(rom_path, 'rb') as f:
            rom = f.read()
            for i, byte in enumerate(rom):
                self.memory[START_ADDRESS + i] = byte

    def load_fontset(self):
        for i in range(FONTSET_SIZE):
            self.memory[FONTSET_START_ADDRESS + i] = fontset[i]

    def random_Generator(self):
        return random.randint(0, 255)
    
    # CLS - Clear the display
    def OP_00E0(self, *args):
        # Clear the display
        # Set all pixels to 0
        for i in range(len(self.display)):
            self.display[i] = 0
    
    # RET - Return from a subroutine
    def OP_00EE(self, *args):
        # Ensure stack pointer is within bounds
        if self.stack_pointer <= 0:
            print("Stack underflow error")
            self.pc = 0  # Reset program counter to prevent further execution
            return
        self.stack_pointer -= 1
        self.pc = self.stack[self.stack_pointer]
    
    # JP addr - Jump to address NNN
    def OP_1NNN(self, *args):
        # Jump to address NNN
        # Do bitwise AND with 0x0FFF to get the address
        # The opcode is stored in self.opcode
        # The address is stored in the last 12 bits of the opcode
        nnn = self.opcode & 0x0FFF
        self.pc = nnn
    
    # CALL addr - Call subroutine at NNN
    def OP_2NNN(self, *args):
        # Call subroutine at NNN
        # The address is stored in the last 12 bits of the opcode
        # The stack pointer is incremented and the current program counter is pushed onto the stack
        # The program counter is set to the address
        # Stack pointer should not exceed the stack size
        if self.stack_pointer >= len(self.stack):
            print("Stack overflow error")
            self.pc = 0
            return
        nnn = self.opcode & 0x0FFF
        self.stack[self.stack_pointer] = self.pc
        self.stack_pointer += 1
        self.pc = nnn
    
    # SE Vx, byte - Skip next instruction if Vx == kk
    def OP_3xkk(self, *args):
        # Skip the next instruction if Vx == kk
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The last byte of the opcode is the value to compare (kk)
        x = (self.opcode & 0x0F00) >> 8
        kk = self.opcode & 0x00FF
        if self.registers[x] == kk:
            self.pc += 2
    
    # SNE Vx, byte - Skip next instruction if Vx != kk
    def OP_4xkk(self, *args):
        # Skip the next instruction if Vx != kk
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The last byte of the opcode is the value to compare (kk)
        x = (self.opcode & 0x0F00) >> 8
        kk = self.opcode & 0x00FF
        if self.registers[x] != kk:
            self.pc += 2
    
    # SE Vx, Vy - Skip next instruction if Vx == Vy
    def OP_5xy0(self, *args):
        # Skip the next instruction if Vx == Vy
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The second byte of the opcode is the register number (Vy)
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        if self.registers[x] == self.registers[y]:
            self.pc += 2
    
    # LD Vx, byte - Set Vx = kk
    def OP_6xkk(self, *args):
        # Set Vx = kk
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The last byte of the opcode is the value to set (kk)
        x = (self.opcode & 0x0F00) >> 8
        kk = self.opcode & 0x00FF
        self.registers[x] = kk 

    # ADD Vx, byte - Set Vx = Vx + kk
    def OP_7xkk(self, *args):
        # Set Vx = Vx + kk
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The last byte of the opcode is the value to add (kk)
        x = (self.opcode & 0x0F00) >> 8
        kk = self.opcode & 0x00FF
        self.registers[x] += kk   
    
    # LD Vx, Vy - Set Vx = Vy
    def OP_8xy0(self, *args):
        # Set Vx = Vy
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The second byte of the opcode is the register number (Vy)
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.registers[x] = self.registers[y]

    # OR Vx, Vy - Set Vx = Vx OR Vy
    def OP_8xy1(self, *args):
        # Set Vx = Vx OR Vy
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The second byte of the opcode is the register number (Vy)
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.registers[x] |= self.registers[y]
    
    # AND Vx, Vy - Set Vx = Vx AND Vy
    def OP_8xy2(self, *args):
        # Set Vx = Vx AND Vy
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The second byte of the opcode is the register number (Vy)
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.registers[x] &= self.registers[y]
    
    # XOR Vx, Vy - Set Vx = Vx XOR Vy
    def OP_8xy3(self, *args):
        # Set Vx = Vx XOR Vy
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The second byte of the opcode is the register number (Vy)
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        self.registers[x] ^= self.registers[y]
    
    # ADD Vx, Vy - Set Vx = Vx + Vy, set VF = carry
    def OP_8xy4(self, *args):
        # Set Vx = Vx + Vy, set VF = carry
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The second byte of the opcode is the register number (Vy)
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4

        sum = self.registers[x] + self.registers[y]
        if sum > 255:
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0
        self.registers[x] = sum & 0xFF
    
    # SUB Vx, Vy - Set Vx = Vx - Vy, set VF = NOT borrow
    def OP_8xy5(self, *args):
        # Set Vx = Vx - Vy, set VF = NOT borrow
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The second byte of the opcode is the register number (Vy)
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4

        if self.registers[x] > self.registers[y]:
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0
        self.registers[x] -= self.registers[y]

    # SHR Vx {, Vy} - Set Vx = Vx SHL 1
    def OP_8xy6(self, *args):
        # Set Vx = Vx SHR 1
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The second byte of the opcode is the register number (Vy)
        x = (self.opcode & 0x0F00) >> 8
        self.registers[0xF] = self.registers[x] & 0x1
        self.registers[x] >>= 1
    
    # SUBN Vx, Vy - Set Vx = Vy - Vx, set VF = NOT borrow
    def OP_8xy7(self, *args):
        # Set Vx = Vy - Vx, set VF = NOT borrow
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The second byte of the opcode is the register number (Vy)
        # Flipped order of x and y from OP_8xy5
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4

        if self.registers[y] > self.registers[x]:
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0
        self.registers[x] = self.registers[y] - self.registers[x]
    
    # SHL Vx {, Vy} - Set Vx = Vx SHL 1
    def OP_8xyE(self, *args):
        # Set Vx = Vx SHL 1
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The second byte of the opcode is the register number (Vy)
        x = (self.opcode & 0x0F00) >> 8
        self.registers[0xF] = (self.registers[x] >> 7) & 0x1
        self.registers[x] <<= 1
    
    # SNE Vx, Vy - Skip next instruction if Vx != Vy
    def OP_9xy0(self, *args):
        # Skip the next instruction if Vx != Vy
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The second byte of the opcode is the register number (Vy)
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        if self.registers[x] != self.registers[y]:
            self.pc += 2  
    
    # LD I, addr - Set I = nnn
    def OP_Annn(self, *args):
        # Set I = nnn
        # The opcode is stored in self.opcode
        # The last 12 bits of the opcode are the address (nnn)
        nnn = self.opcode & 0x0FFF
        self.index = nnn
    
    # JP V0, addr - Jump to location nnn + V0
    def OP_Bnnn(self, *args):
        # Jump to address nnn + V0
        # The opcode is stored in self.opcode
        # The last 12 bits of the opcode are the address (nnn)
        nnn = self.opcode & 0x0FFF
        self.pc = nnn + self.registers[0]
    
    # RND Vx, byte - Set Vx = random byte AND kk
    def OP_Cxkk(self, *args):
        # Set Vx = random byte AND kk
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        # The last byte of the opcode is the value to AND with (kk)
        x = (self.opcode & 0x0F00) >> 8
        kk = self.opcode & 0x00FF
        self.registers[x] = self.random_Generator() & kk

    # DRW Vx, Vy, nibble - Draw a sprite at coordinate (Vx, Vy)
    def OP_Dxyn(self, *args):
        # Draw a sprite at coordinate (Vx, Vy)
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        n = self.opcode & 0x000F

        xPos = self.registers[x] % 64
        yPos = self.registers[y] % 32

        self.registers[0xF] = 0  # Reset collision flag

        for row in range(n):
            sprite_row = self.memory[self.index + row]
            for col in range(8):
                if sprite_row & (0x80 >> col):
                    display_index = (xPos + col) % 64 + ((yPos + row) % 32) * 64
                    if self.display[display_index] == 1:
                        self.registers[0xF] = 1
                    self.display[display_index] ^= 1

    # SKP Vx - Skip next instruction if key with the value of Vx is pressed
    def OP_Ex9E(self, *args):
        # Skip the next instruction if the key stored in Vx is pressed
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        x = (self.opcode & 0x0F00) >> 8
        if self.keypad[self.registers[x]] == 1:
            self.pc += 2
    
    # SKNP Vx - Skip next instruction if key with the value of Vx is not pressed
    def OP_ExA1(self, *args):
        # Skip the next instruction if the key stored in Vx is not pressed
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        x = (self.opcode & 0x0F00) >> 8
        if self.keypad[self.registers[x]] == 0:
            self.pc += 2
    
    # LD Vx, DT - Set Vx = delay timer value
    def OP_Fx07(self, *args):
        # Set Vx = delay timer value
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        x = (self.opcode & 0x0F00) >> 8
        self.registers[x] = self.delay_timer
    
    # LD Vx, K - Wait for a key press, store the value of the key in Vx
    def OP_Fx0A(self, *args):
        # Wait for a key press and store the value in Vx
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        x = (self.opcode & 0x0F00) >> 8

        # Wait for a key press
        if self.keypad[0]:
            self.registers[x] = 0
            
        elif self.keypad[1]:
            self.registers[x] = 1
            
        elif self.keypad[2]:
            self.registers[x] = 2
            
        elif self.keypad[3]:
            self.registers[x] = 3
            
        elif self.keypad[4]:
            self.registers[x] = 4
            
        elif self.keypad[5]:
            self.registers[x] = 5
            
        elif self.keypad[6]:
            self.registers[x] = 6
            
        elif self.keypad[7]:
            self.registers[x] = 7
            
        elif self.keypad[8]:
            self.registers[x] = 8
            
        elif self.keypad[9]:
            self.registers[x] = 9
            
        elif self.keypad[10]:
            self.registers[x] = 10
            
        elif self.keypad[11]:
            self.registers[x] = 11
        
        elif self.keypad[12]:
            self.registers[x] = 12
        
        elif self.keypad[13]:
            self.registers[x] = 13
        
        elif self.keypad[14]:
            self.registers[x] = 14
        
        elif self.keypad[15]:
            self.registers[x] = 15
        
        else:
            # No key pressed, wait for a key press
            self.pc -= 2

    # LD DT, Vx - Set delay timer = Vx
    def OP_Fx15(self, *args):
        # Set delay timer = Vx
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        x = (self.opcode & 0x0F00) >> 8
        self.delay_timer = self.registers[x]
    
    # LD ST, Vx - Set sound timer = Vx
    def OP_Fx18(self, *args):
        # Set sound timer = Vx
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        x = (self.opcode & 0x0F00) >> 8
        self.sound_timer = self.registers[x]

    # LD I, Vx - Set I = I + Vx
    def OP_Fx1E(self, *args):
        # Set I = I + Vx
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        x = (self.opcode & 0x0F00) >> 8
        self.index += self.registers[x]
    
    # LD F, Vx - Set I = location of sprite for digit Vx
    def OP_Fx29(self, *args):
        # Set I = location of sprite for digit Vx
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        x = (self.opcode & 0x0F00) >> 8
        self.index = FONTSET_START_ADDRESS + (self.registers[x] * 5)
    
    # LD B, Vx - Store BCD representation of Vx in memory locations I, I+1, and I+2
    def OP_Fx33(self, *args):
        # Store BCD representation of Vx in memory locations I, I+1, and I+2
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        x = (self.opcode & 0x0F00) >> 8
        value = self.registers[x]
        self.memory[self.index] = value // 100
        self.memory[self.index + 1] = (value // 10) % 10
        self.memory[self.index + 2] = value % 10
    
    # LD [I], Vx - Store registers V0 to Vx in memory starting at location I
    def OP_Fx55(self, *args):
        # Store registers V0 to Vx in memory starting at address I
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        x = (self.opcode & 0x0F00) >> 8
        for i in range(x + 1):
            self.memory[self.index + i] = self.registers[i]
    
    # LD Vx, [I] - Read registers V0 to Vx from memory starting at location I
    def OP_Fx65(self, *args):
        # Read registers V0 to Vx from memory starting at address I
        # The opcode is stored in self.opcode
        # The first byte of the opcode is the register number (Vx)
        x = (self.opcode & 0x0F00) >> 8
        for i in range(x + 1):
            self.registers[i] = self.memory[self.index + i]

    def Cycle(self):
        # Fetch the opcode
        self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        # Increment the program counter
        self.pc += 2

        # Get the first nibble of the opcode to determine which table to use
        first_nibble = (self.opcode & 0xF000) >> 12
        if first_nibble in self.table:
            handler = self.table[first_nibble]
            if callable(handler):
                sub_handler = handler(self.opcode)
                if callable(sub_handler):
                    sub_handler(self.opcode)
            else:
                print(f"Invalid handler for opcode: {hex(self.opcode)}")
        else:
            print(f"Unknown opcode: {hex(self.opcode)}")

        # Update timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

# Load the fontset
fontset = ctypes.c_uint8 * FONTSET_SIZE
fontset = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # D
    0xF0, 0x80, 0xF0, 0x80, 0x80, # E
    0xF0, 0x80, 0xF0, 0x90, 0x90  # F
]

if __name__ == "__main__":
    Chip8 = Chip8()
    Chip8.load_fontset()
    Chip8.load_rom("roms\Maze [David Winter, 199x].ch8")
        

    pygame.init()
    screen = pygame.display.set_mode((64 * 10, 32 * 10))  # Scale display by 10x
    pygame.display.set_caption("CHIP-8 Emulator")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Map keys to CHIP-8 keypad
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                   pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r,
                                   pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f,
                                   pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v]:
                    key_map = {
                        pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
                        pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
                        pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
                        pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
                    }
                    Chip8.keypad[key_map[event.key]] = 1
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                 pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r,
                                 pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f,
                                 pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v]:
                    key_map = {
                        pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
                        pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
                        pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
                        pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
                    }
                    Chip8.keypad[key_map[event.key]] = 0

        # Execute one cycle
        Chip8.Cycle()

        # Render display
        screen.fill((0, 0, 0))  # Clear screen
        for y in range(32):
            for x in range(64):
                if Chip8.display[x + (y * 64)]:
                    pygame.draw.rect(screen, (255, 255, 255), (x * 10, y * 10, 10, 10))
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    pygame.quit()
    sys.exit(0)