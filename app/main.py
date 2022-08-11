from fastapi import FastAPI

from routers import user, authentication, league, achievement
from database import engine
from form import models

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(league.router)
app.include_router(achievement.router)