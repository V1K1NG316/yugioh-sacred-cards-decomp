# Build the ROM. Run inside WSL from the repo root; paths are relative to the repo root.
#
# `make compare`      -- build private/asm/rom.s (the Y3 disassembly) and compare
#                        the result with the original: byte-identical or bust.
# `make compare-shell`-- Y1 shell build (asm/rom.s, the original bytes linked back).
AS      = arm-none-eabi-as
LD      = arm-none-eabi-ld
OBJCOPY = arm-none-eabi-objcopy

BUILD = private/build
ROM   = $(BUILD)/yugioh.gba
ELF   = $(BUILD)/yugioh.elf
OBJ   = $(BUILD)/rom.o
SRC   = private/asm/rom.s
# The sources rom.s includes (one file per function + the data files): make must
# rebuild when one of them is edited, e.g. by the C4 mutation test.
PARTS = $(wildcard private/asm/funcs/*.s) $(wildcard private/asm/data/*.s)

SHELL_OBJ = $(BUILD)/rom_shell.o
SHELL_ELF = $(BUILD)/yugioh_shell.elf
SHELL_ROM = $(BUILD)/yugioh_shell.gba

.PHONY: all compare compare-shell clean

all: $(ROM)

# The disassembly is generated, not authored; keep it out of make (see scripts/disasm.sh).
$(SRC):
	@echo "$(SRC) is missing -- generate it: wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/disasm.sh"
	@exit 1

$(OBJ): $(SRC) $(PARTS) asm/macros.inc ld_script.txt
	@mkdir -p $(BUILD)
	$(AS) -o $@ $(SRC)

$(ELF): $(OBJ) ld_script.txt
	$(LD) -T ld_script.txt -o $@ $(OBJ)

$(ROM): $(ELF)
	$(OBJCOPY) -O binary $< $@

compare: $(ROM)
	sha1sum -c config/yugioh.sha1

# Y1 shell build: asm/rom.s .incbin's the original, so this only proves the toolchain
# and the linker script still produce the ROM.
$(SHELL_OBJ): asm/rom.s
	@mkdir -p $(BUILD)
	$(AS) -o $@ asm/rom.s

$(SHELL_ELF): $(SHELL_OBJ) ld_script.txt
	$(LD) -T ld_script.txt -o $@ $(SHELL_OBJ)

$(SHELL_ROM): $(SHELL_ELF)
	$(OBJCOPY) -O binary $< $@

compare-shell: $(SHELL_ROM)
	sed 's|private/build/yugioh.gba|$(SHELL_ROM)|' config/yugioh.sha1 | sha1sum -c -

clean:
	rm -f $(OBJ) $(ELF) $(ROM) $(SHELL_OBJ) $(SHELL_ELF) $(SHELL_ROM)
