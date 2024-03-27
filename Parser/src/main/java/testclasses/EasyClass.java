package parser.testclasses;

public class EasyClass {
    public int classVar;

    /**
     * A java doc comment.
     * With some lines.
     * */
    public int getClassVar() {
        // Lets see if this comment is hidden
        return classVar;
    }

    private static class innerClass {
        int y;
        int x;
    }
}
