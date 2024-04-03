package parser;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;

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
    HashMap<String, ArrayList<String>> methodBodies;
    HashMap<String, ArrayList<String>> classMethodMapping;

    CharStream input;

    static Logger logger;

    public MethodExtractor(String[] methodNames, String outputDir) {
        this.methodNamesToMatch = methodNames;
        this.outputDir = new File(outputDir);
        this.outputDir.mkdirs();
        this.methodBodies = new HashMap<>();
        this.classMethodMapping = new HashMap<>();
        logger = Logger.getLogger(MethodExtractor.class.getName());
        // logging.properties overides programmatical setting
        //logger.setLevel(Level.INFO);
    }

    @Override
    public void enterMethodDeclaration(JavaParser.MethodDeclarationContext ctx) {
        findMatchingMethods(ctx.identifier(), ctx.start.getStartIndex(), ctx.stop.getStopIndex());
    }

    @Override
    public void enterGenericMethodDeclaration(JavaParser.GenericMethodDeclarationContext ctx) {
        findMatchingMethods(ctx.identifier(), ctx.start.getStartIndex(), ctx.stop.getStopIndex());
    }

    private void findMatchingMethods(JavaParser.IdentifierContext identifier, int startIndex, int stopIndex) {
        if (identifier != null) {
            for (String name : methodNamesToMatch) {
                String foundName = identifier.getText();
                if (foundName.equals(name)) {
                    Interval interval = new Interval(startIndex, stopIndex);
                    String methodBody = input.getText(interval);
                    if(methodBodies.containsKey(name)) {
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
            }
        }
    }


    public void walkDirectory( File dirOrFile ) {
        if(dirOrFile.getName().endsWith(".java")) {
            // A file was directly provided instead of a directory
            logger.info("Parsing a single file instead of directory");
            parseFile(dirOrFile);
        } else {
            // Recursively check all .java files in the given directory
            for( File child : Objects.requireNonNull(dirOrFile.listFiles())) {
                if( child.isDirectory() ) {
                    walkDirectory( child );
                } else {
                    if (child.getName().endsWith(".java")) {
                        parseFile(child);
                    }
                }
            }
        }
    }

    private void parseFile(File child) {
        try {
            currentJavaFile = child;
            classMethodMapping.put(currentJavaFile.getName(), new ArrayList<>());
            intervals = new ArrayList<>();
            input = new ANTLRFileStream(child.getPath());
            JavaLexer lexer = new JavaLexer(input);
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            JavaParser parser = new JavaParser(tokens);

            // To not overwhelm the application
            lexer.removeErrorListeners();
            parser.removeErrorListeners();

            ParserRuleContext tree = parser.compilationUnit();
            ParseTreeWalker walker = new ParseTreeWalker();
            logger.info("Current file: " + child);
            logger.info(tree.toStringTree(parser));
            walker.walk(this, tree);
            if (!methodBodies.isEmpty()) {
                logger.info("Collected parser intervals.");
                writeOutputFile();
            }
        } catch (IOException e) {
            System.err.println("Could not parse " + child.getPath());
            e.printStackTrace();
        }
    }

    private void writeOutputFile() {
        String nameWithExtension =  this.currentJavaFile.getName();
        String className = nameWithExtension.split("\\.")[0];

        File outputFolder = new File(this.outputDir, className + "_methods");
        outputFolder.mkdirs();
            for(String methodToTest : methodNamesToMatch) {
                // Parsed methods are stored under <Provided output path>/classname/method_name.txt
                ArrayList<String> associatedMethods = classMethodMapping.get(this.currentJavaFile.getName());
                if(associatedMethods.contains(methodToTest)) {
                    File outFile = new File(outputFolder, methodToTest);
                    try {
                        FileWriter fw = new FileWriter(outFile);

                        ArrayList<String> methods = methodBodies.get(methodToTest);
                        for(String method : methods) {
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

    public static void main(String[] args) throws IOException {
        if(args.length < 1) {
            System.out.println("Please provide a path to the project directory or file");
            System.exit(-1);
        }

        try {
            String pathToProject = args[0];
            // DEBUG
            //pathToProject = "/Users/glacierali/repos/MEX/poc/Parser/src/main/java/testclasses";

            int numMethods = args.length - 1; // Do not include path to project in count

            String[] methods = new String[args.length - 1];
            System.arraycopy(args, 1, methods, 0, numMethods);

            // DEBUG
            //String[] methodNames = {"calcLuhn", "validateLuhn", "someMethod", "someOtherMethod"};
            //String[] methodNames = {"getClassVar"};

            File input_dir = new File(pathToProject);

            // TODO: change to a tmp folder in home folder
            String outputDir = "/Users/glacierali/repos/MEX/poc/Parser/src/main/java/output";
            MethodExtractor extractor = new MethodExtractor(methods, outputDir);

            logger.info("Directory to parse: " + pathToProject);
            logger.info("Methods to look for: " + Arrays.toString(methods));

            extractor.walkDirectory(input_dir);
        } catch (Exception ex) {
            ex.printStackTrace();
            System.exit(1);
        }


    }
}
