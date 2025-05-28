import uvicorn
from fastapi import FastAPI
from project.app.api.endpoints import router, user_me
from project.app.services.bradley import bradley
from project.app.models.users import Base
from sqlalchemy import create_engine
import multiprocessing
import subprocess
import os
import signal
import atexit
# from pydantic import BaseModel, Field


# class ImageStr(BaseModel):
#     img_str: str = Field(max_length=10000000)

sync_engine = create_engine("sqlite:///3lab/project/app/db/users.db") 
Base.metadata.create_all(sync_engine)

app = FastAPI()
app.include_router(router)

def run_celery():
    # Запускаем Celery worker
    cmd = "celery -A 3lab.project.app.celery_tasks.tasks worker --loglevel=info"
    subprocess.run(cmd, shell=True)

def cleanup():
    # Завершаем Celery процесс при выходе
    if 'celery_process' in globals():
        celery_process.terminate()

if __name__ == "__main__":
    # Регистрируем функцию очистки
    atexit.register(cleanup)
    
    # Запускаем Celery в отдельном процессе
    celery_process = multiprocessing.Process(target=run_celery)
    celery_process.start()
    
    # Запускаем FastAPI
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)