import os

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 min
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 2  # 2 days
ALGORITHM = "HS256"

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
