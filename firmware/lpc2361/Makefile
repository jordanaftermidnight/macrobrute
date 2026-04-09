# MACROBRUTE LPC2361 Firmware Makefile

PROJECT = macrobrute
VERSION = 0.1.0

# Toolchain (arm-none-eabi from brew or system)
CC      = arm-none-eabi-gcc
AS      = arm-none-eabi-as
LD      = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy
OBJDUMP = arm-none-eabi-objdump
SIZE    = arm-none-eabi-size

# Directories
SRC_DIR     = src
BUILD_DIR   = build
INC_DIR     = include
STARTUP_DIR = startup
LINKER_DIR  = linker

# Find all source files
C_SRCS  = $(wildcard $(SRC_DIR)/*.c) \
           $(wildcard $(SRC_DIR)/core/*.c) \
           $(wildcard $(SRC_DIR)/drivers/*.c) \
           $(wildcard $(SRC_DIR)/synth/*.c) \
           $(wildcard $(SRC_DIR)/midi/*.c) \
           $(wildcard $(SRC_DIR)/ui/*.c) \
           $(wildcard $(SRC_DIR)/utils/*.c) \
           $(wildcard $(STARTUP_DIR)/*.c)

ASM_SRCS = $(wildcard $(STARTUP_DIR)/*.s)

# Object files
C_OBJS   = $(patsubst %.c,$(BUILD_DIR)/%.o,$(C_SRCS))
ASM_OBJS = $(patsubst %.s,$(BUILD_DIR)/%.o,$(ASM_SRCS))
OBJS     = $(C_OBJS) $(ASM_OBJS)

# CPU flags (ARM7TDMI-S)
CPU = -mcpu=arm7tdmi -mthumb-interwork

# Compiler flags
CFLAGS  = $(CPU) -g -O2 -Wall -Wextra -Wno-unused-parameter
CFLAGS += -I$(SRC_DIR) -I$(INC_DIR)
CFLAGS += -DDEBUG_LEVEL=2
CFLAGS += -ffunction-sections -fdata-sections
CFLAGS += -std=c99

# Linker flags
LDFLAGS  = $(CPU) -mthumb-interwork
LDFLAGS += -T $(LINKER_DIR)/lpc2361.ld
LDFLAGS += -nostartfiles
LDFLAGS += --specs=nano.specs
LDFLAGS += -Wl,--gc-sections
LDFLAGS += -Wl,-Map=$(BUILD_DIR)/$(PROJECT).map

# Targets
.PHONY: all clean flash monitor size disasm

all: $(BUILD_DIR)/$(PROJECT).hex $(BUILD_DIR)/$(PROJECT).bin
	@echo ""
	@echo "=== Build complete ==="
	@$(SIZE) $(BUILD_DIR)/$(PROJECT).elf
	@echo ""

$(BUILD_DIR)/$(PROJECT).elf: $(OBJS)
	@mkdir -p $(dir $@)
	$(LD) $(LDFLAGS) -o $@ $^

$(BUILD_DIR)/$(PROJECT).hex: $(BUILD_DIR)/$(PROJECT).elf
	$(OBJCOPY) -O ihex $< $@

$(BUILD_DIR)/$(PROJECT).bin: $(BUILD_DIR)/$(PROJECT).elf
	$(OBJCOPY) -O binary $< $@

# C compilation
$(BUILD_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c -o $@ $<

# Assembly
$(BUILD_DIR)/%.o: %.s
	@mkdir -p $(dir $@)
	$(AS) $(CPU) -o $@ $<

clean:
	rm -rf $(BUILD_DIR)

flash: $(BUILD_DIR)/$(PROJECT).hex
	./tools/flash.sh $<

monitor:
	./tools/monitor.sh

size: $(BUILD_DIR)/$(PROJECT).elf
	$(SIZE) -A $<

disasm: $(BUILD_DIR)/$(PROJECT).elf
	$(OBJDUMP) -d $< > $(BUILD_DIR)/$(PROJECT).lst

# Debug build (verbose logging)
debug: CFLAGS += -DDEBUG_LEVEL=3 -O0
debug: all

# Release build (no debug, optimized)
release: CFLAGS += -DDEBUG_LEVEL=0 -Os
release: all
