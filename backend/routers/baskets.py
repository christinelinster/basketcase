from dotenv import load_dotenv
load_dotenv()

import re

from fastapi             import APIRouter
from fastapi.responses   import JSONResponse
from asyncpg.exceptions  import UniqueViolationError
from db.mongo            import db as mongo_db
from db                  import postgres


router = APIRouter(prefix='/api')

NAME_PATTERN = re.compile(r'^[A-Za-z0-9]{1,50}$')

@router.post('/baskets')
async def create_basket(name: str):
    if not NAME_PATTERN.fullmatch(name):
        return JSONResponse(status_code=400, content={"error": "Name must consist of 1-50 alphanumeric characters only."})

    if name.casefold() == 'baskets':
        return JSONResponse(status_code=400, content={"error": "'baskets' is reserved."})

    try:
        async with postgres.pool.acquire() as connection:
            record = await connection.fetchrow(
                """
                INSERT INTO baskets (name)
                VALUES ($1)
                RETURNING id, name, token, capacity, expires_at
                """,
                name,
            )
    except UniqueViolationError as exc:
        if exc.constraint_name == 'baskets_name_key':
            return JSONResponse(status_code=409, content={"error": f"Failed to create basket - {name} already exists."})
        return JSONResponse(status_code=500, content={"error": "Internal server error."})
    except Exception:
        return JSONResponse(status_code=500, content={"error": "Internal server error."})

    return {"data": dict(record)}

@router.get('/baskets')
async def get_baskets():
    return 'hello'
    # landing page for user, view all baskets 
    # -> frontend sends tokens from localstorage
    pass

@router.get('/baskets/{name}')
async def get_basket(name: str):
    pass
