import re
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_lenght=4,
        max_lenght=20,
        description="Имя пользователя (только буквы и цифры)"
    )
    email: EmailStr = Field(
        ...,
        description="Имейл пользователя"
    )
    password: str = Field(
        ...,
        description="Пароль (минимум 1 заглавная, 1 цифра и 1 спецсимвол)"
    )
    confirm_password: str = Field(
        ...,
        description="Подтверждение пароля"
    )
    age: int = Field(
        ...,
        ge=18,
        le=100,
        description="Возраст( от 18 до 100 лет)"
    )

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError('Username must contain only letters and numbers')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*]', v):
            raise ValueError('Password must contain at least one specieal character')
        return v

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserCreate':
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
