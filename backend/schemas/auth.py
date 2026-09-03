from pydantic import BaseModel, EmailStr, Field

class RegisterSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class UpdateProfileSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
