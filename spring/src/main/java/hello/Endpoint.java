package hello;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.io.*;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@SpringBootApplication
@RestController
public class Endpoint {

    @RequestMapping("/helloworld")
    public String name() {
        return "hello world";
    }

    @RequestMapping("/readdata")
    public String readJSON() {
        JSONParser jsonParser = new JSONParser();
        try {
            FileReader reader = new FileReader("../io/database.json");
            try {
                Object obj = jsonParser.parse(reader);
                JSONArray employeeList = (JSONArray) obj;
                return employeeList.toJSONString();
            } catch (ParseException e) {
                System.out.println(e.getMessage());
                return "error";
            } catch (IOException e) {
                System.out.println(e.getMessage());
                return "error";
            }
        } catch (FileNotFoundException e) {
            System.out.println(e.getMessage());
            return "error";
        }
    }

    @RequestMapping("/writedata")
    public String writeJSON() {
        JSONParser jsonParser = new JSONParser();
        try {
            FileReader reader = new FileReader("../io/database.json");
            try {
                Object obj = jsonParser.parse(reader);
                JSONArray employeeList = (JSONArray) obj;

                FileWriter f = new FileWriter("../io/output.json");
                f.write(employeeList.toJSONString());
                f.flush();
                return "done";
            } catch (ParseException e) {
                System.out.println(e.getMessage());
                return "error";
            } catch (IOException e) {
                System.out.println(e.getMessage());
                return "error";
            }
        } catch (FileNotFoundException e) {
            System.out.println(e.getMessage());
            return "error";
        }
    }

    @RequestMapping("/calculatefib")
    public int fib(@RequestParam(name = "n", defaultValue = "20") String n) {
        int nth;
        try {
            nth = new Integer(n);
        } catch (Exception e)
        {
            nth = 20;
        }
        return fibHelper(nth);
    }

    public int fibHelper(int n) {
        if (n == 0) {
            return 0;
        }
        if (n == 1) {
            return 1;
        }
        return fibHelper(n - 1) + fibHelper(n - 2);
    }

    @RequestMapping("/parsefile")
    public String countWord() {
        try {
            Map<String, Integer> dict = new HashMap<>();
            BufferedReader bf = new BufferedReader(new FileReader("../io/MobyDick.txt"));

            String st;
            Pattern p = Pattern.compile("[a-zA-Z]+");

            Matcher regMatch;
            while ((st = bf.readLine()) != null) {
                regMatch = p.matcher(st);
                while (regMatch.find()) {
                    String word = regMatch.group();
                    word = word.toLowerCase();
                    if (word != "") {
                        if (!dict.containsKey(word)) {
                            dict.put(word, 1);
                        } else {
                            dict.put(word, dict.get(word) + 1);
                        }
                    }
                }
            }
            bf.close();
            return new JSONObject(dict).toJSONString();
        } catch (Exception e) {
            return e.getMessage();
        }
    }

    public static void main(String[] args) {
        SpringApplication.run(Endpoint.class, args);
    }
}
