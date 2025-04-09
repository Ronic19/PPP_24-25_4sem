from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy import select
from secrets import token_hex

from ..db.session import get_session
from ..models.users import UserModel
from ..schemas.user_schema import UserLoginSchema


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
