# Apply labels from header file
# @ category Scripts
# @ id apply_labels

import re
from ghidra.app.script import GhidraScript

class ApplyLabels(GhidraScript):
    def run(self):
        header_path = "/Users/jordan_after_midnight/Projects/music/macrobrute/firmware/ghidra_decompiled.h"
        pattern = r'(thunk_)?FUN_([0-9a-fA-F]{8})\s*\('

        with open(header_path) as f:
            content = f.read()

        matches = re.findall(pattern, content)
        self.print(f"Found {len(matches)} function names")

        seen = set()
        count = 0
        for prefix, addr in matches:
            addr_int = int(addr, 16)
            if addr_int not in seen:
                seen.add(addr_int)
                name = f"{prefix}FUN_{addr}" if prefix else f"FUN_{addr}"
                try:
                    func = getFunctionAt(toAddr(addr_int))
                    if func:
                        func.setName(name)
                        count += 1
                except:
                    pass

        self.print(f"Applied {count} labels!")