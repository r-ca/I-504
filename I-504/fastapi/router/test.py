import fastapi as APIRouter

router = APIRouter()

# デバッグとか実験とかで使うエンドポイント郡

@router.get("/meta/")
async def meta():
    """メタ情報の取得"""
    pass

@router.post("/add_debug_job/")
async def add_debug_job():
    """デバッグ用ジョブの登録"""
    pass
