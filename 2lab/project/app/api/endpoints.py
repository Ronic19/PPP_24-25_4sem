from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy import select
from secrets import token_hex

from ..db.session import get_session, engine
from ..models.users import UserModel, Base
from ..schemas.user_schema import UserLoginSchema


router = APIRouter()

Session = Annotated[AsyncSession, Depends(get_session)]

user_me = {
    'id': None, 
    'email': None,
    'token': None
    }


@router.post("/setup_db")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {'ok': True}


# получение информации о всех пользователях
@router.get("/users")
async def get_users(session: Session):
    query = select(UserModel)
    result = await session.execute(query)

    return result.scalars().all()


@router.post("/sign-up")
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


@router.post("/login")
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


@router.get("/users/me/")
def get_current_user():
    user_me_copy = user_me.copy()
    del user_me_copy['token']
    return user_me_copy

