from dotenv import load_dotenv
load_dotenv()

from fastapi     import APIRouter, Request
from db.mongo    import db as mongo_db
from db          import postgres

# Router
router = APIRouter()

# Endpoint for public-facing URL (eg. baskets.com/name)
@router.route('/{name}')
async def receive_request(request: Request):
    # save request (raw) to mongo
    # parse request -> save to postgres
    # return 200 ok
    pass
