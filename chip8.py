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
        funcmap[self.opcode & 0xF0FF]()

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




