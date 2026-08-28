from dotenv import load_dotenv
load_dotenv()

from contextlib  import asynccontextmanager
from fastapi     import APIRouter
from db.mongo    import db as mongo_db
from db          import postgres


router = APIRouter(prefix='/api')

@router.post('/baskets')
async def create_basket():
    async with postgres.pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO baskets (name) VALUES ($1)",
            'test name'
        )
    pass

@router.get('/baskets')
async def get_baskets():
    return 'hello'
    # landing page for user, view all baskets 
    # -> frontend sends tokens from localstorage
    pass

@router.get('/baskets/{name}')
async def get_basket(name: str):
    pass
