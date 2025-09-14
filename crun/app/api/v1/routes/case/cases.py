import re
from io import BytesIO
from typing import Any, List, Optional, Union

import pandas as pd
from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.schemas import (
    TestCase,
    TestCaseCreate,
    TestCaseUpdate,
    TestCaseList,
    BatchTestCaseCreate,
    BatchTestCaseFileValidateError,
    GenericErrorResponse,
    TestCaseFileValidateError,
    ValidateSuccessResponse,
)
from app.crud import cases as crud
from app.crud import case_node as case_node_crud
from app.core import deps


router = APIRouter(prefix="/api/cases")
source = 'TestCase'


@router.get("", response_model=TestCaseList, operation_id='listTestCase')
async def list_data(
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    page: int = 1,
    pageSize: int = 10,
    name: Optional[str] = None,
    index: Optional[str] = None,
    priority: Optional[str] = None,
    automation: Optional[int] = None,
    automated: Optional[int] = None,
    module: Optional[str] = None,
    node_id: Optional[int] = None,
) -> Any:
    f"""
    Retrieve {source}.
    """
    skip = (page - 1) * pageSize
    query_params = {
        "project_id": project_id,
        "name": name,
        "index": index,
        "priority": priority,
        "module": module,
        "node_id": node_id,
    }

    if automation is not None:
        query_params["automation"] = automation
    if automated is not None:
        query_params["automated"] = automated

    datas = await crud.get_multi(db, skip=skip, limit=pageSize, **query_params)
    total = await crud.count(db, **query_params)
    logger.info(datas)
    return {
        "list": datas,
        "total": total,
    }


@router.post("", response_model=TestCase, operation_id='createTestCase')
async def create(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    case_in: TestCaseCreate,
) -> Any:
    f"""
    Create new {source}.
    """
    logger.debug(f"Create {source} with project_id: {project_id}")
    data = await crud.create(db=db, project_id=project_id, obj_in=TestCaseCreate(**case_in.model_dump()))
    return data


@router.patch("/{id}", response_model=TestCase, operation_id='updateTestCase')
async def update(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    data_in: TestCaseUpdate,
) -> Any:
    f"""
    Update an {source}.
    """
    data = await crud.get(db=db, id=id)
    if not data:
        raise HTTPException(status_code=404, detail=f"{source} not found")
    data = await crud.update(db=db, db_obj=data, obj_in=data_in)
    return data


@router.get("/{id}", response_model=TestCase, operation_id='getTestCase')
async def read(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    project_id: int = Depends(deps.current_project_id),
    id: Union[int, str],
) -> Any:
    f"""
    Get {source} by ID.
    """
    if isinstance(id, str):
        data = await crud.get_by_index(db=db, project_id=project_id, index=id)
    else:
        data = await crud.get(db=db, project_id=project_id, id=id)
    if not data:
        raise HTTPException(status_code=404, detail=f"{source} not found")
    return data


@router.delete("/{id}", response_model=TestCase, operation_id='deleteTestCase')
async def delete(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    id: int,
) -> Any:
    f"""
    Delete an {source}.
    """
    data = await crud.get(db=db, id=id)
    if not data:
        raise HTTPException(status_code=404, detail=f"{source} not found")
    data = await crud.remove(db=db, id=id)
    return data


REQUIRED_COLUMNS = {'测试点编号', '测试点名称', '测试目的', '优先级', '预置条件', '测试步骤', '预期结果', '预期结果'}

def filter_valid_sheets(excel_file: pd.ExcelFile) -> tuple[list[str], list[TestCaseFileValidateError]]:
    errors = []
    valid_sheets = []

    for sheet_name in excel_file.sheet_names:
        df: pd.DataFrame  = excel_file.parse(sheet_name)  # pyright: ignore[reportAssignmentType]
        sheet_columns = set(df.columns)

        if not sheet_columns & REQUIRED_COLUMNS:
            continue

        missing = REQUIRED_COLUMNS - sheet_columns
        if missing:
            errors.append(TestCaseFileValidateError(
                sheet=sheet_name,
                type="missing_columns",
                errors=[f"缺少字段：{col}" for col in sorted(missing)]
            ))
            continue

        if df.empty:
            errors.append(TestCaseFileValidateError(
                sheet=sheet_name,
                type="empty_sheet",
                errors=["Sheet 内容为空"]
            ))
            continue

        valid_sheets.append(sheet_name)
    return valid_sheets, errors


@router.post(
    "/validate",
    operation_id="validateTestCaseFile",
    response_model=ValidateSuccessResponse,
    responses={
        HTTP_400_BAD_REQUEST: {
            "model": BatchTestCaseFileValidateError,
            "description": "无有效 sheet, 所有 sheet 均缺少字段或为空"
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": GenericErrorResponse,
            "description": "系统错误, 例如无法读取 Excel"
        },
    },
)
async def validate(file: UploadFile = File(...)) -> ValidateSuccessResponse:
    try:
        contents = await file.read()
        excel_file = pd.ExcelFile(BytesIO(contents))
        valid_sheets, errors = filter_valid_sheets(excel_file)
        if not valid_sheets:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=BatchTestCaseFileValidateError(detail=errors).model_dump()["detail"]
            )

        return ValidateSuccessResponse(
            message="校验通过",
            valid_sheets=valid_sheets,
            warnings=errors
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=GenericErrorResponse(detail=f"系统错误: {str(e)}").model_dump()["detail"]
        )


def clean_index(index: str) -> str:
    """
    去除前后空格，替换多个空格和非法字符为 '-'
    """
    index = index.strip()
    index = re.sub(r"[，。；：、()（）【】《》“”‘’\"\'!@#$%^&*+=<>/?\\|_]", "-", index)
    index = re.sub(r"\s+", "-", index)      # 空格换成 -
    index = re.sub(r"-{2,}", "-", index)    # 合并多个 -
    index = index.strip("-")                # 去除首尾 -
    return index


def is_code_segment(seg: str) -> bool:
    return bool(re.fullmatch(r"[A-Z]{1,3}\d{2,4}", seg)) or bool(re.fullmatch(r"\d{2,4}", seg))


def strip_code_suffix(index: str) -> List[str]:
    index = clean_index(index)  # 清洗字符串
    parts = index.split("-")
    while parts and is_code_segment(parts[-1]):
        parts.pop()
    return parts


@router.post("/import", operation_id='importTestCaseFile')
async def import_cases(
    increment: bool = True,
    file: UploadFile = File(...),
    project_id: int = Depends(deps.current_project_id),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    f"""
    Import test cases from file.
    """
    def get_str_field(val: Any, default: str = "") -> str:
        return val if isinstance(val, str) and not pd.isna(val) else default

    logger.info(f'project_id: {project_id}, increment: {increment}')
    try:
        contents = await file.read()
        excel_file = pd.ExcelFile(BytesIO(contents))
        valid_sheets, errors = filter_valid_sheets(excel_file)
        if errors:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=BatchTestCaseFileValidateError(detail=errors).model_dump()["detail"]
            )

        all_cases: list[TestCaseCreate] = []
        for sheet_name in valid_sheets:
            df: pd.DataFrame  = excel_file.parse(sheet_name)  # pyright: ignore[reportAssignmentType]
            missing = REQUIRED_COLUMNS - set(df.columns)
            if missing:
                raise HTTPException(status_code=400, detail=f"{sheet_name} 缺少字段: {missing}")

            for _, row in df.iterrows():
                index = row.get("测试点编号")
                if not index or pd.isna(index) or str(index).strip() == "":
                    logger.warning(f"{project_id} {sheet_name} 测试点编号为空")
                    continue

                name = row.get("测试点名称")
                if not name or pd.isna(name) or str(name).strip() == "":
                    logger.warning(f"{project_id} {sheet_name} 测试点名称为空")
                    continue

                objective = row.get("测试目的", "")
                if not objective or pd.isna(objective) or str(objective).strip() == "":
                    logger.warning(f"{project_id} {sheet_name} 测试目的为空")
                    continue

                priority = get_str_field(row.get("优先级"))
                setup = get_str_field(row.get("预置条件"))
                step = get_str_field(row.get("测试步骤"))
                expected = get_str_field(row.get("预期结果"))

                # 用户使用 / 分隔节点路径, 如果没有节点, 则使用测试点编号的节点路径
                if row.get('节点'):
                    node_name = (row.get('节点') or '').strip()
                    node_id = await case_node_crud.get_or_create_node_by_path(db, project_id, node_name)
                else:
                    node_path = strip_code_suffix(index)
                    node_id = await case_node_crud.get_or_create_node_by_path(db, project_id, "/".join(node_path))

                # logger.debug(f"{project_id} {sheet_name} {index} {name} {node_id} {priority} {setup} {step} {expected}")
                all_cases.append(BatchTestCaseCreate(
                    index=index.strip(),
                    name=name.strip(),
                    objective=objective.strip(),
                    priority=priority.strip(),
                    setup=setup.strip(),
                    step=step.strip(),
                    expected=expected.strip(),
                    project_id=project_id,
                    node_id=node_id,
                    automated=1 if row.get('已自动化', 'N') == 'Y' else 0,
                    automation=1 if row.get('可自动化', 'N') == 'Y' else 0,
                ))

        if not all_cases:
            raise HTTPException(status_code=400, detail="无有效测试用例，未导入任何数据")

        await crud.create_or_update_cases(db, all_cases)
        return {"message": f"共导入 {len(all_cases)} 条测试用例"}

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")