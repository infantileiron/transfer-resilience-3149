import os
DATABASE_URL=os.getenv("DATABASE_URL","mysql+pymysql://transfer:transfer-demo@db/transfer?charset=utf8mb4")
REDIS_URL=os.getenv("REDIS_URL","redis://redis:6379/0")
JWT_SECRET=os.getenv("JWT_SECRET","transfer-resilience-development-secret-change")
SEED_DEMO=os.getenv("SEED_DEMO","true").lower()=="true"
