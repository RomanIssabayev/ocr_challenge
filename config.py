import os

class Config:
    SECRET_KEY = "asdasd"
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_BINDS = {
        "users": "sqlite:///users.db"
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_PASSWORD = "ExxComp2025"
    ADMIN_LOGIN = "admin@admin.com"
    ADMIN_ACCESS = 3
