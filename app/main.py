from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routers import auth, books

import uvicorn, asyncpg, logging

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
fh = logging.handlers.RotatingFileHandler('error.log', mode='a', maxBytes = 100*1024, backupCount = 3)
formatter = logging.Formatter(
    "%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d - %(levelname)s - %(message)s"
)
fh.setLevel(logging.ERROR)
fh.setFormatter(formatter)
logger.addHandler(fh)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(user='postgres', password='postgres', database='libdb', host='localhost', port=5432, max_size=50)
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan, dependencies=[], title='Lib', description='Lib API description', version='1.0')
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(books.router)


# @app.on_event("startup")
# async def startup():
#     app.state.pool = await asyncpg.create_pool(user='postgres', password='postgres', database='libdb', host='localhost', port=5432, max_size=50)

# @app.on_event("shutdown")
# async def shutdown():
#     await app.state.pool.close()


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
