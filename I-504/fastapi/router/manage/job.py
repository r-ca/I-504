from fastapi import APIRouter

router = APIRouter()

@router.get("/register/")
async def register():
    """ジョブの登録"""
    pass

@router.get("/unregister/")
async def unregister():
    """ジョブの削除"""
    pass

@router.get("/update/")
async def update():
    """ジョブの更新"""
    pass

