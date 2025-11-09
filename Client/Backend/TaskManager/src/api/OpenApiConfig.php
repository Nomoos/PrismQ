<?php
/**
 * OpenAPI Base Configuration
 * 
 * This file contains the base OpenAPI specification attributes.
 * All endpoint-specific attributes are in their respective handler files.
 */

use OpenApi\Attributes as OA;

#[OA\Info(
    version: "1.0.0",
    title: "TaskManager API",
    description: "Lightweight PHP Task Queue with Data-Driven API for shared hosting environments. Provides REST API for managing task types and tasks with JSON schema validation, deduplication, and worker coordination.",
    contact: new OA\Contact(name: "PrismQ", url: "https://github.com/Nomoos/PrismQ.Client")
)]
#[OA\Server(
    url: "/api",
    description: "TaskManager API Server"
)]
#[OA\SecurityScheme(
    securityScheme: "apiKey",
    type: "apiKey",
    name: "X-API-Key",
    in: "header",
    description: "API key authentication. Include your API key in the X-API-Key header."
)]
#[OA\Tag(
    name: "Health",
    description: "Health check and system status"
)]
#[OA\Tag(
    name: "Task Types",
    description: "Task type registration and management"
)]
#[OA\Tag(
    name: "Tasks",
    description: "Task creation, claiming, and completion"
)]
class OpenApiConfig
{
    // This class only exists to hold OpenAPI base configuration
}
