package testclasses;


import java.util.List;

/**
 * Applies the Luhn algorithm (Swedish personnummer) to the input
 * to calculate the checksum digit to append to the number.
 * @return The Luhn checksum for the supplied input
 */
public class EasyClass {
    /**
     * some comments above
     * a class var
     */
    public int classVar;

    /**
     * An ENUM
     * With a javadoc
     */
    @Deprecated
    public enum DAY{
        MONDAY;
    };
    /**
     * Applies the Luhn algorithm (Swedish personnummer) to the input
     * to calculate the checksum digit to append to the number.
     * @param  i string containing the input. All characters except numeric letters will be stripped from the input
     * @return The Luhn checksum for the supplied input
     */
    @Deprecated
    public static int getClassVar(int i) {
        // Lets see if this comment is hidden
        return 1;
    }

    /**
     * Applies the Luhn algorithm (Swedish personnummer) to the input
     * to calculate the checksum digit to append to the number.
     * @param input A string containing the input. All characters except numeric letters will be stripped from the input
     * @return The Luhn checksum for the supplied input
     */
    public static int[] calcLuhn(String input) {
        int sum = 0;
        return new int[]{sum};
    }


    /**
     * A generic method
     * wihch happens to be static
     */
    public <T> List<T> wrap(final List type) {
        return null;
    }

    /**
     * some comments above
     * a class
     */
    private static class innerClass {
        int y;
        int x;
    }
}
