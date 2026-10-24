package com.hotelapp.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hotelapp.config.Messages;
import com.hotelapp.exception.GlobalExceptionHandler;
import com.hotelapp.service.FileStorageService;
import com.hotelapp.service.MessageService;
import jakarta.servlet.MultipartConfigElement;
import org.apache.catalina.startup.Tomcat;
import org.apache.catalina.util.ServerInfo;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.AnnotatedBeanDefinitionReader;
import org.springframework.core.SpringVersion;
import org.springframework.security.web.method.annotation.AuthenticationPrincipalArgumentResolver;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.support.DefaultListableBeanFactory;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.multipart.support.StandardServletMultipartResolver;
import org.springframework.web.servlet.DispatcherServlet;
import org.springframework.web.servlet.HandlerExceptionResolver;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.context.support.GenericWebApplicationContext;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CopyOnWriteArrayList;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verifyNoInteractions;

/** Real loopback parser/resolver slice; no database, auth chain or storage calls. */
class MultipartParserCleanupTest {
    private static final String ROUTE = "/api/messages/conversations/-1/attachment";
    private static final String BOUNDARY = "A05SmallFixtureBoundary";

    record FilesSnapshot(long count, long bytes) {}
    record ErrorSnapshot(String stage, boolean handlerPresent, boolean attachmentHandler,
                         List<String> causes, FilesSnapshot files) {}

    static class Observations {
        Path spool;
        volatile String stage;
        final List<ErrorSnapshot> errors = new CopyOnWriteArrayList<>();
        FilesSnapshot files() throws java.io.IOException {
            try (var stream = Files.list(spool)) {
                var paths = stream.filter(Files::isRegularFile).toList();
                assertThat(paths.size()).isLessThanOrEqualTo(4);
                long bytes = 0;
                for (Path path : paths) bytes += Files.size(path);
                return new FilesSnapshot(paths.size(), bytes);
            }
        }
    }

    @Configuration
    @EnableWebMvc
    static class Slice implements WebMvcConfigurer {
        @Bean MessageController messages(@Autowired MessageService messageService,
                                         @Autowired FileStorageService storage) {
            return new MessageController(messageService, storage);
        }
        @Bean GlobalExceptionHandler advice() { return new GlobalExceptionHandler(mock(Messages.class)); }
        @Bean Observations observations() { return new Observations(); }
        @Bean StandardServletMultipartResolver multipartResolver() {
            return new StandardServletMultipartResolver();
        }
        @Bean Health health() { return new Health(); }
        @Override public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
            resolvers.add(new AuthenticationPrincipalArgumentResolver());
        }
        @Override public void extendHandlerExceptionResolvers(List<HandlerExceptionResolver> resolvers) {
            resolvers.add(0, (request, response, handler, error) -> {
                if (ROUTE.equals(request.getRequestURI())) {
                    var causes = new ArrayList<String>();
                    for (Throwable cause = error; cause != null && causes.size() < 8; cause = cause.getCause()) {
                        causes.add(cause.getClass().getName());
                    }
                    try {
                        observations().errors.add(new ErrorSnapshot(observations().stage, handler != null,
                                handler instanceof HandlerMethod method
                                        && method.getBeanType() == MessageController.class
                                        && method.getMethod().getName().equals("sendAttachment"),
                                causes, observations().files()));
                    } catch (java.io.IOException e) {
                        throw new IllegalStateException("Cannot inspect fixture spool metadata", e);
                    }
                }
                return null; // Delegate unchanged to the actual advice/default resolver chain.
            });
        }
    }

    @RestController
    static class Health {
        @GetMapping("/fixture-health") String health() { return "ok"; }
    }

    private static byte[] body(boolean terminated) {
        // One inert four-byte file under the wrong part name: binding must stop
        // before calling the real attachment method or its mocked dependencies.
        String value = "--" + BOUNDARY + "\r\nContent-Disposition: form-data; name=\"probe\"; "
                + "filename=\"probe.txt\"\r\nContent-Type: text/plain\r\n\r\nTEST";
        if (terminated) value += "\r\n--" + BOUNDARY + "--\r\n";
        byte[] result = value.getBytes(StandardCharsets.US_ASCII);
        assertThat(result.length).isLessThan(8192);
        return result;
    }

    private static HttpResponse<Void> post(HttpClient client, String base, boolean terminated) throws Exception {
        return client.send(HttpRequest.newBuilder(URI.create(base + ROUTE))
                .timeout(Duration.ofSeconds(10))
                .header("Content-Type", "multipart/form-data; boundary=" + BOUNDARY)
                .POST(HttpRequest.BodyPublishers.ofByteArray(body(terminated))).build(),
                HttpResponse.BodyHandlers.discarding());
    }

    @Test
    void smallIncompletePartIsRejectedBeforeBindingAndSpoolReturnsToEmpty(@TempDir Path temp) throws Exception {
        Path spool = Files.createDirectory(temp.resolve("spool"));
        Tomcat tomcat = new Tomcat();
        tomcat.setBaseDir(temp.resolve("tomcat").toString());
        tomcat.setPort(0);
        tomcat.getConnector().setProperty("address", "127.0.0.1");
        var context = tomcat.addContext("", Files.createDirectory(temp.resolve("web")).toString());
        var factory = new DefaultListableBeanFactory();
        // Register already-mocked dependencies before refresh so Spring does
        // not inspect product service @Autowired methods in this parser slice.
        var messageService = mock(MessageService.class);
        var storage = mock(FileStorageService.class);
        factory.registerSingleton("messageService", messageService);
        factory.registerSingleton("fileStorageService", storage);
        var spring = new GenericWebApplicationContext(factory);
        spring.setServletContext(context.getServletContext());
        new AnnotatedBeanDefinitionReader(factory).register(Slice.class);
        var wrapper = Tomcat.addServlet(context, "mvc", new DispatcherServlet(spring));
        wrapper.setLoadOnStartup(1);
        // Current checked-in product limits; test-only spool location. Not a
        // measurement of production/deployment configuration.
        wrapper.setMultipartConfigElement(new MultipartConfigElement(spool.toString(),
                20L * 1024 * 1024, 25L * 1024 * 1024, 0));
        context.addServletMappingDecoded("/", "mvc");
        var result = new LinkedHashMap<String, Object>();
        try {
            tomcat.start();
            var observations = spring.getBean(Observations.class);
            observations.spool = spool;
            String base = "http://127.0.0.1:" + tomcat.getConnector().getLocalPort();
            var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5))
                    .version(HttpClient.Version.HTTP_1_1).followRedirects(HttpClient.Redirect.NEVER).build();
            assertThat(observations.files()).isEqualTo(new FilesSnapshot(0, 0));

            observations.stage = "wellformed";
            var control = post(client, base, true);
            assertThat(control.statusCode()).isBetween(400, 599);
            assertThat(observations.errors).hasSize(1);
            var parsed = observations.errors.get(0);
            assertThat(parsed.handlerPresent()).isTrue();
            assertThat(parsed.attachmentHandler()).isTrue();
            assertThat(parsed.causes()).contains(
                    "org.springframework.web.multipart.support.MissingServletRequestPartException");
            assertThat(parsed.files()).isEqualTo(new FilesSnapshot(1, 4));
            // Required gate: do not send malformed input if the ordinary control
            // left files behind, otherwise cleanup attribution is confounded.
            assertThat(observations.files()).isEqualTo(new FilesSnapshot(0, 0));

            observations.stage = "incomplete";
            var malformed = post(client, base, false);
            assertThat(malformed.statusCode()).isBetween(400, 599);
            assertThat(observations.errors).hasSize(2);
            var rejected = observations.errors.get(1);
            assertThat(rejected.handlerPresent()).isFalse();
            assertThat(rejected.attachmentHandler()).isFalse();
            assertThat(rejected.causes()).contains("org.springframework.web.multipart.MultipartException");
            assertThat(rejected.causes()).anyMatch(name -> name.startsWith("org.apache.tomcat.util.http.fileupload."));
            assertThat(observations.files()).isEqualTo(new FilesSnapshot(0, 0));
            var health = client.send(HttpRequest.newBuilder(URI.create(base + "/fixture-health"))
                    .timeout(Duration.ofSeconds(5)).GET().build(), HttpResponse.BodyHandlers.discarding());
            assertThat(health.statusCode()).isEqualTo(200);
            assertThat(observations.files()).isEqualTo(new FilesSnapshot(0, 0));
            verifyNoInteractions(messageService, storage);
            result.put("tomcat", ServerInfo.getServerNumber());
            result.put("spring", SpringVersion.getVersion());
            result.put("controlStatus", control.statusCode());
            result.put("incompleteStatus", malformed.statusCode());
            result.put("controlBodyBytes", body(true).length);
            result.put("incompleteBodyBytes", body(false).length);
            result.put("observations", observations.errors);
            result.put("spoolAfterResponses", observations.files());
            result.put("healthAfterStatus", health.statusCode());
            result.put("serviceInteractions", 0);
        } finally {
            try { tomcat.stop(); }
            finally { tomcat.destroy(); spring.close(); }
        }
        result.put("serverStopped", true);
        Files.writeString(Path.of("target/a05-parser-cleanup-result.json"),
                new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(result));
    }
}
