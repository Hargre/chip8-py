import pyglet
import random

from pyglet.sprite import Sprite

KEY_MAP = {
    pyglet.window.key._1: 0x1,
    pyglet.window.key._2: 0x2,
    pyglet.window.key._3: 0x3,
    pyglet.window.key._4: 0xC,
    pyglet.window.key.Q:  0x4,
    pyglet.window.key.W:  0x5,
    pyglet.window.key.E:  0x6,
    pyglet.window.key.R:  0xD,
    pyglet.window.key.A:  0x7,
    pyglet.window.key.S:  0x8,
    pyglet.window.key.D:  0x9,
    pyglet.window.key.F:  0xE,
    pyglet.window.key.Z:  0xA,
    pyglet.window.key.X:  0,
    pyglet.window.key.C:  0xB,
    pyglet.window.key.V:  0xF
}

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
        Pyglet resources
    """

    pixel = pyglet.resource.image('pixel.png')
    buzz  = pyglet.resource.media('buzz.wav', streaming = False)

    batch = pyglet.graphics.Batch()
    sprites = []
    for i in range(0, 2048):
        sprites.append(pyglet.sprite.Sprite(pixel, batch = batch))

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
        if not key_press:
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

    # 0xFX29: Sets I to the location of the sprite for the character in Vx.
    # Characters are represented by a 4x5 font.
    def _FX29(self):
        self.index = self.registers[self.vx] * 0x5

    # 0xFX33: Stores the BCD representation of Vx.
    # Stored at address I (MSD), I + 1, I + 2 (LSD)
    def _FX33(self):
        self.memory[self.index]     =  self.registers[self.vx] / 100
        self.memory[self.index + 1] = (self.registers[self.vx] / 10)  % 10
        self.memory[self.index + 2] = (self.registers[self.vx] % 100) % 10 

    # 0xFX55: Stores V0 to Vx (including Vx) in memory, starting at address I
    def _FX55(self):
        for i in range(self.vx + 1):
            self.memory[self.index + i] = self.registers[i]

    # 0xFX65: Fills V0 to Vx (including Vx) with values from memory starting at address I
    def _FX65(self):
        for i in range(self.vx + 1):
            self.registers[i] = self.memory[self.index + i]

    def __init__(self, *args, **kwargs):
        super(Chip8, self).__init__(*args, **kwargs)

        self.funcmap = {
            0x0000: self._0NNN,
            0x00E0: self._00E0,
            0x00EE: self._00EE,
            0x1000: self._1NNN,
            0x2000: self._2NNN,
            0x3000: self._3XNN,
            0x4000: self._4XNN,
            0x5000: self._5XY0,
            0x6000: self._6XNN,
            0x7000: self._7XNN,
            0x8000: self._8NNN,
            0x8FF0: self._8XY0,
            0x8FF1: self._8XY1,
            0x8FF2: self._8XY2,
            0x8FF3: self._8XY3,
            0x8FF4: self._8XY4,
            0x8FF5: self._8XY5,
            0x8FF6: self._8XY6,
            0x8FF7: self._8XY7,
            0x8FFE: self._8XYE,
            0x9000: self._9XY0,
            0xA000: self._ANNN,
            0xB000: self._BNNN,
            0xC000: self._CXNN,
            0xD000: self._DXYN,
            0xE000: self._ENNN,
            0xE09E: self._EX9E,
            0xE0A1: self._EXA1,
            0xF000: self._FNNN,
            0xF007: self._FX07,
            0xF00A: self._FX0A,
            0xF015: self._FX15,
            0xF018: self._FX18,
            0xF01E: self._FX1E,
            0xF029: self._FX29,
            0xF033: self._FX33,
            0xF055: self._FX55,
            0xF065: self._FX65
        }

        self.clear()

        self.pc     = 0x200
        self.opcode = 0
        self.index  = 0
        self.sp     = 0

        self.memory    = [0]*4096
        self.registers = [0]*16
        self.stack     = [0]*16
        self.key       = [0]*16
        self.graphics  = [0]*32*64

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

    def draw(self):
        if self.draw_flag:
            line_counter = 0
            for i in range(2048):
                if self.graphics[i] == 1:
                    self.pixel.blit((i%64)*10, 310 - ((i/64)*10))
            self.flip()
            self.draw_flag = false

    def on_key_press(self, symbol, modifiers):
        if symbol in KEY_MAP.keys():
            self.key[KEY_MAP[symbol]] = 1
            if self.key_wait:
                self.key_wait = False
        else:
            super(Chip8, self).on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        if symbol in KEY_MAP.keys():
            self.keys[KEY_MAP[symbol]] = 0



