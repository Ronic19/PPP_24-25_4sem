import uvicorn
from fastapi import FastAPI
from project.app.api.endpoints import router, user_me
from project.app.services.bradley import bradley
from project.app.models.users import Base
from sqlalchemy import create_engine
from pydantic import BaseModel, Field


class ImageStr(BaseModel):
    img_str: str = Field(max_length=10000000)

sync_engine = create_engine("sqlite:///2lab/project/app/db/users.db") 
Base.metadata.create_all(sync_engine)

app = FastAPI()
app.include_router(router)

@app.post("/binary_image", tags=["Бинаризованное изображение 🦃"])
async def get_binary_image(image: ImageStr):
    if user_me['email'] is None:
        return {'result': 'Авторизуйтесь, пожалуйста O_o'}
    res = bradley(image.img_str)
    return {'result': res}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

