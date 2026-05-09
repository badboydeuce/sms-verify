from fastapi import APIRouter
import httpx
import os

router = APIRouter()


@router.get("/countries")
async def get_countries():

    token = os.getenv("SMSMAN_TOKEN")

    if not token:
        return {
            "success": False,
            "error": "SMSMAN_TOKEN missing"
        }

    url = "https://api.sms-man.com/control/countries"


    params = {
        "token": token
    }

    try:

        async with httpx.AsyncClient(timeout=30) as client:

            response = await client.get(
                url,
                params=params
            )

        return {
            "status_code": response.status_code,
            "response": response.text
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }