import java.util.*;
import java.net.*;
import java.net.http.*;
import java.time.Duration;
import org.springframework.boot.SpringApplication;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.boot.web.servlet.context.ServletWebServerApplicationContext;
import org.springframework.boot.web.embedded.tomcat.TomcatWebServer;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;

public class MethodSnapshot {
  static final Map<String,Object> out = new LinkedHashMap<>();
  static void getters(String key,Object obj,String... methods) {
    Map<String,Object> values = new LinkedHashMap<>();
    values.put("class",obj.getClass().getName());
    for(String method:methods) try { values.put(method,obj.getClass().getMethod(method).invoke(obj)); }
      catch(NoSuchMethodException e) { values.put(method,"METHOD_ABSENT"); }
      catch(Exception e) { values.put(method,"ERROR:"+e.getClass().getSimpleName()); }
    out.put(key,values);
  }
  static List<Map<String,Object>> meters(MeterRegistry registry) {
    List<Map<String,Object>> result = new ArrayList<>();
    for(Timer timer:registry.find("http.server.requests").timers()) {
      Map<String,Object> row = new LinkedHashMap<>();
      Map<String,String> tags=new TreeMap<>();
      timer.getId().getTags().forEach(t->tags.put(t.getKey(),t.getValue()));
      row.put("tags",tags);row.put("count",timer.count());result.add(row);
    } return result;
  }
  public static void main(String[] args) throws Exception {
    TimeZone.setDefault(TimeZone.getTimeZone("Europe/Istanbul"));
    System.setProperty("user.timezone","Europe/Istanbul");
    try(ConfigurableApplicationContext ctx=SpringApplication.run(com.hotelapp.HotelStudentPlatformApplication.class,args)) {
      out.put("activeProfiles",ctx.getEnvironment().getActiveProfiles());
      out.put("observationRegistryClass",ctx.getBean(io.micrometer.observation.ObservationRegistry.class).getClass().getName());
      out.put("meterRegistryClass",ctx.getBean(MeterRegistry.class).getClass().getName());
      for(String type:List.of("io.micrometer.observation.ObservationRegistry","org.springframework.web.filter.ServerHttpObservationFilter","io.micrometer.core.instrument.MeterRegistry","org.springframework.web.multipart.MultipartResolver")) {
        out.put(type,Arrays.asList(ctx.getBeanNamesForType(Class.forName(type))));
      }
      ServletWebServerApplicationContext web=(ServletWebServerApplicationContext)ctx;
      Map<String,Object> filters=new TreeMap<>();
      web.getServletContext().getFilterRegistrations().forEach((n,r)-> {
        Map<String,Object> item=new LinkedHashMap<>();item.put("class",r.getClassName());
        item.put("urlPatterns",r.getUrlPatternMappings());item.put("servletNames",r.getServletNameMappings());filters.put(n,item);
      });out.put("servletFilters",filters);
      getters("multipartProperties",ctx.getBean(org.springframework.boot.autoconfigure.web.servlet.MultipartProperties.class),"isEnabled","getMaxFileSize","getMaxRequestSize","getFileSizeThreshold","getLocation","isResolveLazily");
      getters("multipartConfig",ctx.getBean(jakarta.servlet.MultipartConfigElement.class),"getMaxFileSize","getMaxRequestSize","getFileSizeThreshold","getLocation");
      out.put("java.io.tmpdir",System.getProperty("java.io.tmpdir"));
      Object temp=web.getServletContext().getAttribute("jakarta.servlet.context.tempdir");
      out.put("servletTempDir",temp==null?null:temp.toString());
      if(temp instanceof java.io.File dir) out.put("tempFilesystem",Map.of("exists",dir.exists(),"readable",dir.canRead(),"writable",dir.canWrite(),"usableBytes",dir.getUsableSpace(),"totalBytes",dir.getTotalSpace()));
      var server=(TomcatWebServer)web.getWebServer();
      getters("tomcatConnector",server.getTomcat().getConnector(),"getPort","getMaxParameterCount","getMaxPostSize","getMaxSavePostSize","getMaxPartCount","getMaxPartHeaderSize","getParseBodyMethods");
      getters("tomcatProtocol",server.getTomcat().getConnector().getProtocolHandler(),"getMaxSwallowSize","getMaxHttpRequestHeaderSize","getMaxHeaderCount","getConnectionTimeout","getMaxConnections","getMaxThreads");
      MeterRegistry registry=ctx.getBean(MeterRegistry.class);
      var client=HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).connectTimeout(Duration.ofSeconds(5)).followRedirects(HttpClient.Redirect.NEVER).build();
      var uri=URI.create("http://127.0.0.1:"+server.getPort()+"/actuator/health");
      try {
      out.put("requestStage","health-before-attempted");
      var before=client.send(HttpRequest.newBuilder(uri).timeout(Duration.ofSeconds(10)).GET().build(),HttpResponse.BodyHandlers.discarding());
      out.put("healthBefore",Map.of("method","GET","path","/actuator/health","status",before.statusCode()));
      Thread.sleep(200);
      out.put("metersBeforeCustom",meters(registry));
      if(before.statusCode()!=200) throw new IllegalStateException("Health-before gate failed; custom method not sent");
      out.put("requestStage","custom-attempted");
      var custom=client.send(HttpRequest.newBuilder(uri).timeout(Duration.ofSeconds(10)).method("A05CHECK",HttpRequest.BodyPublishers.noBody()).build(),HttpResponse.BodyHandlers.discarding());
      out.put("customRequest",Map.of("method","A05CHECK","path","/actuator/health","status",custom.statusCode()));
      Thread.sleep(200);
      out.put("metersAfterCustom",meters(registry));
      out.put("requestStage","health-after-attempted");
      var after=client.send(HttpRequest.newBuilder(uri).timeout(Duration.ofSeconds(10)).GET().build(),HttpResponse.BodyHandlers.discarding());
      out.put("healthAfter",Map.of("method","GET","path","/actuator/health","status",after.statusCode()));
      Thread.sleep(200);
      out.put("metersAfterHealth",meters(registry));
      out.put("requestStage","complete");
      } catch(Exception error) {
        out.put("requestErrorClass",error.getClass().getName());
      } finally {
        System.out.println("A05_METHOD_SNAPSHOT="+new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(out));
      }
    }
  }
}
