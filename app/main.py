from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, books

import uvicorn, asyncpg

app = FastAPI(dependencies=[], title='Lib', description='Lib API description', version='1.0')
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


@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(user='postgres', password='postgres', database='libdb', host='localhost', port=5432, max_size=50)

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
