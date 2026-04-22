// Apply labels to MicroBrute firmware - Java version
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
import java.util.regex.*;

public class ApplyLabelsHeadless extends GhidraScript {
    public void run() throws Exception {
        String headerPath = "/Users/jordan_after_midnight/Projects/music/macrobrute/firmware/ghidra_decompiled.h";
        
        println("Reading header file: " + headerPath);
        
        java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.FileReader(headerPath));
        StringBuilder content = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            content.append(line).append("\n");
        }
        reader.close();
        
        Pattern pattern = Pattern.compile("(thunk_)?FUN_([0-9a-fA-F]{8})\\s*\\(");
        Matcher matcher = pattern.matcher(content.toString());
        
        java.util.Set<Integer> seen = new java.util.HashSet<>();
        int count = 0;
        int failed = 0;
        
        while (matcher.find()) {
            String prefix = matcher.group(1);
            String addrStr = matcher.group(2);
            int addrInt = Integer.parseInt(addrStr, 16);
            
            if (!seen.contains(addrInt)) {
                seen.add(addrInt);
                String name = (prefix != null ? "thunk_FUN_" : "FUN_") + addrStr;
                
                try {
                    Address addrObj = toAddr(addrInt);
                    Function func = getFunctionAt(addrObj);
                    if (func != null) {
                        func.setName(name, SourceType.USER_DEFINED);
                        count++;
                    } else {
                        func = createFunction(addrObj, name);
                        if (func != null) {
                            count++;
                        } else {
                            failed++;
                        }
                    }
                } catch (Exception e) {
                    failed++;
                }
            }
        }
        
        println("Found " + seen.size() + " unique function names");
        println("Applied " + count + " labels!");
        println("Failed or not found: " + failed);
    }
}