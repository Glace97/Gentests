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

        /**
         * Some dmmy funciton within enums
         * */
        public boolean getTrue() {
            return true;
        }
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


    /**
     * The {@link Processor.Type} enum defines types of a microprocessor.
     * The following types are defined:
     * <ul>
     *     <li>AArch64</li>
     *     <li>x86</li>
     *     <li>ia64</li>
     *     <li>PPC</li>
     *     <li>RISCV</li>
     *     <li>Unknown</li>
     * </ul>
     */
    public enum Type {

        /**
         * ARM 64-bit.
         *
         * @since 3.13.0
         */
        AARCH_64("string"),
        /**
         * Unknown architecture.
         */
        UNKNOWN("Unknown");
        private final String label;

        Type(final String label) {
            this.label = label;
        }

        /**
         * Gets the label suitable for display.
         *
         * @return the label.
         * @since 3.13.0
         */
        public String getLabel() {
            return label;
        }

    }

    /**
     * Tests if {@link Processor} is type of Aarch64.
     *
     * @return {@code true}, if {@link Processor} is {@link Processor.Type#AARCH_64}, else {@code false}.
     *
     * @since 3.13.0
     */
    public boolean isAarch64() {
        return Processor.Type.AARCH_64 == null;
    }

    /**
     * Tests if {@link Processor} is 32 bit.
     *
     * @return {@code true}, if {@link Processor} is {@link Processor.Arch#BIT_32}, else {@code false}.
     */
    public boolean is32Bit() {
        return true;
    }
}
