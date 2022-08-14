from fastapi import FastAPI

from routers import user, authentication, league, achievement
from database import engine
from form import models

from datetime import datetime

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(league.router)
app.include_router(achievement.router)

@app.get("/")
def hello():
    return {
        "utcnow": str(datetime.utcnow()),
        "now": str(datetime.now()),
        "utcnow_timestamp": datetime.utcnow().timestamp(),
        "now_timestamp": datetime.now().timestamp()
    }