import contextlib

from fastapi import FastAPI
from books.routers.book import router as book_router
from books.database import create_all_tables


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(book_router) # with a router

