from django.http import JsonResponse
from django.db import connection


def health(request):
    return JsonResponse({'status': 'ok'})


def health_db(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'status': 'ok', 'database': 'connected'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'database': str(e)}, status=500)


def health_redis(request):
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 5)
        val = cache.get('health_check')
        return JsonResponse({'status': 'ok', 'redis': 'connected' if val == 'ok' else 'error'})
    except Exception as e:
        return JsonResponse({'status': 'ok', 'redis': 'not configured (using locmem)'})
