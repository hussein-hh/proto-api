from .celery import app as celery_app

# The patch will be applied through the middleware and render-build.sh script

__all__ = ('celery_app',)
