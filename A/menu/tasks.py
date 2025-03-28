from bucket import bucket
from celery import shared_task

# TODO : need to get async

def get_all_objects_task():
    return bucket.get_all_objects()


@shared_task
def get_one_object_tasks(key):
    return bucket.get_one_object(key=key)

@shared_task
def delete_object_tasks(key):
    return bucket.delete_object(key)