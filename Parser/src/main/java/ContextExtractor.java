package parser;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
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
public class ContextExtractor extends JavaParserBaseListener {
    String[] methodNamesToMatch;
    File currentJavaFile;
    File outputDir;
    ArrayList<String> metaData;
    CharStream input;

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
            metaData.add(importString);
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
                                    JavaParser.MemberDeclarationContext memberDeclaration = (JavaParser.MemberDeclarationContext) declarationChild;
                                    ParseTree memberDeclarationChild = memberDeclaration.getChild(0);
                                    if (!(memberDeclarationChild instanceof JavaParser.MethodDeclarationContext) &&
                                            !(memberDeclarationChild instanceof JavaParser.GenericMethodDeclarationContext)) {
                                        // Not a method
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
                                        metaData.add(content);
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
        //File testDir = new File("/Users/glacierali/repos/MEX/poc/Parser/src/main/java/testclasses");
        File testDir = new File ("/Users/glacierali/repos/MEX/commons-lang/src/main/java");
        String outputDir = "/Users/glacierali/repos/MEX/poc/Parser/src/main/java/output/complex";
        ContextExtractor extractor = new ContextExtractor(outputDir);
        extractor.walkDirectory(testDir);
    }

}