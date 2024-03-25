import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.Interval;
import org.antlr.v4.runtime.tree.ParseTreeWalker;


/**
 * Extracts information from Javafiles.
 * Imports, packages,  class variables, enums.
 */
public class ContextExtractor extends JavaParserBaseListener {
    String[] methodNamesToMatch;
    File currentJavaFile;
    File outputDir;
    ArrayList<String> metaData;
    CharStream input;

    public ContextExtractor(String outputDir) {
        this.outputDir = new File(outputDir);
        this.outputDir.mkdirs();
    }


    @Override public void enterImportDeclaration(JavaParser.ImportDeclarationContext ctx) {
        if(ctx != null) {
            int a = ctx.start.getStartIndex();
            int b = ctx.stop.getStopIndex();
            Interval interval = new Interval(a, b);
            String importString = input.getText(interval);
            metaData.add(importString);
        }
    }

     //Parse one term by one
      @Override public void enterClassDeclaration(JavaParser.ClassDeclarationContext ctx) {
        if(ctx != null) {
            int a = ctx.start.getStartIndex();
            int b = ctx.stop.getStopIndex();
            Interval interval = new Interval(a, b);
            String importString = input.getText(interval);
            metaData.add(importString);
        }
       }


    public void walkDirectory( File dir ) {
        for( File child : Objects.requireNonNull(dir.listFiles())) {
            if( child.isDirectory() ) {
                walkDirectory( child );
            } else {
                if (child.getName().endsWith(".java")) {
                    parseFile(child);
                }
            }
        }
    }


    private void parseFile(File child) {
        try {
            currentJavaFile = child;
            metaData = new ArrayList<>();
            input = new ANTLRFileStream(child.getPath());
            JavaLexer lexer = new JavaLexer(input);
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            JavaParser parser = new JavaParser(tokens);
            ParserRuleContext tree = parser.compilationUnit();
            ParseTreeWalker walker = new ParseTreeWalker();
            walker.walk(this, tree);
            if (!metaData.isEmpty()) {
                writeOutputFile();
            }
        } catch (IOException e) {
            System.err.println("Could not parse " + child.getPath());
            e.printStackTrace();
        }
    }

    private void writeOutputFile() {
        String nameWithExtension =  this.currentJavaFile.getName();
        String context = nameWithExtension.split("\\.")[0] + "_context";
        File outFile = new File(this.outputDir, context);
        try {
            // Write methods to test
            FileWriter fw = new FileWriter(outFile);
            fw.close();
            fw = new FileWriter(outFile);
            // Write metadata
            outFile = new File(this.outputDir, context);
            for(String line:this.metaData) {
                fw.write(line);
                fw.write("\n");
            }
            fw.close();

        } catch (Exception e) {
            System.err.println("Could not write output file " + outFile);
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws IOException {
        File luhnCalculator = new File("/Users/glacierali/repos/MEX/poc/Parser/src/main/java/testclasses");
        String outputDir = "/Users/glacierali/repos/MEX/poc/Parser/src/main/java/output";
        ContextExtractor extractor = new ContextExtractor(outputDir);
        extractor.walkDirectory(luhnCalculator);
    }

}