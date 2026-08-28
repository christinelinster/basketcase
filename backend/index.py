import os
import asyncio
from hypercorn.asyncio import serve
from contextlib import asynccontextmanager
from hypercorn.config import Config
import redis.asyncio as redis
from dotenv import load_dotenv
import logging

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware


# Load environment variables
load_dotenv()

# Your project modules
from lib.pg_persistence import PgPersistence
from lib.startup import startup

from lib.rateLimit import rate_limit_handler
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from lib.catch_error import catch_error
from lib.csrfTokenMaker import validate_csrf_token, get_or_create_csrf_token
from lib.db_query import Database
from mongoDB import connect_to_mongodb
from lib.sessionControl import RedisSessionMiddleware
from routes.api import router


db = Database()

TRUST_PROXY = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("USE_DB") == "true":
        await startup()
    
    else:
        print("DB Disabled: change at env")
    yield

app = FastAPI(lifespan=lifespan)
app.add_exception_handler(Exception, catch_error)

PORT = int(os.getenv("PORT", 3000))

HOST = "0.0.0.0"

redis_client = None

if os.getenv("USE_REDIS", "").lower() == "true":

    redis_client = redis.from_url(
        os.getenv("REDIS_URL")
    )

else:
    print("Redis Disabled: change env")


app.add_middleware(
    RedisSessionMiddleware,
    redis_client=redis_client
)

@app.middleware("http")
async def force_https(request: Request, call_next):

    if (
        os.getenv("NODE_ENV") == "production"
        and request.headers.get("X-Forwarded-Proto") != "https"
    ):
        url = request.url.replace(scheme="https")

        return RedirectResponse(
            url=str(url),
            status_code=301
        )

    return await call_next(request)

"Webhook for stripe. need to make py, its JS"
"""
app.post('/webhook', express.raw({type: 'application/json'}), async (req, res) => {
    let event;

    // Verify the webhook signature to ensure it's from Stripe
    try {
      event = stripe.webhooks.constructEvent(req.body, req.headers['stripe-signature'], endpointSecret);
    } catch (err) {
      console.error('Webhook signature verification failed:', err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }
  
    // Handle only the 'checkout.session.completed' event
    if (event.type === 'checkout.session.completed') {
      const session = event.data.object;
        const paymentStatus = session.payment_status; // check if still using session?
        const stripeId = session.id;
        const payment_intent = session.payment_intent;
        const amount_paid = (session.amount_total / 100).toFixed(2);

        if(paymentStatus === 'paid') {
            let orderDetails = {
                id: stripeId,
                payment_intent,
                userId: session.metadata.userId,
                status: paymentStatus,
                amount_paid
            }
	
        try {
            let orderExists = await res.locals.store.stripeOrderExists(stripeId);
            if(!orderExists) {
                await res.locals.store.createOrderUsingStripeId(paymentStatus, stripeId, payment_intent)
            } else {
                await res.locals.store.updatePaymentStatus(paymentStatus, stripeId, payment_intent);
            }

        } catch(err) {
                console.error(' Error while processing order');  
                orderDetails.error = err;
            }
	await nodemailer(orderDetails)
		.catch(err => console.log('Nodemailer failed: ', err))
		}	
       // let orderUpdated = await res.locals.updatePaymentStatus(session.payment_status, session.metadata.order_id)
 
    }
    res.json({received: true});
  }); 
"""

#cmon guys, trust me... it'll be fine
trustedOrigins = [
    'https://danluna.com',
    'https://www.danluna.com',
    'https://capstone.danluna.com',
];

app.add_middleware(
    CORSMiddleware,
    allow_origins=trustedOrigins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(
    key_func=get_remote_address
)

app.add_exception_handler(
    RateLimitExceeded,
    rate_limit_handler
)




@app.get("/api/csrf-token")#keep?
async def csrf_token(request: Request):

    return {
        "token": get_or_create_csrf_token(request)
    }

"make sure CSP is in nginx for scripts that are external"

@app.middleware("http")
async def block_wp_scans(request: Request, call_next):

    path = request.url.path.lower()

    if "wp-admin" in path or "wordpress" in path:

        print(f"Blocked WP scan attempt: {path}")

        return Response(
            status_code=404
        )

    return await call_next(request)

app.include_router(
    router,
    prefix="/api" #just needed somethign for testing, change later
)

@app.get("/debug-routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "methods": list(route.methods) if hasattr(route, "methods") else None,
            "name": route.name
        })
    return {"routes": routes}

logger = logging.getLogger(__name__)


async def main():
    config = Config()
    config.bind = [f"{HOST}:{PORT}"]

    print(f"Listening in {HOST} on port {PORT}")

    await serve(app, config)


if __name__ == "__main__":
    asyncio.run(main())