
import uvicorn
from fastapi import FastAPI
from project.app.api.endpoints import router
from project.app.services.bradley import bradley
from pydantic import BaseModel, Field


app = FastAPI()
app.include_router(router)


class ImageRequest(BaseModel):
    img_str: str = Field(max_length=1000000)


@app.post("/binary_image")
async def get_binary_image(request: ImageRequest):
    res = bradley(request.img_str)
    return {'result': res}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

