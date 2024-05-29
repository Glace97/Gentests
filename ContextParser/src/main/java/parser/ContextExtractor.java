package parser;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;

import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.Interval;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.ParseTreeWalker;


/**
 * Extracts information from Java files such as imports, packages, class variables, and enums.
 */
public class ContextExtractor extends JavaParserBaseListener {
    File currentJavaFile;
    File outputDir;
    ArrayList<String> context;
    CharStream input;

    ArrayList<String> imports;
    HashSet<String>  entries;

    String packageName = "";

    String declaration = "";


    /**
     * Constructor to initialize output directory and data structures.
     * @param outputDir Path to the output directory where extracted information will be stored.
     */
    public ContextExtractor(String outputDir) {
        this.outputDir = new File(outputDir);
        this.outputDir.mkdirs();
        this.entries = new HashSet<>();
    }

    /**
     * Callback when entering a package declaration in the Java file.
     * @param ctx The package declaration context.
     */
    @Override public void enterPackageDeclaration(JavaParser.PackageDeclarationContext ctx) {
        packageName = getTextFromContext(ctx);
    }

    /**
     * Callback when entering an import declaration in the Java file.
     * @param ctx The import declaration context.
     */
    @Override public void enterImportDeclaration(JavaParser.ImportDeclarationContext ctx) {
        String importString = getTextFromContext(ctx);
        imports.add(importString);
    }

    /**
     * Extracts String text from a given context.
     * @param ctx The context from which text is to be extracted.
     * @return Extracted readable text from the context.
     */
    private String getTextFromContext(ParserRuleContext ctx) {
        if (ctx != null) {
            int startIndex = ctx.start.getStartIndex();
            int stopIndex = ctx.stop.getStopIndex();
            Interval interval = new Interval(startIndex, stopIndex);
            return input.getText(interval);
        }
        return " ";
    }

    /**
     * Callback when entering a class declaration in the Java file.
     * Extracts information about class members.
     * <p>
     * Class declaration consists of a classBody Context. The classBody context consists of a class Body.
     * The classBody consists of members such as methodDeclarations, fieldDeclarations, inner classDeclarations, constructors, etc.
     * </p>
     *
     * @param ctx The class declaration context.
     */
    @Override
    public void enterClassDeclaration(JavaParser.ClassDeclarationContext ctx) {
        if(ctx != null) {
            setFullDeclaration(ctx);
            for (int i = 0; i < ctx.getChildCount(); i++) {
                ParseTree child = ctx.getChild(i);
                if (child instanceof JavaParser.ClassBodyContext) {
                    // Get full class body
                    JavaParser.ClassBodyContext classBody = (JavaParser.ClassBodyContext) child;
                    for (int j = 0; j < classBody.getChildCount(); j++) {
                        ParseTree classBodyChild = classBody.getChild(j);
                        if (classBodyChild instanceof JavaParser.ClassBodyDeclarationContext) {
                            JavaParser.ClassBodyDeclarationContext declaration = (JavaParser.ClassBodyDeclarationContext) classBodyChild;
                            for (int k = 0; k < declaration.getChildCount(); k++) {
                                ParseTree declarationChild = declaration.getChild(k);
                                if (declarationChild instanceof JavaParser.MemberDeclarationContext) {
                                    // Check all members of class
                                    JavaParser.MemberDeclarationContext memberDeclaration = (JavaParser.MemberDeclarationContext) declarationChild;
                                    ParseTree memberDeclarationChild = memberDeclaration.getChild(0);
                                    if (!(memberDeclarationChild instanceof parser.JavaParser.MethodDeclarationContext) &&
                                            !(memberDeclarationChild instanceof parser.JavaParser.GenericMethodDeclarationContext) && (memberDeclarationChild != null)) {
                                        // Not a method, but can be anything else within the class (variables, inner classes, enums).
                                        ParserRuleContext ruleCtx = (ParserRuleContext) declarationChild;
                                        int startIndex = ruleCtx.getStart().getStartIndex();
                                        int stopIndex = ruleCtx.getStop().getStopIndex();
                                        Interval interval = new Interval(startIndex, stopIndex);
                                        String content = input.getText(interval);
                                        boolean duplicate = false;
                                        for(String entry: entries) {
                                            if(entry.contains(content)) {
                                                duplicate = true;
                                                break;
                                            }
                                        }
                                        if(!duplicate) {
                                            // To avoid duplicates, like field variables, written twice
                                            context.add(content);
                                            entries.add(content);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    /**
     * Constructs the full declaration of the class including its name, type parameters, inheritance, etc.
     * @param ctx The class declaration context.
     */
    private void setFullDeclaration(JavaParser.ClassDeclarationContext ctx){
        if(!isNestedClass(ctx)) {
            ArrayList<String> classDeclaration = new ArrayList<>();


            // Safely get identifier text
            if (ctx.identifier() != null) {
                classDeclaration.add(ctx.identifier().getText());
            }

            // Safely get type parameters text
            if (ctx.typeParameters() != null) {
                classDeclaration.add(ctx.typeParameters().getText());
            }

            // Safely get extends keyword text
            if (ctx.EXTENDS() != null) {
                classDeclaration.add(ctx.EXTENDS().getText());
            }

            // Safely get extends keyword text
            if (ctx.typeType() != null) {
                classDeclaration.add(ctx.typeType().getText());
            }

            // Safely get implements keyword text
            if (ctx.IMPLEMENTS() != null) {
                classDeclaration.add(ctx.IMPLEMENTS().getText());
            }

            // Safely get type list as a string
            if (ctx.typeList() != null) {
                if (!ctx.typeList().isEmpty()) {
                    for(JavaParser.TypeListContext type : ctx.typeList()) {
                        classDeclaration.add(type.getText());
                    }
                }
            }

            StringBuilder sb = new StringBuilder();
            for(String part: classDeclaration) {
                if(part != null) {  // Additional safeguard, redundant but safe
                    sb.append(part);
                    sb.append(" ");
                }
            }
            declaration = sb.toString();
        }
    }

    /**
     * Checks if the class is a nested class.
     * @param context The class context.
     * @return True if the class is nested, otherwise false.
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
     * Recursively walks through a directory to parse all Java files.
     * @param dirOrFile The directory or file to be parsed.
     */
    public void walkDirectory( File dirOrFile ) {
        if(dirOrFile.getName().endsWith(".java")) {
            // A file was directly provided instead of a directory
            parseFile(dirOrFile);
        } else {
            // Xheck all .java files in the given directory
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

    /**
     * Parses a Java file, extracting its context, imports, and other information.
     * @param child The Java file to be parsed.
     */
    private void parseFile(File child) {
        try {
            currentJavaFile = child;
            context = new ArrayList<>();
            imports = new ArrayList<>();
            input = new ANTLRFileStream(child.getPath());
            JavaLexer lexer = new JavaLexer(input);
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            JavaParser parser = new JavaParser(tokens);

            // To not overwhelm the application
            lexer.removeErrorListeners();
            parser.removeErrorListeners();

            ParserRuleContext tree = parser.compilationUnit();
            ParseTreeWalker walker = new ParseTreeWalker();
            walker.walk(this, tree);
            writeOutputFile();
        } catch (IOException e) {
            System.err.println("Could not parse " + child.getPath());
            e.printStackTrace();
        }
    }

    /**
     * Writes the extracted information to the corresponding output files.
     */
    private void writeOutputFile() {
        String nameWithExtension =  this.currentJavaFile.getName();
        String className = nameWithExtension.split("\\.")[0];
        String context = className + "_context";

        File outputFolder = new File(this.outputDir, context);
        outputFolder.mkdirs();

        File outFilePackage = new File(outputFolder, "package");
        File outFileImports = new File(outputFolder, "imports");
        File outFileContext = new File(outputFolder, "context");
        File classDeclaration = new File(outputFolder, "declaration");

        try {
            // Write package name (if there is one) to separate file
            FileWriter fw = new FileWriter(outFilePackage);
            fw.write(packageName);
            fw.write("\n\n");
            fw.close();

            // Write class declaration
            fw = new FileWriter(classDeclaration);
            fw.write(declaration);
            fw.write("\n\n");
            fw.close();

            fw = new FileWriter(outFileImports);
            for(String importString : imports) {
                // Write imports to separate file
                fw.write(importString);
                fw.write("\n");
            }
            fw.close();

            fw = new FileWriter(outFileContext);
            // Write metadata to separate file
            for(String line:this.context) {
                fw.write(line);
                fw.write("\n");
            }
            if(context.isEmpty()) { fw.write(" ");}
            fw.close();

        } catch (Exception e) {
            System.err.println("Could not write output file");
            e.printStackTrace();
        }
    }

    /**
     * Entry point of the application. Parses the specified directory or file.
     * @param args Command-line arguments. Expects the path to the project directory or file.
     * @throws IOException If an I/O error occurs.
     */
    public static void main(String[] args) throws IOException {
        if(args.length < 1) {
            System.out.println("Please provide a path to the project directory or file");
            System.exit(-1);
        }

        try {
            String pathToProject = args[0];

            // DEBUG
            //File input = new File("/Users/glacierali/repos/MEX/poc/Parser/src/main/java/testclasses")
            File input = new File(pathToProject);

            String outputDir = "/Users/glacierali/repos/MEX/Gentests/parser_output";
            ContextExtractor extractor = new ContextExtractor(outputDir);
            extractor.walkDirectory(input);
        } catch (Exception ex) {
            ex.printStackTrace();
            System.exit(1);
        }

    }

}