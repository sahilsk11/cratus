package hello;

import org.json.simple.JSONArray;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

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
            FileReader reader = new FileReader("/Users/sahil/OneDrive - purdue.edu/Portfolio/endpointspeed/database.json");
            try {
                Object obj = jsonParser.parse(reader);
                JSONArray employeeList = (JSONArray) obj;
                return employeeList.toJSONString();
            } catch (ParseException e) {
                System.out.println(e.getMessage());
                return "";
            } catch (IOException e) {
                System.out.println(e.getMessage());
                return "";
            }
        } catch (FileNotFoundException e) {
            System.out.println(e.getMessage());
            return "";
        }
    }

    @RequestMapping("/writedata")
    public String writeJSON() {
        JSONParser jsonParser = new JSONParser();
        try {
            FileReader reader = new FileReader("/Users/sahil/OneDrive - purdue.edu/Portfolio/endpointspeed/database.json");
            try {
                Object obj = jsonParser.parse(reader);
                JSONArray employeeList = (JSONArray) obj;

                FileWriter f = new FileWriter("/Users/sahil/OneDrive - purdue.edu/Portfolio/endpointspeed/output.json");
                f.write(employeeList.toJSONString());
                f.flush();
                return "done";
            } catch (ParseException e) {
                System.out.println(e.getMessage());
                return "";
            } catch (IOException e) {
                System.out.println(e.getMessage());
                return "";
            }
        } catch (FileNotFoundException e) {
            System.out.println(e.getMessage());
            return "";
        }
    }

    public static void main(String[] args) {
        SpringApplication.run(Endpoint.class, args);
    }

}
