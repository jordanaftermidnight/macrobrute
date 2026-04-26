"""EFFIGY bridge constants — GENERATED, do not edit by hand.

Generated from EFFIGY/firmware/src/macrobrute_bridge.h by
tools/sync_effigy_constants.py. The C header is the authoritative
source of register addresses, event types, and error codes; this
module mirrors them for the MACROBRUTE Pico firmware to import.

Source revision: unknown
"""

from micropython import const

# ───────────────────────────────────────────────────────────────────
# Register addresses
# ───────────────────────────────────────────────────────────────────
REG_DEVICE_ID         = const(0x00)  # 0x00
REG_FW_VERSION_MAJOR  = const(0x01)  # 0x01
REG_FW_VERSION_MINOR  = const(0x02)  # 0x02
REG_CAPABILITIES      = const(0x03)  # 0x03
REG_HEARTBEAT         = const(0x0F)  # 0x0F
REG_MASS              = const(0x10)  # 0x10
REG_ENTROPY           = const(0x11)  # 0x11
REG_POSITION          = const(0x12)  # 0x12
REG_TEXTURE           = const(0x13)  # 0x13
REG_MIX               = const(0x14)  # 0x14
REG_FOLD              = const(0x15)  # 0x15
REG_FILTER            = const(0x16)  # 0x16
REG_REVERB            = const(0x17)  # 0x17
REG_CRUSH             = const(0x18)  # 0x18
REG_DESTRUCTION_MACRO = const(0x19)  # 0x19
REG_ENGINE_INDEX      = const(0x1A)  # 0x1A
REG_HARMONIZER_INT    = const(0x1B)  # 0x1B
REG_MICRO_LFO_RATE    = const(0x1C)  # 0x1C
REG_ENV_SHAPE         = const(0x1D)  # 0x1D
REG_TRIG_VOICE_1      = const(0x30)  # 0x30
REG_FREEZE            = const(0x31)  # 0x31
REG_PANEL_OVERRIDE    = const(0x32)  # 0x32
REG_LEVEL_L           = const(0x40)  # 0x40
REG_LEVEL_R           = const(0x41)  # 0x41
REG_CLIP_FLAGS        = const(0x42)  # 0x42
REG_ENGINE_NAME       = const(0x43)  # 0x43
REG_PRESET_SLOT       = const(0x44)  # 0x44
REG_CPU_LOAD          = const(0x45)  # 0x45
REG_GRAIN_BUFFER_FILL = const(0x46)  # 0x46
REG_FREEZE_STATE      = const(0x47)  # 0x47
REG_ENV_STAGE         = const(0x48)  # 0x48
REG_CV_OUT_1_VALUE    = const(0x49)  # 0x49
REG_CV_OUT_2_VALUE    = const(0x4A)  # 0x4A
REG_EVENT_COUNT       = const(0x60)  # 0x60
REG_EVENT_POP         = const(0x61)  # 0x61
REG_EVENT_CLEAR       = const(0x62)  # 0x62
REG_PAIR_ACTIVE       = const(0x80)  # 0x80
REG_CLOCK_MASTER      = const(0x81)  # 0x81
REG_MENU_OWNER        = const(0x82)  # 0x82
REG_FOCUS_OWNER       = const(0x83)  # 0x83
REG_CLOCK_TICK        = const(0x90)  # 0x90
REG_CLOCK_BPM         = const(0x91)  # 0x91
REG_TRANSPORT_STATE   = const(0x92)  # 0x92
REG_PRESET_RECALL     = const(0x93)  # 0x93
REG_SRC_COUNT         = const(0xA0)  # 0xA0
REG_SRC_NAME          = const(0xA1)  # 0xA1
REG_ERROR_STATUS      = const(0xF0)  # 0xF0
REG_RESET_BRIDGE      = const(0xFF)  # 0xFF

# ───────────────────────────────────────────────────────────────────
# Event type tags (first byte returned by EVENT_POP at 0x61)
# ───────────────────────────────────────────────────────────────────
EVENT_ENCODER = const(0x01)
EVENT_BUTTON  = const(0x02)
EVENT_PRESET  = const(0x03)
EVENT_ENGINE  = const(0x04)
EVENT_CLIP    = const(0x05)
EVENT_PANEL   = const(0x06)

# ───────────────────────────────────────────────────────────────────
# Error codes (register ERROR_STATUS at 0xF0)
# ───────────────────────────────────────────────────────────────────
ERR_OK                   = const(0x00)
ERR_BAD_REGISTER         = const(0x01)
ERR_WRITE_TO_READONLY    = const(0x02)
ERR_READ_FROM_WRITEONLY  = const(0x03)
ERR_EVENT_QUEUE_OVERFLOW = const(0x04)
ERR_HEARTBEAT_TIMEOUT    = const(0x05)
