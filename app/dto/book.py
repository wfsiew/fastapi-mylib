from pydantic import BaseModel, Field

class RegisterBookDto(BaseModel):
    isbn: str
    username: str