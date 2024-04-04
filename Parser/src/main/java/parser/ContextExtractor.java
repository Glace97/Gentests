package parser;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Objects;

import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.Interval;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.ParseTreeWalker;


/**
 * Extracts information from Javafiles.
 * Imports, packages,  class variables, enums.
 */
//TODO: add logging
public class ContextExtractor extends JavaParserBaseListener {
    File currentJavaFile;
    File outputDir;
    ArrayList<String> context;
    CharStream input;

    ArrayList<String> imports;
    HashSet<String>  entries;

    public ContextExtractor(String outputDir) {
        this.outputDir = new File(outputDir);
        this.outputDir.mkdirs();
        this.entries = new HashSet<>();
    }

    @Override public void enterImportDeclaration(JavaParser.ImportDeclarationContext ctx) {
        if(ctx != null) {
            int a = ctx.start.getStartIndex();
            int b = ctx.stop.getStopIndex();
            Interval interval = new Interval(a, b);
            String importString = input.getText(interval);
            imports.add(importString);
        }
    }

    // Class declaration consists of a classBody Context
    // The classBody context consists of a class Body
    // The classBody consists of members
    // Members has methodDeclarations, fieldDeclarations, inner classDeclarations, constructors etc.
    @Override
    public void enterClassDeclaration(JavaParser.ClassDeclarationContext ctx) {
        if(ctx != null) {
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
                                    if (!(memberDeclarationChild instanceof JavaParser.MethodDeclarationContext) &&
                                            !(memberDeclarationChild instanceof JavaParser.GenericMethodDeclarationContext) && (memberDeclarationChild != null)) {
                                        // Not a method, but can be anything else within the class (variables, inner classes, enums).
                                        // Add it as context to the method.
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

    public void walkDirectory( File dirOrFile ) {
        if(dirOrFile.getName().endsWith(".java")) {
            // A file was directly provided instead of a directory
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
            if (!context.isEmpty() || !imports.isEmpty()) {
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
        String context = className + "_context";

        File outputFolder = new File(this.outputDir, context);
        outputFolder.mkdirs();

        File outFileImports = new File(outputFolder, "imports");
        File outFileContext = new File(outputFolder, "context");

        try {
            FileWriter fw = new FileWriter(outFileImports);

            for(String importString : imports) {
                // Write imports to seperate file
                fw.write(importString);
            }
            fw.close();

            fw = new FileWriter(outFileContext);
            // Write metadata to separate file
            for(String line:this.context) {
                fw.write(line);
                fw.write("\n");
            }
            fw.close();

        } catch (Exception e) {
            System.err.println("Could not write output file");
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
            //File input = new File("/Users/glacierali/repos/MEX/poc/Parser/src/main/java/testclasses")
            File input = new File(pathToProject);

            String outputDir = "/Users/glacierali/repos/MEX/poc/parser_output";
            ContextExtractor extractor = new ContextExtractor(outputDir);
            extractor.walkDirectory(input);
        } catch (Exception ex) {
            ex.printStackTrace();
            System.exit(1);
        }

    }

}