from pydantic import BaseModel
from typing import Optional, List

class InterfaceResponse(BaseModel):
    id: int
    name: str
    method: str
    path: str
    description: str
    request_params: str
    response_schema: str
    created_at: str
    updated_at: str

class MockConfigRequest(BaseModel):
    enabled: bool = False
    status_code: int = 200
    headers: str = "{}"
    body: str = "{}"
    delay_ms: int = 0

class MockConfigResponse(BaseModel):
    enabled: bool
    status_code: int
    headers: str
    body: str
    delay_ms: int

class IntegrationStatusRequest(BaseModel):
    status: str = "未开始"
    notes: str = ""

class IntegrationStatusResponse(BaseModel):
    status: str
    notes: str
    updated_at: str

class ChangeLogItem(BaseModel):
    id: int
    field: str
    old_value: str
    new_value: str
    changed_at: str

class ChangeLogResponse(BaseModel):
    items: List[ChangeLogItem]

class PaginatedInterfaces(BaseModel):
    total: int
    items: List[InterfaceResponse]
    page: int
    page_size: int
