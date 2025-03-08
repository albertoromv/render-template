
from collections.abc import Sequence

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from books.models.models import Comment, Post
from books.schemas import schemas

from books.database import get_async_session

from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter()


async def pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
) -> tuple[int, int]:
    capped_limit = min(100, limit)
    return (skip, capped_limit)


# eager loading
# async database needs options and selectinload to make sure that Post.comments is loaded!!
async def get_post_or_404(
    id: int, session: AsyncSession = Depends(get_async_session)
) -> Post:
    select_query = (
        select(Post).options(selectinload(Post.comments)).where(Post.id == id)
    )
    result = await session.execute(select_query)
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return post


@router.get("/posts", response_model=list[schemas.PostRead])
async def list_posts(
    pagination: tuple[int, int] = Depends(pagination),
    session: AsyncSession = Depends(get_async_session),
) -> Sequence[Post]:
    skip, limit = pagination
    select_query = (
        select(Post).options(selectinload(Post.comments)).offset(skip).limit(limit)
    )
    result = await session.execute(select_query)

    return result.scalars().all()


@router.get("/posts/{id}", response_model=schemas.PostRead)
async def get_post(post: Post = Depends(get_post_or_404)) -> Post:
    return post


# Now, when we POST /posts , the ORM Model Post has an empty list which is comments
@router.post(
    "/posts", response_model=schemas.PostRead, status_code=status.HTTP_201_CREATED
)
async def create_post(
    post_create: schemas.PostCreate, session: AsyncSession = Depends(get_async_session)
) -> Post:
    post = Post(**post_create.model_dump(), comments=[])
    session.add(post)
    await session.commit()

    return post


@router.patch("/posts/{id}", response_model=schemas.PostRead)
async def update_post(
    post_update: schemas.PostPartialUpdate,
    post: Post = Depends(get_post_or_404),
    session: AsyncSession = Depends(get_async_session),
) -> Post:
    post_update_dict = post_update.model_dump(exclude_unset=True)
    for key, value in post_update_dict.items():
        setattr(post, key, value)

    session.add(post)
    await session.commit()

    return post


@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post: Post = Depends(get_post_or_404),
    session: AsyncSession = Depends(get_async_session),
):
    await session.delete(post)
    await session.commit()


# To post comments on a post
# POST /posts/{id}/comments
@router.post(
    "/posts/{id}/comments",
    response_model=schemas.CommentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    comment_create: schemas.CommentCreate,
    post: Post = Depends(get_post_or_404),
    session: AsyncSession = Depends(get_async_session),
) -> Comment:
    comment = Comment(**comment_create.model_dump(), post=post)
    session.add(comment)
    await session.commit()

    return comment


