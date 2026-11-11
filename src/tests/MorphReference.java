import edu.internet2.middleware.morphString.Morph;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class MorphReference {
  public static void main(String[] args) throws Exception {
    BufferedReader in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
    String key = new String(Base64.getDecoder().decode(in.readLine()), StandardCharsets.UTF_8);
    String value = new String(Base64.getDecoder().decode(in.readLine()), StandardCharsets.UTF_8);
    Properties properties = new Properties();
    properties.setProperty("encrypt.key", key);
    properties.setProperty("encrypt.disableExternalFileLookup", "true");
    try (OutputStream out = new FileOutputStream("morphString.properties")) {
      properties.store(out, "Generated test-only input");
    }
    String encrypted = Morph.encrypt(value);
    System.out.println("CIPHER=" + encrypted);
    System.out.println("PLAIN=" + Base64.getEncoder().encodeToString(Morph.decrypt(encrypted).getBytes(StandardCharsets.UTF_8)));
  }
}
