from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_GET
def healthz(request):
    """
    Health check endpoint for container orchestrators, PaaS health checks, and UptimeRobot.
    Verifies database connectivity and returns 200 (healthy) or 503 (unhealthy).
    Never exposes internal credentials, connection strings, or raw traces.
    """
    try:
        connection.ensure_connection()
        return JsonResponse({
            'status': 'ok',
            'database': 'connected'
        }, status=200)
    except Exception as exc:
        logger.error("Health check database probe failed: %s", exc)
        return JsonResponse({
            'status': 'error',
            'database': 'unreachable'
        }, status=503)
