import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import java.io.*;

public class ExportLabels extends GhidraScript {
    public void run() throws Exception {
        println("Starting export...");
        
        FunctionManager fm = getCurrentProgram().getFunctionManager();
        println("Got function manager, " + fm.getFunctionCount() + " functions");
        
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
        
        println("Exported " + count + " labels");
        println("Saved to: " + csvPath);
    }
}