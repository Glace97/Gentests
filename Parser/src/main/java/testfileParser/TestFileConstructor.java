package testfileParser;

import org.antlr.v4.runtime.ANTLRFileStream;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.misc.Interval;
import org.antlr.v4.runtime.tree.ParseTreeWalker;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;

public class TestFileConstructor extends JavaParserBaseListener {
    File outputDir;

    CharStream input;

    HashSet<String> imports;
    HashSet<String> classContents;
     String testFilePath;

    String packageName;

    HashSet<String> entries;

     String generatedTestFilePath;

    public TestFileConstructor(String outputDir, String testFilePath, String generatedTestFilePath) {
//      existingTestFileImports = new ArrayList<>();
//      generatedTestFileImports = new ArrayList<>();
        this.outputDir = new File(outputDir);
        this.outputDir.mkdirs();
        imports = new HashSet<>();
        this.testFilePath = testFilePath;
        this.generatedTestFilePath = generatedTestFilePath;
        entries = new HashSet<>();
        classContents = new HashSet<>();
    }


    // Read existing imports from the test file
    @Override public void enterImportDeclaration(JavaParser.ImportDeclarationContext ctx) {
        if (ctx != null) {
            int startIndex = ctx.start.getStartIndex();
            int stopIndex = ctx.stop.getStopIndex();
            Interval interval = new Interval(startIndex, stopIndex);

            imports.add(input.getText(interval));
        }
    }

    @Override
    public void enterPackageDeclaration(JavaParser.PackageDeclarationContext ctx) {
        if(ctx != null) {
            int startIndex = ctx.start.getStartIndex();
            int stopIndex = ctx.stop.getStopIndex();
            Interval interval = new Interval(startIndex, stopIndex);

            String foundPackage = input.getText(interval);
            if (!foundPackage.isEmpty()) {
                packageName = foundPackage;
            }

        }
    }

    private boolean isNestedClass(ParserRuleContext context) {
        ParserRuleContext parent = context.getParent();
        while (parent != null) {
            if (parent instanceof JavaParser.ClassBodyContext) {
                return true;
            }
            parent = parent.getParent();
        }
        return false;
    }

    @Override
    public void enterClassBody(JavaParser.ClassBodyContext ctx) {
        if(ctx != null && !isNestedClass(ctx)) {
            int startIndex = ctx.start.getStartIndex();
            int stopIndex = ctx.stop.getStopIndex();
            Interval interval = new Interval(startIndex, stopIndex);
            String classContent = input.getText(interval);
            // Remove the first '{' and the last '}'
            classContent = classContent.substring(classContent.indexOf('{') + 1, classContent.lastIndexOf('}'));
            classContents.add(classContent);
        }
    }


    public void walkDirectory( ArrayList<String> paths ) {
        for(String filePath : paths ) {
            parseFile(filePath);
        }
    }

    private void parseFile(String filePath) {
        try {
            input = new ANTLRFileStream(filePath);
            JavaLexer lexer = new JavaLexer(input);
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            JavaParser parser = new JavaParser(tokens);

            // To not overwhelm the application
            lexer.removeErrorListeners();
            parser.removeErrorListeners();

            ParserRuleContext tree = parser.compilationUnit();
            ParseTreeWalker walker = new ParseTreeWalker();
            walker.walk(this, tree);
        } catch (IOException e) {
            System.err.println("Could not parse file " + filePath);
            e.printStackTrace();
        }
    }

    private void writeOutputFile() {

        // Write package name (if there is one) to separate file
        String className = getClassName(testFilePath); // Get name of testFile
        String[] generatedTestFilePathSplit = generatedTestFilePath.split("/");
        String generatedTestFileName = generatedTestFilePathSplit[generatedTestFilePathSplit.length - 1];
        String reconstructedTestClasses = className + "_reconstructedTestClasses";

        File outputFolder = new File(this.outputDir, reconstructedTestClasses);
        outputFolder.mkdirs();

        File outputFile = new File(outputFolder, generatedTestFileName);
        try {
           FileWriter fw = new FileWriter(outputFile);
           if(packageName == null) {
               packageName = " ";
           }
           fw.write(packageName);
            fw.write("\n\n");

            for(String importString : imports) {
                // Write imports to separate file
                fw.write(importString);
                fw.write("\n");
            }

            fw.write("\n");
            fw.write(String.format("public class %s {\n", className));
            fw.write("\n");

            for(String classBodyContent : classContents) {
                fw.write(classBodyContent);
                fw.write("\n");
            }

            fw.write("}");
            fw.close();
        } catch (Exception e) {
            System.err.println("Could not write output file");
            e.printStackTrace();
        }
    }

    private String getClassName(String pathToFile){
        // Step 1: Extract the file name with extension
        int lastSlashIndex = pathToFile.lastIndexOf('/');
        String fileNameWithExtension = pathToFile.substring(lastSlashIndex + 1);

        // Step 2: Remove the extension
        int lastDotIndex = fileNameWithExtension.lastIndexOf('.');
        String fileName = fileNameWithExtension.substring(0, lastDotIndex);

        return fileName;
    }

    // /Users/glacierali/repos/MEX/commonslang/src/test/java/org/apache/commons/lang3/ClassUtilsTest.java
    // /Users/glacierali/repos/MEX/poc/model_responses/ClassUtils/getAllSuperclasses
    public static void main(String[] args) {
        if(args.length < 2) {
            System.out.println("Please provide a path to the existing and generated testfiles, in this exact order");
            System.exit(-1);
        }
        try {
            // DEBUG
            String testFilePath = args[0];
            String generatedTestFilePath = args[1];

            String outputDir = "/Users/glacierali/repos/MEX/poc/parser_output";

            ArrayList<String> inputs = new ArrayList<>();
            inputs.add(testFilePath);
            inputs.add(generatedTestFilePath);

            TestFileConstructor testFileConstructor = new TestFileConstructor(outputDir, testFilePath, generatedTestFilePath);
            testFileConstructor.walkDirectory(inputs);
            testFileConstructor.writeOutputFile();
        } catch (Exception ex) {
            ex.printStackTrace();
            System.exit(1);
        }

    }
}
