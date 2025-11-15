from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Text, TypeDecorator
from sqlalchemy.orm import validates
from typing import Union
import bcrypt

class Base(DeclarativeBase):
 pass

