from pydantic import BaseModel, EmailStr, ConfigDict


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
    model_config = ConfigDict(extra='forbid')

