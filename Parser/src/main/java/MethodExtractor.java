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
 * Imports, packages, methods, class variables, enums.
 */
public class MethodExtractor extends JavaParserBaseListener {
    String[] methodNamesToMatch;
    File currentJavaFile;
    File outputDir;
    List<Interval> intervals;
    ArrayList<String> metaData;
    CharStream input;

    public MethodExtractor(String[] methodNames, String outputDir) {
        this.methodNamesToMatch = methodNames;
        this.outputDir = new File(outputDir);
        this.outputDir.mkdirs();
    }

    @Override public void enterMethodDeclaration(JavaParser.MethodDeclarationContext ctx) {
        JavaParser.IdentifierContext identifier = ctx.identifier();
        if (identifier!=null) {
            for (String name:methodNamesToMatch) {
                if (identifier.getText().equals(name)) {
                    int a = ctx.start.getStartIndex();
                    int b = ctx.stop.getStopIndex();
                    Interval interval = new Interval(a,b);
                    intervals.add(interval);
                }
            }
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
            intervals = new ArrayList<>();
            input = new ANTLRFileStream(child.getPath());
            JavaLexer lexer = new JavaLexer(input);
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            JavaParser parser = new JavaParser(tokens);
            ParserRuleContext tree = parser.compilationUnit();
            ParseTreeWalker walker = new ParseTreeWalker();
            walker.walk(this, tree);
            if (!intervals.isEmpty()) {
                writeOutputFile();
            }
        } catch (IOException e) {
            System.err.println("Could not parse " + child.getPath());
            e.printStackTrace();
        }
    }

    private void writeOutputFile() {
        String nameWithExtension =  this.currentJavaFile.getName();
        String methodsToTest = nameWithExtension.split("\\.")[0] + "_methods";
        File outFile = new File(this.outputDir, methodsToTest);
        try {
            // Write methods to test
            FileWriter fw = new FileWriter(outFile);
            for (Interval interval:this.intervals) {
                fw.write(input.getText(interval));
                fw.write("\n\n");
            }
            fw.close();

        } catch (Exception e) {
            System.err.println("Could not write output file " + outFile);
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws IOException {
        String[] methodNames = {"calcLuhn", "validateLuhn", "someMethod", "someOtherMethod"};
        File luhnCalculator = new File("/Users/glacierali/repos/MEX/poc/Parser/src/main/java/testclasses");
        String outputDir = "/Users/glacierali/repos/MEX/poc/Parser/src/main/java/output";
        MethodExtractor extractor = new MethodExtractor(methodNames, outputDir);
        extractor.walkDirectory(luhnCalculator);
    }

}