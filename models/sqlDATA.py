from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func


Base = declarative_base()

class User(Base):
    __tablename__ = "signin"
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, unique=True, index=True, nullable=False)
    hash_password = sa.Column(sa.String)
    is_logged_in = sa.Column(sa.Boolean, default=False)

    # Establishes a relationship with the Blog table
    blogs = relationship("Blog", back_populates="owner")

class Blog(Base):
    __tablename__ = "blogs"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    author = sa.Column(sa.String, nullable=False)
    title = sa.Column(sa.String, index=True, nullable=False)
    body = sa.Column(sa.Text, nullable=False)
    #Automatically sets the date to the current time
    date = sa.Column(sa.DateTime, default=sa.func.now())
    owner_id = sa.Column(sa.Integer, sa.ForeignKey("signin.id"), nullable=False)

    # Establishes a relationship with the User and Blog tables,
    # allowing you to access the owner of a blog and the blogs owned by a user.
    owner = relationship("User", back_populates="blogs")


class ResetCode(Base):
    __tablename__ = "py_code"
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String, index=True)
    reset_code = sa.Column(sa.String,unique=True, index=True)
    status = sa.Column(sa.String(1))
    expired_in = sa.Column(sa.DateTime)