from django.utils import timezone


def year(request):
    now = timezone.now().year
    return {
        'year': now
    }
