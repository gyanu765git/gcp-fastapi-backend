from celery_app import celery

@celery.task(name='tasks.add')
def add(x, y):
    """Simple task that adds two numbers."""
    return x + y
