import os

class Config:
    SECRET_KEY = "dev-secret-key"
    DATABASE_PATH = os.path.join("instance", "todo.db")