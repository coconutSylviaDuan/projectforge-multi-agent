from dataclasses import dataclass
from typing import Optional

@dataclass
class Interface:
    id: Optional[int] = None
    name: str = ""
    method: str = "GET"
    path: str = ""
    description: str = ""
    request_params: str = "{}"
    response_schema: str = "{}"
    created_at: str = ""
    updated_at: str = ""

@dataclass
class MockConfig:
    id: Optional[int] = None
    interface_id: int = 0
    enabled: bool = False
    status_code: int = 200
    headers: str = "{}"
    body: str = "{}"
    delay_ms: int = 0
    updated_at: str = ""

@dataclass
class ChangeLog:
    id: Optional[int] = None
    interface_id: int = 0
    field: str = ""
    old_value: str = ""
    new_value: str = ""
    changed_at: str = ""

@dataclass
class IntegrationStatus:
    id: Optional[int] = None
    interface_id: int = 0
    status: str = "未开始"
    notes: str = ""
    updated_at: str = ""
