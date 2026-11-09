import asyncio
from app.database import AsyncSessionLocal, Base, engine
from app.seed import seed_initial_data


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed_initial_data(db)
    print("CNMOVI_DB_INITIALIZED_AND_SEEDED_OK")


if __name__ == "__main__":
    asyncio.run(main())
