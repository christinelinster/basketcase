from dotenv import load_dotenv
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from mongoDB import db

load_dotenv()

router = APIRouter()

@router.get('')
async def confirm_without_slash():
    return {'success': 'here no slash i know we said hello world but my routes were being weird'}

