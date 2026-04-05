from fastapi import APIRouter

router = APIRouter(prefix='/health')


@router.get(path='/', include_in_schema=False)
async def health_check():
    return {'status': 'healthy'}
