from celery import Celery
import redislite
import time

from ..services.bradley import bradley
from ..websocket.websocket_connection import manager


# Celery("<имя_объекта>")
celery_app = Celery("TASKS")

# создаем подключение к redislight
redis_connection = redislite.Redis('/tmp/redis_example.rdb')

# указываем Celery, где искать очередь задач
celery_app.conf.broker_url = "redis+socket://" + redis_connection.socket_file

# указываем Celery, где будем хранить результаты выполнения задач
celery_app.conf.result_backend = "redis+socket://" + redis_connection.socket_file


@celery_app.task(bind=True)
def get_binary_image(self, user_id: str, image: str):
    task_id = self.request.id

    manager.send_message(
        user_id, 
        {
            "status": "STARTED",
            "task_id": task_id,
            "algorithm": "bradley algorithm"
        }
    )

    for i in range(1, 11):
        time.sleep(0.5)
        manager.send_message(
                user_id, 
                {
                    "status": "PROGRESS",
                    "task_id": task_id,
                    "algorithm": i * 10
                }
        )
    
    result = bradley(image)
    manager.send_message(
        user_id, 
        {
            "status": "PROGRCOMPLETEDESS",
            "task_id": task_id,
            "binarized_image": result
        }
    )
    
