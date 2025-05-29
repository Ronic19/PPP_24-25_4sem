from fastapi import APIRouter, Depends, HTTPException, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy import select
from secrets import token_hex
import asyncio
from pydantic import ValidationError

from ..db.session import get_session
from ..models.users import UserModel
from ..schemas.user_schema import UserLoginSchema
from ..websocket.websocket_connection import *
from ..celery_tasks.tasks import *


router = APIRouter()


Session = Annotated[AsyncSession, Depends(get_session)]

user_me = {
    'id': None, 
    'email': None,
    'token': None
    }

# получение информации о всех пользователях
@router.get("/users", tags=['Все пользователи 🕊️'])
async def get_users(session: Session):
    query = select(UserModel)
    result = await session.execute(query)

    return result.scalars().all()


@router.post("/sign-up", tags=['Зарегистрироваться 🦜'])
async def sign_up(data: UserLoginSchema, session: Session):

    query = select(UserModel).filter_by(email=data.email)
    result = await session.execute(query)

    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Пользователь уже зарегистрирован")

    new_user = UserModel(
        email=data.email, 
        password=data.password
    )
    session.add(new_user)
    await session.commit()

    query = select(UserModel).filter_by(email=data.email)
    result = await session.execute(query)
    user = result.scalars().one()
    user_me['id'] = user.id
    user_me['email'] = user.email
    user_me['token'] = token_hex()

    return user_me


@router.post("/login", tags=['Войти в систему 🦚'])
async def login(data: UserLoginSchema, session: Session):
    query = select(UserModel).filter_by(email=data.email, password=data.password)
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    user_me['id'] = user.id
    user_me['email'] = user.email
    user_me['token'] = token_hex()

    return user_me


@router.get("/users/me", tags=['Текущий пользователь 🦩'])
def get_current_user():
    user_me_copy = user_me.copy()
    del user_me_copy['token']
    return user_me_copy


@router.websocket("/ws/{user_email}")
async def websocket_endpoint(websocket: WebSocket, user_email: str, session: Session):
    await manager.connect(user_email, websocket)
    try:
        while True:
            data_str = await websocket.receive_text()
            data = data_str.split()
            if data[0] == 'login' and len(data) == 3:

                try:
                    login_data = UserLoginSchema(
                        email=data[1],
                        password=data[2]
                    )
                    try:
                        await login(login_data, session)
                        await manager.send_message(user_email, {
                            "status": "SUCCESS", 
                            "email": user_me["email"], 
                            "token": user_me["token"]
                            })
                    except HTTPException as e:
                        await manager.send_message(user_email, {
                            "status": "ERROR",
                            "detail": str(e.detail)
                        })
                except ValidationError:
                    await manager.send_message(user_email, {
                        "status": "ERROR",
                        "detail": "некорректный email"
                    })

            elif data[0] == 'signup' and len(data) == 3:
                try:
                    login_data = UserLoginSchema(
                        email=data[1],
                        password=data[2]
                    )

                    try:
                        await sign_up(login_data, session)
                        await manager.send_message(user_email, {
                            "status": "SUCCESS", 
                            "email": user_me["email"], 
                            "token": user_me["token"]
                            })
                    except HTTPException as e:
                        await manager.send_message(user_email, {
                            "status": "ERROR",
                            "detail": str(e.detail)
                    })
                        
                except ValidationError:
                    await manager.send_message(user_email, {
                        "status": "ERROR",
                        "detail": "некорректный email"
                    })

            elif data_str == 'task':
                if user_me['email'] is None:
                    await manager.send_message(user_email, {
                        "status": "ERROR",
                        "detail": "Авторизуйтесь, пожалуйста"})
                else:
                    task = get_binary_image.delay()
                    await manager.send_message(user_email, {
                        "status": "STARTED", 
                        "task_id": task.id
                        })

                    while not task.ready():
                        if isinstance(task.info, dict):
                            await manager.send_message(user_email, {
                                "status": "PROGRESS", 
                                "task_id": task.id, 
                                "progress": task.info.get('progress')
                                })
                            await asyncio.sleep(0.5)
                    await manager.send_message(user_email, {
                        "status": "SUCCESS", 
                        "task_id": task.id, 
                        "res": task.get()
                        })
            
            else:
                await manager.send_message(user_email, {
                    "status": "ERROR", 
                    "detail": "неверная команда",
                    "cmd": data_str
                    })
    except WebSocketDisconnect:
        manager.disconnect(user_email, websocket)

