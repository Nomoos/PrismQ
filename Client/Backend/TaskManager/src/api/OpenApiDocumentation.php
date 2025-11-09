<?php
/**
 * OpenAPI Documentation
 * 
 * Complete OpenAPI specification for TaskManager API.
 * This file is scanned to generate the openapi.json file.
 */

use OpenApi\Attributes as OA;

/**
 * @OA\OpenApi(
 *     @OA\Info(
 *         version="1.0.0",
 *         title="TaskManager API",
 *         description="Lightweight PHP Task Queue with Data-Driven API for shared hosting environments. Provides REST API for managing task types and tasks with JSON schema validation, deduplication, and worker coordination.",
 *         @OA\Contact(name="PrismQ", url="https://github.com/Nomoos/PrismQ.Client")
 *     ),
 *     @OA\Server(url="/api", description="TaskManager API Server"),
 *     security={{"apiKey": {}}},
 *     @OA\SecurityScheme(
 *         securityScheme="apiKey",
 *         type="apiKey",
 *         in="header",
 *         name="X-API-Key",
 *         description="API key authentication. Include your API key in the X-API-Key header."
 *     ),
 *     @OA\Tag(name="Health", description="Health check and system status"),
 *     @OA\Tag(name="Task Types", description="Task type registration and management"),
 *     @OA\Tag(name="Tasks", description="Task creation, claiming, and completion")
 * )
 */

/**
 * @OA\Get(
 *     path="/health",
 *     operationId="healthCheck",
 *     summary="Health check endpoint",
 *     tags={"Health"},
 *     security={},
 *     @OA\Response(
 *         response=200,
 *         description="System is healthy",
 *         @OA\JsonContent(
 *             @OA\Property(property="status", type="string", example="healthy"),
 *             @OA\Property(property="timestamp", type="integer", example=1699372800),
 *             @OA\Property(property="database", type="string", example="connected")
 *         )
 *     )
 * )
 */

/**
 * @OA\Post(
 *     path="/task-types/register",
 *     operationId="registerTaskType",
 *     summary="Register or update a task type",
 *     tags={"Task Types"},
 *     @OA\RequestBody(
 *         required=true,
 *         @OA\JsonContent(
 *             required={"name", "version", "param_schema"},
 *             @OA\Property(property="name", type="string", example="PrismQ.Script.Generate", description="Unique task type identifier"),
 *             @OA\Property(property="version", type="string", example="1.0.0", description="Schema version"),
 *             @OA\Property(
 *                 property="param_schema",
 *                 type="object",
 *                 description="JSON Schema for parameter validation",
 *                 example={
 *                     "type": "object",
 *                     "properties": {
 *                         "topic": {"type": "string", "minLength": 1},
 *                         "style": {"type": "string", "enum": {"formal", "casual", "technical"}}
 *                     },
 *                     "required": {"topic", "style"}
 *                 }
 *             )
 *         )
 *     ),
 *     @OA\Response(
 *         response=200,
 *         description="Task type registered successfully",
 *         @OA\JsonContent(
 *             @OA\Property(property="id", type="integer", example=1),
 *             @OA\Property(property="name", type="string", example="PrismQ.Script.Generate"),
 *             @OA\Property(property="version", type="string", example="1.0.0"),
 *             @OA\Property(property="created", type="boolean", example=true),
 *             @OA\Property(property="updated", type="boolean", example=false)
 *         )
 *     ),
 *     @OA\Response(response=400, description="Invalid request or validation error"),
 *     @OA\Response(response=401, description="Unauthorized - Invalid API key")
 * )
 */

/**
 * @OA\Get(
 *     path="/task-types/{name}",
 *     operationId="getTaskType",
 *     summary="Get a specific task type by name",
 *     tags={"Task Types"},
 *     @OA\Parameter(
 *         name="name",
 *         in="path",
 *         required=true,
 *         description="Task type name",
 *         @OA\Schema(type="string", example="PrismQ.Script.Generate")
 *     ),
 *     @OA\Response(
 *         response=200,
 *         description="Task type details",
 *         @OA\JsonContent(
 *             @OA\Property(property="id", type="integer", example=1),
 *             @OA\Property(property="name", type="string", example="PrismQ.Script.Generate"),
 *             @OA\Property(property="version", type="string", example="1.0.0"),
 *             @OA\Property(property="param_schema", type="object"),
 *             @OA\Property(property="is_active", type="boolean", example=true)
 *         )
 *     ),
 *     @OA\Response(response=401, description="Unauthorized - Invalid API key"),
 *     @OA\Response(response=404, description="Task type not found")
 * )
 */

/**
 * @OA\Get(
 *     path="/task-types",
 *     operationId="listTaskTypes",
 *     summary="List all task types",
 *     tags={"Task Types"},
 *     @OA\Parameter(
 *         name="active_only",
 *         in="query",
 *         required=false,
 *         description="Filter to only active task types",
 *         @OA\Schema(type="boolean", default=false)
 *     ),
 *     @OA\Response(
 *         response=200,
 *         description="List of task types",
 *         @OA\JsonContent(
 *             type="array",
 *             @OA\Items(
 *                 @OA\Property(property="id", type="integer"),
 *                 @OA\Property(property="name", type="string"),
 *                 @OA\Property(property="version", type="string"),
 *                 @OA\Property(property="is_active", type="boolean")
 *             )
 *         )
 *     ),
 *     @OA\Response(response=401, description="Unauthorized - Invalid API key")
 * )
 */

/**
 * @OA\Post(
 *     path="/tasks",
 *     operationId="createTask",
 *     summary="Create a new task",
 *     tags={"Tasks"},
 *     @OA\RequestBody(
 *         required=true,
 *         @OA\JsonContent(
 *             required={"type", "params"},
 *             @OA\Property(property="type", type="string", example="PrismQ.Script.Generate", description="Task type name"),
 *             @OA\Property(
 *                 property="params",
 *                 type="object",
 *                 description="Task parameters (validated against task type schema)",
 *                 example={"topic": "AI in Healthcare", "style": "formal", "length": 1500}
 *             )
 *         )
 *     ),
 *     @OA\Response(
 *         response=200,
 *         description="Task created or existing task returned",
 *         @OA\JsonContent(
 *             @OA\Property(property="id", type="integer", example=123),
 *             @OA\Property(property="type", type="string", example="PrismQ.Script.Generate"),
 *             @OA\Property(property="status", type="string", example="pending"),
 *             @OA\Property(property="dedupe_key", type="string", example="abc123..."),
 *             @OA\Property(property="duplicate", type="boolean", example=false)
 *         )
 *     ),
 *     @OA\Response(response=400, description="Invalid request or parameter validation failed"),
 *     @OA\Response(response=401, description="Unauthorized - Invalid API key"),
 *     @OA\Response(response=404, description="Task type not found")
 * )
 */

/**
 * @OA\Post(
 *     path="/tasks/claim",
 *     operationId="claimTask",
 *     summary="Claim a pending task for processing",
 *     tags={"Tasks"},
 *     @OA\RequestBody(
 *         required=true,
 *         @OA\JsonContent(
 *             required={"worker_id", "task_type_id"},
 *             @OA\Property(property="worker_id", type="string", example="worker-001", description="Unique worker identifier"),
 *             @OA\Property(property="task_type_id", type="integer", example=1, description="Specific task type ID to claim"),
 *             @OA\Property(property="type_pattern", type="string", example="PrismQ.Script.%", description="Optional: filter by type pattern (SQL LIKE syntax)"),
 *             @OA\Property(property="sort_by", type="string", enum={"created_at", "priority", "id", "attempts"}, default="created_at", description="Optional: field to sort by"),
 *             @OA\Property(property="sort_order", type="string", enum={"ASC", "DESC"}, default="ASC", description="Optional: sort direction")
 *         )
 *     ),
 *     @OA\Response(
 *         response=200,
 *         description="Task claimed successfully",
 *         @OA\JsonContent(
 *             @OA\Property(property="id", type="integer", example=123),
 *             @OA\Property(property="type", type="string", example="PrismQ.Script.Generate"),
 *             @OA\Property(property="params", type="object"),
 *             @OA\Property(property="attempts", type="integer", example=1),
 *             @OA\Property(property="priority", type="integer", example=0)
 *         )
 *     ),
 *     @OA\Response(response=400, description="Invalid request - Invalid sort_by or sort_order"),
 *     @OA\Response(response=401, description="Unauthorized - Invalid API key"),
 *     @OA\Response(response=404, description="No tasks available")
 * )
 */

/**
 * @OA\Post(
 *     path="/tasks/{id}/complete",
 *     operationId="completeTask",
 *     summary="Mark a task as completed or failed",
 *     tags={"Tasks"},
 *     @OA\Parameter(
 *         name="id",
 *         in="path",
 *         required=true,
 *         description="Task ID",
 *         @OA\Schema(type="integer")
 *     ),
 *     @OA\RequestBody(
 *         required=true,
 *         @OA\JsonContent(
 *             required={"worker_id", "success"},
 *             @OA\Property(property="worker_id", type="string", example="worker-001"),
 *             @OA\Property(property="success", type="boolean", example=true),
 *             @OA\Property(property="result", type="object", description="Task result (required if success=true)"),
 *             @OA\Property(property="error", type="string", description="Error message (required if success=false)")
 *         )
 *     ),
 *     @OA\Response(
 *         response=200,
 *         description="Task completed successfully",
 *         @OA\JsonContent(
 *             @OA\Property(property="success", type="boolean", example=true),
 *             @OA\Property(property="message", type="string", example="Task completed successfully")
 *         )
 *     ),
 *     @OA\Response(response=400, description="Invalid request"),
 *     @OA\Response(response=401, description="Unauthorized - Invalid API key"),
 *     @OA\Response(response=404, description="Task not found")
 * )
 */

/**
 * @OA\Get(
 *     path="/tasks/{id}",
 *     operationId="getTask",
 *     summary="Get task status and details",
 *     tags={"Tasks"},
 *     @OA\Parameter(
 *         name="id",
 *         in="path",
 *         required=true,
 *         description="Task ID",
 *         @OA\Schema(type="integer")
 *     ),
 *     @OA\Response(
 *         response=200,
 *         description="Task details",
 *         @OA\JsonContent(
 *             @OA\Property(property="id", type="integer"),
 *             @OA\Property(property="type", type="string"),
 *             @OA\Property(property="status", type="string", enum={"pending", "claimed", "completed", "failed"}),
 *             @OA\Property(property="params", type="object"),
 *             @OA\Property(property="result", type="object"),
 *             @OA\Property(property="error_message", type="string"),
 *             @OA\Property(property="attempts", type="integer"),
 *             @OA\Property(property="created_at", type="string", format="date-time"),
 *             @OA\Property(property="completed_at", type="string", format="date-time")
 *         )
 *     ),
 *     @OA\Response(response=401, description="Unauthorized - Invalid API key"),
 *     @OA\Response(response=404, description="Task not found")
 * )
 */

/**
 * @OA\Get(
 *     path="/tasks",
 *     operationId="listTasks",
 *     summary="List tasks with optional filters",
 *     tags={"Tasks"},
 *     @OA\Parameter(name="status", in="query", description="Filter by status", @OA\Schema(type="string", enum={"pending", "claimed", "completed", "failed"})),
 *     @OA\Parameter(name="type", in="query", description="Filter by type (supports SQL LIKE patterns)", @OA\Schema(type="string")),
 *     @OA\Parameter(name="limit", in="query", description="Maximum number of results", @OA\Schema(type="integer", default=10)),
 *     @OA\Parameter(name="offset", in="query", description="Result offset for pagination", @OA\Schema(type="integer", default=0)),
 *     @OA\Response(
 *         response=200,
 *         description="List of tasks",
 *         @OA\JsonContent(
 *             type="array",
 *             @OA\Items(
 *                 @OA\Property(property="id", type="integer"),
 *                 @OA\Property(property="type", type="string"),
 *                 @OA\Property(property="status", type="string"),
 *                 @OA\Property(property="created_at", type="string", format="date-time")
 *             )
 *         )
 *     ),
 *     @OA\Response(response=401, description="Unauthorized - Invalid API key")
 * )
 */

class OpenApiDocumentation
{
    // This class only exists to hold OpenAPI documentation
}
