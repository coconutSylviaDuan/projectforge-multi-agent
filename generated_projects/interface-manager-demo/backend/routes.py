from fastapi import APIRouter, HTTPException, Query
from backend.database import get_db
from backend.schemas import (
    InterfaceResponse,
    MockConfigRequest,
    MockConfigResponse,
    IntegrationStatusRequest,
    IntegrationStatusResponse,
    ChangeLogResponse,
    ChangeLogItem,
    PaginatedInterfaces
)

router = APIRouter()

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

@router.get("/interfaces", response_model=PaginatedInterfaces)
def list_interfaces(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), method: str = Query(None)):
    db = get_db()
    cursor = db.cursor()
    where = ""
    params = []
    if method:
        where = "WHERE method = ?"
        params.append(method.upper())
    count_sql = f"SELECT COUNT(*) FROM interfaces {where}"
    cursor.execute(count_sql, params)
    total = cursor.fetchone()[0]
    offset = (page - 1) * page_size
    data_sql = f"SELECT * FROM interfaces {where} ORDER BY updated_at DESC LIMIT ? OFFSET ?"
    cursor.execute(data_sql, params + [page_size, offset])
    rows = cursor.fetchall()
    db.close()
    items = [InterfaceResponse(**row_to_dict(r)) for r in rows]
    return PaginatedInterfaces(total=total, items=items, page=page, page_size=page_size)

@router.get("/interfaces/{interface_id}", response_model=InterfaceResponse)
def get_interface(interface_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM interfaces WHERE id = ?", (interface_id,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="接口不存在")
    return InterfaceResponse(**row_to_dict(row))

@router.get("/interfaces/{interface_id}/mock", response_model=MockConfigResponse)
def get_mock_config(interface_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM mock_configs WHERE interface_id = ?", (interface_id,))
    row = cursor.fetchone()
    db.close()
    if row:
        return MockConfigResponse(**row_to_dict(row))
    else:
        # 返回默认配置
        return MockConfigResponse(enabled=False, status_code=200, headers="{}", body="{}", delay_ms=0)

@router.put("/interfaces/{interface_id}/mock", response_model=dict)
def update_mock_config(interface_id: int, config: MockConfigRequest):
    db = get_db()
    cursor = db.cursor()
    # 检查接口是否存在
    cursor.execute("SELECT id FROM interfaces WHERE id = ?", (interface_id,))
    if not cursor.fetchone():
        db.close()
        raise HTTPException(status_code=404, detail="接口不存在")
    # upsert
    cursor.execute(
        """INSERT INTO mock_configs (interface_id, enabled, status_code, headers, body, delay_ms, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
           ON CONFLICT(interface_id) DO UPDATE SET
               enabled = excluded.enabled,
               status_code = excluded.status_code,
               headers = excluded.headers,
               body = excluded.body,
               delay_ms = excluded.delay_ms,
               updated_at = datetime('now')""",
        (interface_id, int(config.enabled), config.status_code, config.headers, config.body, config.delay_ms)
    )
    db.commit()
    db.close()
    return {"success": True}

@router.get("/interfaces/{interface_id}/changes", response_model=ChangeLogResponse)
def get_change_logs(interface_id: int, limit: int = Query(20, ge=1, le=100)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, field, old_value, new_value, changed_at FROM change_logs WHERE interface_id = ? ORDER BY changed_at DESC LIMIT ?",
        (interface_id, limit)
    )
    rows = cursor.fetchall()
    db.close()
    items = [ChangeLogItem(**row_to_dict(r)) for r in rows]
    return ChangeLogResponse(items=items)

@router.get("/interfaces/{interface_id}/integration", response_model=IntegrationStatusResponse)
def get_integration_status(interface_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM integration_statuses WHERE interface_id = ?", (interface_id,))
    row = cursor.fetchone()
    db.close()
    if row:
        return IntegrationStatusResponse(**row_to_dict(row))
    else:
        return IntegrationStatusResponse(status="未开始", notes="", updated_at="")

@router.put("/interfaces/{interface_id}/integration", response_model=dict)
def update_integration_status(interface_id: int, status_req: IntegrationStatusRequest):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM interfaces WHERE id = ?", (interface_id,))
    if not cursor.fetchone():
        db.close()
        raise HTTPException(status_code=404, detail="接口不存在")
    cursor.execute(
        """INSERT INTO integration_statuses (interface_id, status, notes, updated_at)
           VALUES (?, ?, ?, datetime('now'))
           ON CONFLICT(interface_id) DO UPDATE SET
               status = excluded.status,
               notes = excluded.notes,
               updated_at = datetime('now')""",
        (interface_id, status_req.status, status_req.notes)
    )
    db.commit()
    db.close()
    return {"success": True}

# 注意：mock_configs表需要唯一约束确保upsert工作，但为了简单，我们使用INSERT OR REPLACE策略；实际已经使用ON CONFLICT。需要在数据库约束上添加唯一索引。在init_db中补充。
# 为了兼容，我们在database.py中创建唯一索引。
