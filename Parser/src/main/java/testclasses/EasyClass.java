package testclasses;

public class EasyClass {
    public int classVar;

    /**
     * Applies the Luhn algorithm (Swedish personnummer) to the input
     * to calculate the checksum digit to append to the number.
     * @param  i string containing the input. All characters except numeric letters will be stripped from the input
     * @return The Luhn checksum for the supplied input
     */
    public int getClassVar(int i) {
        // Lets see if this comment is hidden
        return classVar;
    }

    /**
     * Applies the Luhn algorithm (Swedish personnummer) to the input
     * to calculate the checksum digit to append to the number.
     * @param input A string containing the input. All characters except numeric letters will be stripped from the input
     * @return The Luhn checksum for the supplied input
     */
    public static int[] calcLuhn(String input) {
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
        return new int[]{checksum};
    }
    private static class innerClass {
        int y;
        int x;
    }
}
