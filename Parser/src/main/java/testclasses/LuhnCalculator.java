import java.util.List;
import java.io.BufferedInputStream;

public class LuhnCalculator {
    /**
    * Testing parsing inner class
    */
   private class InnerClass {
    private int x;
    private int y;

    private InnerClass(int x, int y) {
        this.x = x;
        this.y = y;
    }

    private int[] getXY(){
        int[] vars = {x, y};
        return vars;
    }
   }

    /**
    * Applies the Luhn algorithm (Swedish personnummer) to the input
    * to calculate the checksum digit to append to the number.
    * @param input A string containing the input. All characters except numeric letters will be stripped from the input
    * @return The Luhn checksum for the supplied input
    */
    public static int calcLuhn(String input) {
        int sum = 0;
        int length = input.length();
        int parity = length % 2;
        for (int i = 0; i < length; i++) {
            char c = input.charAt(i);
            if (!Character.isDigit(c)) {
                continue;
            }
            int digit = Character.getNumericValue(c);
            if (i % 2 == parity) {
                digit *= 2;
                if (digit > 9) {
                    digit -= 9;
                }
            }
            sum += digit;
        }
        int checksum = 10 - (sum % 10);
        if (checksum == 10) {
            checksum = 0;
        }
        return checksum;        
    }

    /**
     * Validates a given input using the Luhn algorithm.
     *
     * @param input the input to be validated
     * @return true if the input is valid according to the Luhn algorithm, false otherwise
     */
    public static Boolean validateLuhn(String input) {
        int checksum = calcLuhn(input);
        return checksum == 0;
    }

    /**
     * Some bogus private method
     * @return some bogus value
     */
    private static int helperMethod() {
        // Bogus method
        return -1;
    }

    public void someMethod(int verylongargumentname,
        int anotherlongargumentname) {
        // Bogus method
        helperMethod();
    }

    public static List<String> someOtherMethod() 
    {
        // Bogus method
        return null;
    }

    public static List<String> someOtherMethod(int takesAnArgument)
    {
        // Bogus method
        return null;
    }
}
