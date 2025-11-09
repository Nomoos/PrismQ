window.onload = function() {
  //<editor-fold desc="Changeable Configuration Block">

  // TaskManager API Configuration
  window.ui = SwaggerUIBundle({
    url: "/api/openapi.json",
    dom_id: '#swagger-ui',
    deepLinking: true,
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIStandalonePreset
    ],
    plugins: [
      SwaggerUIBundle.plugins.DownloadUrl
    ],
    layout: "StandaloneLayout",
    // Pre-authorize with API key if available
    onComplete: function() {
      // Users can set their API key using the Authorize button in Swagger UI
    }
  });

  //</editor-fold>
};
