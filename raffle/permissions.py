from django.conf import settings





def is_manager_ip(request):
    """
    Check if the request IP is a manager IP.

    Args:
        request (Request): The current request object.

    Returns:
        bool: True if the request IP is a manager IP, False otherwise.
    """
    manager_ips = settings.MANAGER_IPS.split(',')
    request_ip = request.META.get('REMOTE_ADDR')
    return request_ip in manager_ips
