package parser;

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

/**
 * This class parses two test files (old and new), extracts their contents such as package declaration,
 * imports, and class contents, and then reassembles and combines them into a new test file.
 */
public class TestFileParser extends JavaParserBaseListener {
    File outputDir;

    CharStream input;

    HashSet<String> imports;
    HashSet<String> classContents;
     String testFilePath;

    String packageName;

    HashSet<String> entries;

     String generatedTestFilePath;


    /**
     * Constructs a TestFileParser with the specified output directory, test file path, and generated test file path.
     *
     * @param outputDir The directory where the combined test file will be output.
     * @param testFilePath The path of the new test file to be parsed.
     * @param generatedTestFilePath The path of the old test file to be parsed.
     */
    public TestFileParser(String outputDir, String testFilePath, String generatedTestFilePath) {
        this.outputDir = new File(outputDir);
        this.outputDir.mkdirs();
        imports = new HashSet<>();
        this.testFilePath = testFilePath;
        this.generatedTestFilePath = generatedTestFilePath;
        entries = new HashSet<>();
        classContents = new HashSet<>();
    }

    /**
     * Reads existing imports from the test file and adds them to the set of unique imports.
     *
     * @param ctx The context of the import declaration in the parse tree.
     */
    @Override public void enterImportDeclaration(JavaParser.ImportDeclarationContext ctx) {
        if (ctx != null) {
            int startIndex = ctx.start.getStartIndex();
            int stopIndex = ctx.stop.getStopIndex();
            Interval interval = new Interval(startIndex, stopIndex);

            imports.add(input.getText(interval));
        }
    }

    /**
     * Reads the package declaration from the original test file.
     *
     * @param ctx The context of the package declaration in the parse tree.
     */
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

    /**
     * Determines if the given context represents a nested class.
     *
     * @param context The parser rule context to check.
     * @return True if the context represents a nested class, false otherwise.
     */
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

    /**
     * Reads the class body from the test file, excluding nested classes, and adds the content to the set of class contents.
     *
     * @param ctx The context of the class body in the parse tree.
     */
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

    /**
     * Walks through the provided list of file paths, parsing each file.
     *
     * @param paths A list of file paths to be parsed.
     */
    public void walkDirectory( ArrayList<String> paths ) {
        for(String filePath : paths ) {
            parseFile(filePath);
        }
    }

    /**
     * Parses the file at the given file path, extracting its contents.
     *
     * @param filePath The path of the file to be parsed.
     */
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

    /**
     * Writes the output file by combining the package name, imports, and class contents extracted from the test files.
     */
    private void writeOutputFile() {

        // Write package name (if there is one) to separate file
        String className = getClassName(testFilePath); // Get name of testFile
        String[] generatedTestFilePathSplit = generatedTestFilePath.split("/");
        String generatedTestFileName = generatedTestFilePathSplit[generatedTestFilePathSplit.length - 1];
        String reconstructedTestClasses = className + "_reconstructed";

        File outputFolder = new File(this.outputDir, reconstructedTestClasses);
        outputFolder.mkdirs();

        File outputFile = new File(outputFolder, String.format("%s.java", className));
        try {
           FileWriter fw = new FileWriter(outputFile);
           if(packageName == null) {
               packageName = " ";
           }
           fw.write(packageName);
            fw.write("\n\n");

            for(String importString : imports) {
                 //Write imports to separate file
                fw.write(importString);
                fw.write("\n");
            }

            fw.write("\n");
            fw.write(String.format("public class %s {\n", className));
            fw.write("\n");

            // Write package name
            for(String classBodyContent : classContents) {
                fw.write(classBodyContent);
                fw.write("\n");
                //System.out.println(classBodyContent);
            }

            fw.write("}");
            fw.close();
        } catch (Exception e) {
            System.err.println("Could not write output file");
            e.printStackTrace();
        }
    }

    /**
     * Extracts the class name from the given file path.
     *
     * @param pathToFile The path of the file from which to extract the class name.
     * @return The class name extracted from the file path.
     */
    private String getClassName(String pathToFile){
        // Step 1: Extract the file name with extension
        int lastSlashIndex = pathToFile.lastIndexOf('/');
        String fileNameWithExtension = pathToFile.substring(lastSlashIndex + 1);

        // Step 2: Remove the extension
        int lastDotIndex = fileNameWithExtension.lastIndexOf('.');
        String fileName = fileNameWithExtension.substring(0, lastDotIndex);

        return fileName;
    }

    /**
     * The main method to run the TestFileParser. It expects two arguments: the path to the existing test file and the path to the generated test file.
     *
     * @param args The command line arguments, where the first argument is the path to the existing test file and the second argument is the path to the generated test file.
     */
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

            TestFileParser testFileParser = new TestFileParser(outputDir, testFilePath, generatedTestFilePath);
            testFileParser.walkDirectory(inputs);
            testFileParser.writeOutputFile();
        } catch (Exception ex) {
            ex.printStackTrace();
            System.exit(1);
        }

    }
}
