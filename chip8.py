import pyglet


class Chip8 (pyglet.window.Window):
    fontset = [
        0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
        0x20, 0x60, 0x20, 0x20, 0x70,  # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
        0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
        0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
        0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
        0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
        0xF0, 0x80, 0xF0, 0x80, 0x80   # F
    ]

    """ 
        Definitions for the Opcodes
    """
    def _0NNN(self):
        self.funcmap[self.opcode & 0xF0FF]()

    # 0x00E0: Clears the screen
    def _00E0(self):
        for i in range(len(self.graphics)):
            self.graphics[i] = 0
        self.draw_flag = True

    # 0x00EE: Returns from a subroutine
    def _00EE(self):
        self.sp -= 1
        self.pc  = self.stack[self.sp]

    # 0x1NNN: Jumps to address NNN
    def _1NNN(self):
        self.pc = self.opcode & 0x0FFF

    # 0x2NNN: Calls subroutine at NNN
    def _2NNN(self):
        self.stack[self.sp] = self.pc
        self.sp += 1
        self.pc = self.opcode & 0x0FFF

    # 0x3XNN: Skips instruction if Vx equals NN
    def _3XNN(self):
        if self.registers[self.vx] == (self.opcode & 0x00FF):
            self.pc += 2

    # 0x4XNN: Skips instruction if Vx doesn't equal NN
    def _4XNN(self):
        if self.registers[self.vx] != (self.opcode & 0x00FF):
            self.pc += 2

    # 0x5XY0: Skips instruction if Vx equals Vy
    def _5XY0(self):
        if self.registers[self.vx] == self.registers[self.vy]:
            self.pc += 2

    # 0x6XNN: Sets Vx to NN
    def _6XNN(self):
        self.registers[self.vx] = (self.opcode & 0x00FF)

    # 0x7XNN: Adds NN to Vx
    def _7XNN(self):
        self.registers[self.vx] += (self.opcode & 0x00FF)

    def _8NNN(self):
        self.funcmap[(self.opcode & 0xF00F) + 0xFF0]()

    # 0x8XY0: Sets Vx to Vy
    def _8XY0(self):
        self.registers[self.vx] = self.registers[self.vy]

    # 0x8XY1: Sets Vx to Vx || Vy
    def _8XY1(self):
        self.registers[self.vx] |= self.registers[self.vy]

    # 0x8XY2: Sets Vx to Vx && Vy
    def _8XY2(self):
        self.registers[self.vx] &= self.registers[self.vy]

    # 0x8XY3: Sets Vx to Vx XOR Vy
    def _8XY3(self):
        self.registers[self.vx] ^= self.registers[self.vy]

    # 0x8XY4: Adds Vy to Vx. Sets VF to 1 if there's carry
    def _8XY4(self):
        if (self.registers[self.vx] + self.registers[self.vy]) > 0xFF:
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0

        self.registers[self.vx] += self.registers[self.vy]

    # 0x8XY5: Subtracts Vy from Vx. Sets VF to 0 if there's borrow, 1 otherwise
    def _8XY5(self):
        if self.registers[self.vx] < self.registers[self.vy]:
            self.registers[0xF] = 0
        else:
            self.registers[0xF] = 1

        self.registers[self.vx] -= self.registers[self.vy]

    # 0x8XY6: Shifts Vx right by one. Sets VF to the LSB of Vx before-shift
    def _8XY6(self):
        self.registers[0xF] = self.registers[self.vx] & 0x1
        self.registers[self.vx] >>= 1

    # 0x8XY7: Sets Vx to Vy - Vx. Sets VF to 0 if there's borrow, 1 otherwise
    def _8XY7(self):
        if self.registers[self.vx] > self.registers[self.vy]:
            self.registers[0xF] = 0
        else:
            self.registers[0xF] = 1

        self.registers[self.vx] = self.registers[self.vy] - self.registers[self.vx]

    # 0x8XYE: Shifts Vx left by one. Sets VF to the MSB of Vx before-shift
    def _8XYE(self):
        self.registers[0xF] = self.registers[self.vx] >> 7
        self.registers[self.vx] <<= 1

    # 0x9XY0: Skips instruction if Vx != Vy
    def _9XY0(self):
        if self.registers[self.vx] != self.registers[self.vy]:
            self.pc += 2

    # 0xANNN: Sets I to the address NNN
    def _ANNN(self):
        self.index = self.opcode & 0x0FFF

    # 0xBNNN: Jumps to the address NNN plus V0
    def _BNNN(self):
        self.pc = (self.opcode & 0x0FFF) + self.registers[0]

    # 0xCXNN: Sets Vx to NN && random number
    def _CXNN(self):
        self.registers[self.vx] = (self.opcode & 0x00FF) & random.randint(0x0, 0xFF)

    # 0xDXYN: Draws a 8xN sprite at coordinate (Vx, Vy). 
    # Sets VF to 1 if any pixels are flipped.
    # Each row of 8 pixels is read starting at memory location I
    def _DXYN(self):
        x = self.registers[self.vx]
        y = self.registers[self.vy]

        height = self.opcode & 0x000F
        pixel = 0

        self.registers[0xF] = 0

        for y_line in range(height):
            pixel = self.memory[self.index + y_line]
            for x_line in range(8):
                if pixel & (0x80 >> x_line) != 0:
                    if self.graphics[x + x_line + ((y + y_line) * 64)] == 1:
                        self.registers[0xF] = 1
                    self.graphics[x + x_line + ((y + y_line) * 64)] ^= 1
                    
        self.draw_flag = True

    def _ENNN(self):
        self.funcmap(self.opcode & 0xF0FF)()

    # 0xEX9E: Skips instruction if key stored in Vx is pressed
    def _EX9E(self):
        if self.key[self.registers[self.vx]] != 0:
            self.pc += 2

    # 0xEXA1: Skips instruction if key stored in Vx is not pressed
    def _EXA1(self):
        if self.key[self.registers[self.vx]] == 0:
            self.pc += 2

    def _FNNN(self):
        self.funcmap(self.opcode & 0xF0FF)()

    # 0xFX07: Sets Vx to the value of delay timer
    def _FX07(self):
        self.registers[self.vx] = self.delay_timer

    # 0xFX0A: Waits for a key press and stores its value in Vx
    def _FX0A(self):
        key_press = False

        for i in range(16):
            if self.key[i] != 0:
                self.registers[self.vx] = i
                key_press = True

        # If no key was pressed, return and repeat next cycle
        if !key_press:
            self.pc -= 2

    # 0xFX15: Sets delay timer to Vx
    def _FX15(self):
        self.delay_timer = self.registers[self.vx]

    # 0xFX18: Sets sound timer to Vx
    def _FX18(self):
        self.sound_timer = self.registers[self.vx]

    # 0xFX1E: Adds Vx to I. Sets VF if in overflow range (undocumented)
    def _FX1E(self):
        if self.index + self.registers[self.vx] > 0xFF:
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0

        self.index += self.registers[self.vx]

        
    
    def __init__(self):
        self.pc     = 0x200
        self.opcode = 0
        self.index  = 0
        self.sp     = 0

        self.memory    = [0] * 4096
        self.registers = [0] * 16
        self.stack     = [0] * 16
        self.key       = [0] * 16
        self.graphics  = [0] * 32 * 64

        self.delay_timer = 0
        self.sound_timer = 0

        self.draw_flag = False

        for i in range(len(fontset)):
            self.memory[i] = fontset[i]

    def load_rom(self, rom_path):
        rom = open(rom_path, "rb").read()

        for i in range(len(rom)):
            self.memory[i + 0x200] = ord(rom[i])

    def emulate_cycle(self):
        """ Fetch
            Get two bytes from memory, combine them into opcode word
        """
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]

        """ Decode
            Reads first nibble from opcode, switches to and executes matching
            instruction.
            Vx and Vy represent general purpose registers, with associated 
            values stored in the 2nd and 3rd nibbles.
            The PC is updated before executing the opcode in order to 
            jump-related opcodes to work.
        """
        self.vx = (self.opcode & 0x0F00) >> 8
        self.vy = (self.opcode & 0x00F0) >> 4

        self.pc += 2

        self.funcmap[self.opcode & 0xF000]()

        """ Timers
            Update delay and sound timers
        """
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1
            if self.sound_timer == 0:
                self.buzz.play()




