from celery import Celery
import redislite
import time

from ..services.bradley import bradley


celery_app = Celery("TASKS")
redis_connection = redislite.Redis('/tmp/redis_example.rdb')

celery_app.conf.broker_url = "redis+socket://" + redis_connection.socket_file
celery_app.conf.result_backend = "redis+socket://" + redis_connection.socket_file


@celery_app.task(bind=True, name='project.app.celery_tasks.tasks.get_binary_image')
def get_binary_image(self):

    with open("3lab/project/app/services/img_str.txt", "r") as fh:
        img_str = fh.read().strip()
    result = bradley(img_str)

    for i in range(1, 11):
        time.sleep(0.3)
        self.update_state(
            state='PROGRESS',
            meta={'progress': f"{i * 10}%"}
        )
     
    return result