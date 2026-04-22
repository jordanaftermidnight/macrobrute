// Apply labels AND export in one run
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.address.*;
import java.util.regex.*;
import java.io.*;

public class LabelAndExport extends GhidraScript {
    public void run() throws Exception {
        // 1. Read header file
        String headerPath = "/Users/jordan_after_midnight/Projects/music/macrobrute/firmware/ghidra_decompiled.h";
        
        BufferedReader reader = new BufferedReader(new FileReader(headerPath));
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
        
        println("Found " + targetAddrs.size() + " target addresses");
        
        // 2. Create functions and label
        FunctionManager fm = currentProgram.getFunctionManager();
        
        for (int addrInt : targetAddrs) {
            Address addrObj = toAddr(addrInt);
            Function func = fm.getFunctionAt(addrObj);
            
            if (func == null) {
                func = createFunction(addrObj, addrToName.get(addrInt));
            }
            
            if (func != null) {
                func.setName(addrToName.get(addrInt), SourceType.USER_DEFINED);
            }
        }
        
        // 3. Export to CSV
        String csvPath = "/Users/jordan_after_midnight/Projects/music/macrobrute/firmware/labels_export.csv";
        PrintWriter csv = new PrintWriter(new FileWriter(csvPath));
        csv.println("Address,Name");
        
        int count = 0;
        for (Function func : fm.getFunctions(true)) {
            String name = func.getName();
            String addr = func.getEntryPoint().toString();
            csv.println(addr.substring(1) + "," + name);
            count++;
        }
        
        csv.close();
        
        println("Exported " + count + " labels to: " + csvPath);
    }
}