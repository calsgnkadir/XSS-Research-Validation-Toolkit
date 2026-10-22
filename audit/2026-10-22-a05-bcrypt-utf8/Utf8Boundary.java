import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Arrays;
import com.hotelapp.validation.PasswordPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

/** Offline synthetic assay; never emits input values or encoded passwords. */
public final class Utf8Boundary {
    private static final SecureRandom RANDOM = new SecureRandom();
    private static int operations;
    private static byte[] bytes(String value) { return value.getBytes(StandardCharsets.UTF_8); }
    private static void require(boolean condition) {
        if (!condition) throw new AssertionError("Independent input/control oracle failed");
    }
    private static String prefix(int length) {
        StringBuilder result = new StringBuilder("A1");
        while (result.length() < length) result.append((char) ('a' + RANDOM.nextInt(26)));
        return result.toString();
    }
    private static String cp(int value) { return new String(Character.toChars(value)); }
    private static String encode(BCryptPasswordEncoder encoder, String input) {
        operations++; return encoder.encode(input);
    }
    private static boolean matches(BCryptPasswordEncoder encoder, String input, String hash) {
        operations++; return encoder.matches(input, hash);
    }
    public static void main(String[] args) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        String control = prefix(70) + cp(0x00e9);
        require(bytes(control).length == 72 && control.length() == 71);
        require(PasswordPolicy.violationKey(control) == null);
        String hash = encode(encoder, control);
        boolean correct = matches(encoder, control, hash);
        boolean wrong = matches(encoder, "B" + control.substring(1), hash);
        require(correct && !wrong);
        StringBuilder output = new StringBuilder("{\"control\":{\"utf16Units\":71,\"utf8Bytes\":72,\"knownMatches\":")
            .append(correct).append(",\"wrongMatches\":").append(wrong).append("},\"pairs\":[");
        int[][] points = {{0x00e9, 0x00ea}, {0x20ac, 0x20ad}, {0x1f600, 0x1f601}};
        for (int i = 0; i < points.length; i++) {
            String shared = prefix(71);
            String left = shared + cp(points[i][0]);
            String right = shared + cp(points[i][1]);
            byte[] a = bytes(left), b = bytes(right);
            int width = i + 2;
            boolean prefixEqual = Arrays.equals(Arrays.copyOf(a, 72), Arrays.copyOf(b, 72));
            boolean fullDifferent = !Arrays.equals(a, b) && !left.equals(right);
            boolean policyAllowed = PasswordPolicy.violationKey(left) == null
                && PasswordPolicy.violationKey(right) == null;
            require(bytes(cp(points[i][0])).length == width && bytes(cp(points[i][1])).length == width);
            require(a.length == 71 + width && b.length == 71 + width);
            require(left.length() == (width == 4 ? 73 : 72) && right.length() == left.length());
            require(prefixEqual && fullDifferent && policyAllowed);
            boolean observed = matches(encoder, right, encode(encoder, left));
            // Observed behavior is recorded; it is deliberately not the input oracle.
            if (i > 0) output.append(',');
            output.append("{\"codepointBytes\":").append(width)
                .append(",\"leftUtf16Units\":").append(left.length())
                .append(",\"rightUtf16Units\":").append(right.length())
                .append(",\"leftUtf8Bytes\":").append(a.length)
                .append(",\"rightUtf8Bytes\":").append(b.length)
                .append(",\"sameFirst72Bytes\":").append(prefixEqual)
                .append(",\"fullInputsDiffer\":").append(fullDifferent)
                .append(",\"packagedPolicyAllowsBoth\":").append(policyAllowed)
                .append(",\"differentSuffixMatches\":").append(observed).append('}');
        }
        require(operations == 9);
        output.append("],\"bcryptOperations\":").append(operations)
            .append(",\"independentOraclesPassed\":true}");
        System.out.println(output);
    }
}
