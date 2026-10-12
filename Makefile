# Build the ROM. Run inside WSL from the repo root; paths are relative to the repo root.
AS      = arm-none-eabi-as
LD      = arm-none-eabi-ld
OBJCOPY = arm-none-eabi-objcopy

BUILD = private/build
ROM   = $(BUILD)/yugioh.gba
ELF   = $(BUILD)/yugioh.elf
OBJ   = $(BUILD)/rom.o

.PHONY: all compare clean

all: $(ROM)

$(OBJ): asm/rom.s private/baserom.gba
	@mkdir -p $(BUILD)
	$(AS) -o $@ asm/rom.s

$(ELF): $(OBJ) ld_script.txt
	$(LD) -T ld_script.txt -o $@ $(OBJ)

$(ROM): $(ELF)
	$(OBJCOPY) -O binary $< $@

compare: $(ROM)
	sha1sum -c config/yugioh.sha1

clean:
	rm -f $(OBJ) $(ELF) $(ROM)
