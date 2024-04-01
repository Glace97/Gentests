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
    CharStream input;

    HashSet<String> entries;

    static Logger logger;

    public MethodExtractor(String[] methodNames, String outputDir) {
        this.methodNamesToMatch = methodNames;
        this.outputDir = new File(outputDir);
        this.outputDir.mkdirs();
        this.entries = new HashSet<>();
        logger = Logger.getLogger(MethodExtractor.class.getName());
        // logging.properties overides programmatical setting
        //logger.setLevel(Level.INFO);
    }

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
                    String method = input.getText(interval);
                    boolean duplicate = false;
                    for (String entry : entries) {
                        if (entry.contains(method)) {
                            duplicate = true;
                            break;
                        }
                    }
                    if (!duplicate) {
                        intervals.add(interval);
                    }
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
            if (!intervals.isEmpty()) {
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
        String methodsToTest = nameWithExtension.split("\\.")[0] + "_methods";
        File outFile = new File(this.outputDir, methodsToTest);
        try {
            // Write methods to test
            FileWriter fw = new FileWriter(outFile);
            for (Interval interval:this.intervals) {
                String parsedContent = input.getText(interval);
                fw.write(parsedContent);
                if(!parsedContent.isEmpty()) {
                    logger.info("Methodbody parsed and added");
                }
                fw.write("\n\n");
            }
            fw.close();

        } catch (Exception e) {
            System.err.println("Could not write output file " + outFile);
            e.printStackTrace();
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
            pathToProject = "/Users/glacierali/repos/MEX/poc/Parser/src/main/java/testclasses";

            int numMethods = args.length - 1; // Do not include path to project in count

            String[] methods = new String[args.length - 1];
            System.arraycopy(args, 1, methods, 0, numMethods);

            // DEBUG
            //String[] methodNames = {"calcLuhn", "validateLuhn", "someMethod", "someOtherMethod"};
            //String[] methodNames = {"getClassVar"};

            File input_dir = new File(pathToProject);
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