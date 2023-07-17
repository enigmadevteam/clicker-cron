from fastapi import FastAPI
from sqlalchemy import create_engine, MetaData, Table, select, update
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import insert
import asyncio

app = FastAPI()

DATABASE_URL = "postgresql://postres:postgres@host.docker.internal:5432/postgres"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Assuming you have a table named "table"
table = Table("items", metadata, autoload_with=engine)


class Item(BaseModel):
    chat_id: int
    reward: int


@app.post("/update/")
async def create_item(item: Item):
    reward_per_hour: float = item.reward / 24
    asyncio.create_task(update_reward_periodically(item.chat_id, reward_per_hour))


def update_reward_periodically(chat_id: int, reward_per_hour: float):
    while True:
        with engine.connect() as connection:
            stmt = select(table).where(table.c.chat_id == chat_id)
            result = connection.execute(stmt)
            row = result.fetchone()

            if row is not None:
                new_reward = row['reward'] + reward_per_hour
                update_stmt = update(table).where(table.c.chat_id == chat_id).values(reward=new_reward)
                connection.execute(update_stmt)

        # sleep for one hour
        asyncio.sleep(3600)