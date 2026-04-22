##  IP: GHIDRA
# Apply function labels to MicroBrute firmware

#@category Firmware
#@runtime Jython

import re
from ghidra.program.model.address import *
from ghidra.program.model.listing import *

header_path = "/Users/jordan_after_midnight/Projects/music/macrobrute/firmware/ghidra_decompiled.h"
pattern = r'(thunk_)?FUN_([0-9a-fA-F]{8})\s*\('

with open(header_path) as f:
    content = f.read()

matches = re.findall(pattern, content)
print("Found %d function names" % len(matches))

seen = set()
count = 0
for prefix, addr in matches:
    addr_int = int(addr, 16)
    if addr_int not in seen:
        seen.add(addr_int)
        name = "%sFUN_%s" % (prefix, addr) if prefix else "FUN_%s" % addr
        try:
            func = getFunctionAt(toAddr(addr_int))
            if func:
                func.setName(name)
                count += 1
        except:
            pass

print("Applied %d labels!" % count)