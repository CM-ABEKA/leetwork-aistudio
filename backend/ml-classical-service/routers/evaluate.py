from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def evaluate():
    return {
        "message": "Classical ML evaluation stub",
        "status": "not_implemented",
    }
