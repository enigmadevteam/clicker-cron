from typing import Optional, Dict
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Table, MetaData, select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import asyncio
import const


class Item(BaseModel):
    chat_id: int
    reward: float

app = FastAPI()

sync_engine = create_engine(const.POSTGRES_URL)
metadata = MetaData()

# Use the synchronous engine to load metadata
table = Table('upgrade', metadata, autoload_with=sync_engine)
reward_lock = asyncio.Lock()

async_engine = create_async_engine(
    const.ASYNC_POSTGRES_URL,
)
metadata = MetaData()

original_rewards: Dict[int, float] = {}
update_tasks: Dict[int, asyncio.Task] = {}


async def update_reward_periodically(chat_id, reward_per_hour):
    for i in range(24):
        async with AsyncSession(async_engine) as session:
            stmt = select(table).where(table.c.chat_id == chat_id)
            result = await session.execute(stmt)
            row = result.fetchone()
            if row is not None:
                new_reward = row[1] + reward_per_hour
                stmt = update(table).where(table.c.chat_id == chat_id).values(reward=new_reward)
                await session.execute(stmt)
                await session.commit()

        # Sleep for one hour
        await asyncio.sleep(const.WAIT_TIME)

    del original_rewards[chat_id]
    del update_tasks[chat_id]


async def manage_task(chat_id: int, item: Item):
    async with AsyncSession(async_engine) as session:
        # If an update task is already running for this chat_id, cancel it
        if chat_id in update_tasks:
            update_tasks[chat_id].cancel()
            del update_tasks[chat_id]

            stmt = update(table).where(table.c.chat_id == chat_id).values(reward=original_rewards[chat_id])
            await session.execute(stmt)
            await session.commit()
        else:
            # Get the original reward value and store it
            stmt = select(table).where(table.c.chat_id == chat_id)
            result = await session.execute(stmt)
            row = result.fetchone()
            if row is not None:
                original_rewards[chat_id] = row[1]

        # Start the update task
        reward_per_hour = item.reward / 24
        task = asyncio.create_task(update_reward_periodically(chat_id, reward_per_hour))
        update_tasks[chat_id] = task


@app.post("/items/")
async def create_item(item: Item):
    await manage_task(item.chat_id, item)
    return {"message": "The update task has been successfully started"}
