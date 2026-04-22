// Aggressive function detection and labeling
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
import java.util.regex.*;

public class AggressiveLabels extends GhidraScript {
    public void run() throws Exception {
        String headerPath = "/Users/jordan_after_midnight/Projects/music/macrobrute/firmware/ghidra_decompiled.h";
        
        println("=== Step 1: Reading header file ===");
        
        java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.FileReader(headerPath));
        StringBuilder content = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            content.append(line).append("\n");
        }
        reader.close();
        
        Pattern pattern = Pattern.compile("(thunk_)?FUN_([0-9a-fA-F]{8})\\s*\\(");
        Matcher matcher = pattern.matcher(content.toString());
        
        java.util.Set<Integer> targetAddrs = new java.util.HashSet<>();
        java.util.Map<Integer, String> addrToName = new java.util.HashMap<>();
        
        while (matcher.find()) {
            String prefix = matcher.group(1);
            String addrStr = matcher.group(2);
            int addrInt = Integer.parseInt(addrStr, 16);
            String name = (prefix != null ? "thunk_FUN_" : "FUN_") + addrStr;
            
            if (!targetAddrs.contains(addrInt)) {
                targetAddrs.add(addrInt);
                addrToName.put(addrInt, name);
            }
        }
        
        println("Found " + targetAddrs.size() + " unique target addresses");
        
        // Step 2: Run more aggressive function detection
        println("\n=== Step 2: Running aggressive function detection ===");
        
        FunctionManager fm = currentProgram.getFunctionManager();
        int existingCount = fm.getFunctionCount();
        println("Existing functions: " + existingCount);
        
        // Try to create functions at all target addresses
        int created = 0;
        for (int addrInt : targetAddrs) {
            Address addrObj = toAddr(addrInt);
            Function existing = fm.getFunctionAt(addrObj);
            
            if (existing == null) {
                Function newFunc = createFunction(addrObj, addrToName.get(addrInt));
                if (newFunc != null) {
                    created++;
                }
            }
        }
        
        println("Created " + created + " new functions");
        
        // Step 3: Apply all labels
        println("\n=== Step 3: Applying labels ===");
        
        int count = 0;
        int failed = 0;
        
        for (int addrInt : targetAddrs) {
            Address addrObj = toAddr(addrInt);
            Function func = fm.getFunctionAt(addrObj);
            
            if (func != null) {
                String name = addrToName.get(addrInt);
                func.setName(name, SourceType.USER_DEFINED);
                count++;
            } else {
                failed++;
            }
        }
        
        println("Applied " + count + " labels!");
        println("Failed (no function): " + failed);
        
        // List some failed addresses for debugging
        if (failed > 0) {
            println("\n=== First 20 failed addresses ===");
            int shown = 0;
            for (int addrInt : targetAddrs) {
                if (fm.getFunctionAt(toAddr(addrInt)) == null && shown < 20) {
                    println(String.format("0x%04x - %s", addrInt, addrToName.get(addrInt)));
                    shown++;
                }
            }
        }
    }
}