package parser;

import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.Interval;
import org.antlr.v4.runtime.tree.ParseTreeWalker;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;
import java.util.logging.Logger;

/**
 * Extracts methods and the method bodiees from Java files.
 */
public class MethodExtractor extends JavaParserBaseListener {
    String[] methodNamesToMatch;
    File currentJavaFile;
    File outputDir;
    List<Interval> intervals;
    HashMap<String, ArrayList<String>> methodBodies;
    HashMap<String, ArrayList<String>> classMethodMapping;
    CharStream input;
    ArrayList<String> allMethodsNames;

    // Flag indicating whether to extract all method names
    static boolean allMethods = false;

    /**
     * Constructor for MethodExtractor.
     * Initializes method names to match, output directory, and logger.
     * @param methodNames Names of methods to match and extract.
     * @param outputDir Path to the output directory where extracted information will be stored.
     */
    public MethodExtractor(String[] methodNames, String outputDir) {
        this.methodNamesToMatch = methodNames;
        this.outputDir = new File(outputDir);
        this.outputDir.mkdirs();
        this.methodBodies = new HashMap<>();
        this.classMethodMapping = new HashMap<>();
    }

    /**
     * Overloaded constructor for MethodExtractor.
     * Initializes output directory and logger.
     * @param outputDir Path to the output directory where extracted information will be stored.
     */
    public MethodExtractor(String outputDir) {
        this.outputDir = new File(outputDir);
        this.outputDir.mkdirs();
        this.methodBodies = new HashMap<>();
        this.classMethodMapping = new HashMap<>();
    }

    /**
     * Callback when entering a method declaration.
     * Extracts information about method names and bodies.
     * @param ctx The method declaration context.
     */
    @Override
    public void enterMethodDeclaration(JavaParser.MethodDeclarationContext ctx) {
        parseMethods(ctx.identifier(), ctx.modifier(), ctx.start.getStartIndex(), ctx.stop.getStopIndex());
    }

    /**
     * Callback when entering a generic method declaration.
     * Extracts information about method names and bodies.
     * @param ctx The generic method declaration context.
     */
    @Override
    public void enterGenericMethodDeclaration(JavaParser.GenericMethodDeclarationContext ctx) {

        parseMethods(ctx.identifier(), ctx.modifier(), ctx.start.getStartIndex(), ctx.stop.getStopIndex());
    }

    /**
     * Parses method names and bodies based on specified criteria.
     * @param identifier The identifier context representing the method name.
     * @param modifier The modifier context representing the method modifier.
     * @param startIndex The start index of the method declaration.
     * @param stopIndex The stop index of the method declaration.
     */
    private void parseMethods(JavaParser.IdentifierContext identifier, JavaParser.ModifierContext modifier, int startIndex, int stopIndex) {
        if (identifier != null) {
            String foundName = identifier.getText();
            if (allMethods) {
                // We want to add all public method names
                if(modifier != null) {
                String accesModifer = modifier.getText();
                    if (accesModifer.equals("public") || accesModifer.equals("static")) {
                        // Testable method
                        allMethodsNames.add(foundName);
                        extractMethodBody(foundName, startIndex, stopIndex);
                    }
                } else {
                    // Doesn't contain modifier, therefore default/available to package
                    allMethodsNames.add(foundName);
                    extractMethodBody(foundName, startIndex, stopIndex);
                }
            } else {
                for (String name : methodNamesToMatch) {
                    if (foundName.equals(name)) {
                        extractMethodBody(name, startIndex, stopIndex);
                    }
                }
            }
        }
    }

    /**
     * Extracts the body of a method and associates it with its name.
     * Keeps track of methods belonging to the current Java file for organization.
     * @param name The name of the method.
     * @param startIndex The start index of the method declaration.
     * @param stopIndex The stop index of the method declaration.
     */
    private void extractMethodBody(String name, int startIndex, int stopIndex) {
        Interval interval = new Interval(startIndex, stopIndex);
        String methodBody = input.getText(interval);
        if (methodBodies.containsKey(name)) {
            // There are several methods with the same name.
            ArrayList<String> bodies = methodBodies.get(name);
            bodies.add(methodBody);
            methodBodies.replace(name, bodies);
        } else {
            ArrayList<String> bodies = new ArrayList<>();
            bodies.add(methodBody);
            methodBodies.put(name, bodies);
        }

        // Keep track of what methods belong to which class
        // In order to organize output files
        ArrayList<String> associatedMethods = classMethodMapping.get(currentJavaFile.getName());
        associatedMethods.add(name);
        classMethodMapping.put(currentJavaFile.getName(), associatedMethods);
    }


    /**
     * Recursively walks through the directory structure to parse Java files.
     * @param dirOrFile The directory or file to start walking from.
     */
    public void walkDirectory(File dirOrFile) {
        if (dirOrFile.getName().endsWith(".java")) {
            // A file was directly provided instead of a directory
            parseFile(dirOrFile);
        } else {
            // Recursively check all .java files in the given directory
            for (File child : Objects.requireNonNull(dirOrFile.listFiles())) {
                if (child.isDirectory()) {
                    walkDirectory(child);
                } else {
                    if (child.getName().endsWith(".java")) {
                        parseFile(child);
                    }
                }
            }
        }
    }

    /**
     * Parses a Java file, extracting method bodies and associated information.
     * @param child The Java file to be parsed.
     */
    private void parseFile(File child) {
        try {
            currentJavaFile = child;
            classMethodMapping.put(currentJavaFile.getName(), new ArrayList<>());
            intervals = new ArrayList<>();
            input = new ANTLRFileStream(child.getPath());
            allMethodsNames = new ArrayList<>();
            JavaLexer lexer = new JavaLexer(input);
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            JavaParser parser = new JavaParser(tokens);

            // To not overwhelm the application
            lexer.removeErrorListeners();
            parser.removeErrorListeners();

            ParserRuleContext tree = parser.compilationUnit();
            ParseTreeWalker walker = new ParseTreeWalker();
            walker.walk(this, tree);
            if (!methodBodies.isEmpty()) {
                System.out.println("Collected parser intervals.");
                writeOutputFile();
            } else {
                System.out.println("No methodbodies recovered");
            }
        } catch (IOException e) {
            System.err.println("Could not parse " + child.getPath());
            e.printStackTrace();
        }
    }

    /**
     * Writes the extracted method bodies to output files.
     */
    private void writeOutputFile() {
        String nameWithExtension = this.currentJavaFile.getName();
        String className = nameWithExtension.split("\\.")[0];

        File outputFolder = new File(this.outputDir, className + "_methods");
        outputFolder.mkdirs();

        // We may want to print all methods, or just the methodnames to match
        String[] methodsToPrint;

        if(allMethods) {
            methodsToPrint = new String[allMethodsNames.size()];
            methodsToPrint = allMethodsNames.toArray(methodsToPrint);
        } else {
            methodsToPrint = methodNamesToMatch;
        }

        for (String methodToTest : methodsToPrint) {
            // Parsed methods are stored under <Provided output path>/classname/method_name.txt
            ArrayList<String> associatedMethods = classMethodMapping.get(this.currentJavaFile.getName());
            if (associatedMethods.contains(methodToTest)) {
                if(!methodToTest.isEmpty()) {
                    File outFile = new File(outputFolder, methodToTest);
                    try {
                        FileWriter fw = new FileWriter(outFile);
                        ArrayList<String> methods = methodBodies.get(methodToTest);
                        for (String method : methods) {
                            fw.write(method);
                            fw.write("\n\n");
                        }
                        fw.close();

                    } catch (Exception e) {
                        System.err.println("Could not write output file " + outFile);
                        e.printStackTrace();
                    }
                }
            }

        }
    }


    /**
     * Main method to initiate the Java file parsing and method extraction process.
     * Accepts command line arguments specifying the path to the project directory or file, and optionally, method names to match and extract.
     * @param args Command line arguments. If no method names are provided, all public methods are extracted.
     * @throws IOException If an I/O error occurs.
     */
    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.out.println("Please provide a path to the project directory or file");
            System.exit(-1);
        }

        try {
            String pathToProject = args[0];
            // DEBUG
            //pathToProject = "/Users/glacierali/repos/MEX/poc/Parser/src/main/java/testclasses";
            File input_dir = new File(pathToProject);
            String outputDir = "/Users/glacierali/repos/MEX/Gentests/parser_output";

            int numMethods = args.length - 1; // Do not include path to project in count
            if (numMethods == 0) {
                // Only path to file was provided, get all public methods
                allMethods = true;
                MethodExtractor extractor = new MethodExtractor(outputDir);
                extractor.walkDirectory(input_dir);
            } else {
                // DEBUG
                //String[] methodNames = {"calcLuhn", "validateLuhn", "someMethod", "someOtherMethod"};
                //String[] methodNames = {"getClassVar"};

                String[] methods = new String[numMethods];
                System.arraycopy(args, 1, methods, 0, numMethods);
                MethodExtractor extractor = new MethodExtractor(methods, outputDir);
                extractor.walkDirectory(input_dir);
            }
        } catch (Exception ex) {
            ex.printStackTrace();
            System.exit(1);
        }
    }
}

