from pydantic import BaseModel, Field

class LoginDto(BaseModel):
    username: str
    password: str