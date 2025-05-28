from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
    model_config = ConfigDict(extra='forbid')


class ImageStr(BaseModel):
    img_str: str = Field(max_length=10000000)
