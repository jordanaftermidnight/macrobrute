# Apply labels to MicroBrute firmware - headless version
# Usage: Ghidra/support/analyzeHeadless <project-dir> <repo-name> -import <firmware-file> -scriptPath <path-to-this-script> -postScript apply_labels_headless.py

import re
from ghidra.app.script import GhidraScript
from ghidra.program.model.address import *

class ApplyLabelsHeadless(GhidraScript):
    def run(self):
        header_path = "/Users/jordan_after_midnight/Projects/music/macrobrute/firmware/ghidra_decompiled.h"
        
        self.print("Reading header file: " + header_path)
        
        with open(header_path, 'r') as f:
            content = f.read()

        # Pattern to match function declarations
        pattern = r'(thunk_)?FUN_([0-9a-fA-F]{8})\s*\('
        matches = re.findall(pattern, content)
        
        self.print("Found %d function names" % len(matches))

        seen = set()
        count = 0
        failed = 0
        
        for prefix, addr in matches:
            addr_int = int(addr, 16)
            if addr_int not in seen:
                seen.add(addr_int)
                name = "thunk_FUN_%s" % addr if prefix else "FUN_%s" % addr
                try:
                    addr_obj = toAddr(addr_int)
                    func = getFunctionAt(addr_obj)
                    if func:
                        func.setName(name)
                        count += 1
                    else:
                        # Try to create function if it doesn't exist
                        func = createFunction(addr_obj, name)
                        if func:
                            count += 1
                        else:
                            failed += 1
                except Exception as e:
                    failed += 1

        self.print("Applied %d labels!" % count)
        self.print("Failed or not found: %d" % failed)