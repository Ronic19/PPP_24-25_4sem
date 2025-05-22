import uvicorn
from fastapi import FastAPI
from project.app.api.endpoints import router, user_me
from project.app.services.bradley import bradley
from project.app.models.users import Base
from sqlalchemy import create_engine
from pydantic import BaseModel, Field
import websockets
import asyncio



sync_engine = create_engine("sqlite:///project/app/db/users.db") 
Base.metadata.create_all(sync_engine)

app = FastAPI()
app.include_router(router)


# async def run_client():
#     uri = "ws://localhost:8000/ws/123?token=your_token_here"
#     async with websockets.connect(uri) as websocket:
#         async def listen():
#             while True:
#                 response = await websocket.recv()
#                 print("[NOTIFY]:", response)

#         listener = asyncio.create_task(listen())

#         while True:
#             cmd = input(">>> ").strip().lower()

#             if cmd == "exit":
#                 break

#             elif cmd == "login":
#                 email = input("email: ")
#                 password = input("password: ")

#                 _, image_data = cmd.split(" ", 1)

#                 await websocket.send(json.dumps({
#                     "action": "start_task",
#                     "image": image_data
#                 }))

#         listener.cancel()


async def main():
    print(f'Для регистрации введите singup')
    print(f'Для входа введите login')
    print(f'Для получения информации о текущем пользователе me')
    print(f'Для бинаризации изображение введите task')
    print(f'Для выхода введите exit')
    # await run_client()



if __name__ == "__main__":
    asyncio.run(main())
