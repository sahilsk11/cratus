package hello;

import org.json.JSONArray;
import org.json.JSONObject;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletResponse;
import java.sql.*;


@SpringBootApplication
@RestController
public class Endpoint {

    @RequestMapping("/")
    public String healthcheck() {
        return "Java endpoint is up and running";
    }

    @RequestMapping("/helloworld")
    public String name() {
        return "hello world";
    }

    @RequestMapping("/get-mini-employees")
    public String getMiniEmployees(HttpServletResponse response) {
        response.setContentType("application/json");
        String url = "jdbc:postgresql://localhost:5432/cratus-data";
        String user = "postgres";
        String password = "postgres";

        try (Connection con = DriverManager.getConnection(url, user, password);
             Statement st = con.createStatement();
             ResultSet rs = st.executeQuery("SELECT * FROM mini_employee")) {
            String jsonString = "";

            JSONArray jsonArray = new JSONArray();
            JSONObject jsonobject = null;


            while (rs.next()) {

                ResultSetMetaData metaData = rs.getMetaData();
                jsonobject = new JSONObject();

                for (int i = 0; i < metaData.getColumnCount(); i++) {

                    jsonobject.put(metaData.getColumnLabel(i + 1),rs.getObject(i + 1));

                }

                jsonArray.put(jsonobject);
            }

            if (jsonArray.length() > 0) {

                jsonString= jsonArray.toString();

            }
            con.close();
            return jsonString;

        } catch (SQLException ex) {
            return "error: " + ex.getMessage();
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

    public static void main(String[] args) {
        SpringApplication.run(Endpoint.class, args);
    }
}
