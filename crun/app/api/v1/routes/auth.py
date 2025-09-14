import uuid

import aiohttp
from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi_users import BaseUserManager, models
from fastapi_users.authentication import Strategy

from app.config.config import get_settings
from app.core import deps
from app.schemas import UserCreate
from app.models import User


settings = get_settings()
requires_verification = False

logger.debug(f'APP_ID: {settings.LARK_CLIENT_ID}')
logger.debug(f'REDIRECT_URL: {settings.LARK_REDIRECT_URI}')
logger.debug(f'CALLBACK_URL: {settings.FRONTEND_URL}')
logger.debug(f"STATE_URL: {settings.STATIC_URL}")

router = APIRouter(prefix="/api/auth")
source = 'Auth'

async def get_lark_tenant_access_token(code: str):
    """
    获取飞书租户的 access_token
    """
    ...


async def get_user_token(code: str):
    """
    获取飞书用户的 token
    """
    url = 'https://open.larkoffice.com/open-apis/authen/v2/oauth/token'
    content_type = 'application/json; charset=utf-8'
    payload = {}
    payload['grant_type'] = 'authorization_code'
    payload['client_id'] = settings.LARK_CLIENT_ID
    payload['client_secret'] = settings.LARK_SECRET
    payload['code'] = code
    payload['redirect_uri'] = settings.LARK_REDIRECT_URI
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers={'Content-Type': content_type}) as resp:
                response = await resp.json()
    except aiohttp.ClientError as e:
        logger.error(f"Error getting lark token: {e}")
        raise HTTPException(status_code=500, detail="Error getting lark token")
    logger.info(f"Get lark token response: {response}")
    return response


async def get_lark_user_info(user_access_token: str):
    """
    获取飞书用户的信息
    """
    url = 'https://open.larkoffice.com/open-apis/authen/v1/user_info'
    headers = {
        'Authorization': f'Bearer {user_access_token}',
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                response = await resp.json()
    except aiohttp.ClientError as e:
        logger.error(f"Error getting lark user info: {e}")
        raise HTTPException(status_code=500, detail="Error getting lark user info")
    logger.info(f"Get lark user info response: {response}")
    return response


async def get_or_create_user_by_lark(
    user_access_token: str,
    user_manager: BaseUserManager[User, uuid.UUID] = Depends(deps.get_user_manager)
):
    """
    获取或创建飞书用户

    TODO 需要考虑一下, 如果飞书用户的 email 已经存在, 但是又通过飞书登录, 不是同一个人咋办???
    现在的逻辑是直接给覆盖了, 默认注册的用户都老老实实用自己的邮箱注册;
    当前业务场景下还没有开放给用户注册, 所以暂时不考虑;
    如果后期开放注册了, 需要给用户邮箱发送验证码, 确认邮箱是用户自己的
    """
    lark_user_response = await get_lark_user_info(user_access_token)
    if lark_user_response.get("code") != 0:
        raise HTTPException(status_code=400, detail="Get lark user info error")

    lark_user_info = lark_user_response["data"]
    lark_email = lark_user_info["email"]
    avatar_url = lark_user_info.get("avatar_url")
    existing_user = await user_manager.user_db.get_by_email(lark_email)
    if existing_user:
        await user_manager.user_db.update(existing_user, {
            "union_id": lark_user_info.get("user_id", ""),
            "name": lark_user_info.get("name", ""),
            "en_name": lark_user_info.get("en_name", ""),
            "email": lark_email,
            "avatar": existing_user.avatar or avatar_url,
        })
        return existing_user
    else:
        name = lark_user_info.get("name", "")
        en_name = lark_user_info.get("en_name", "")
        user_create = UserCreate(
            name=name,
            en_name=en_name,
            email=lark_email,
            password=f"lark_{uuid.uuid4()}",
            union_id=lark_user_info.get("user_id", ""),
            avatar=avatar_url,
        )
        new_user = await user_manager.create(user_create, safe=True)
        return new_user

async def update_user_token(access_token: str, user_id: str):
    """
    更新飞书用户的 token
    """
    ...

@router.get('/lark_callback', operation_id='larkCallback')
async def lark_callback(
    request: Request,
    code: str,
    user_manager: BaseUserManager[User, uuid.UUID] = Depends(deps.get_user_manager),
    strategy: Strategy[models.UP, models.ID] = Depends(deps.auth_backend.get_strategy),
):
    if not code:
        raise HTTPException(status_code=400, detail="code is empty")

    lark_response = await get_user_token(code)
    if lark_response.get("code") != 0:
        logger.error(lark_response)
        raise HTTPException(status_code=400, detail="Get lark token error")

    logger.info(f"Get lark token success: {lark_response}")
    user_access_token = lark_response["access_token"]
    user = await get_or_create_user_by_lark(user_access_token, user_manager)

    # 为用户创建JWT令牌并登录
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not active",
        )
    if requires_verification and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not verified",
        )

    # 重定向到前端, 并带上 token
    token = await strategy.write_token(user)
    redirect_url = f"{settings.FRONTEND_URL}/login?token={token}"
    return RedirectResponse(url=redirect_url)
