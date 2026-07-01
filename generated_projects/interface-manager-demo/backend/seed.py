from backend.database import get_db

def seed_data(db):
    cursor = db.cursor()
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM interfaces")
    if cursor.fetchone()[0] > 0:
        return
    # 插入接口
    interfaces = [
        ("获取用户列表", "GET", "/api/users", "返回所有用户信息列表", '{"page":"integer","page_size":"integer"}', '{"users":"array"}'),
        ("创建用户", "POST", "/api/users", "创建一个新用户", '{"name":"string","email":"string"}', '{"id":"integer","name":"string"}'),
        ("更新用户", "PUT", "/api/users/{id}", "更新指定用户信息", '{"name":"string"}', '{"success":"boolean"}'),
        ("删除用户", "DELETE", "/api/users/{id}", "删除指定用户", '{}', '{"success":"boolean"}'),
        ("获取订单列表", "GET", "/api/orders", "分页返回订单列表", '{"page":"integer","status":"string"}', '{"orders":"array","total":"integer"}')
    ]
    cursor.executemany(
        "INSERT INTO interfaces (name, method, path, description, request_params, response_schema) VALUES (?, ?, ?, ?, ?, ?)",
        interfaces
    )
    # 获取各接口ID
    cursor.execute("SELECT id FROM interfaces")
    ids = [row[0] for row in cursor.fetchall()]
    # Mock配置（默认未启用）
    mocks = [(iid, 0, 200, '{}', '{}', 0) for iid in ids]
    cursor.executemany(
        "INSERT INTO mock_configs (interface_id, enabled, status_code, headers, body, delay_ms) VALUES (?, ?, ?, ?, ?, ?)",
        mocks
    )
    # 变更记录
    changes = [
        (ids[0], "description", "", "返回所有用户信息列表"),
        (ids[1], "request_params", "{}", '{"name":"string","email":"string"}'),
        (ids[2], "method", "PATCH", "PUT"),
        (ids[3], "response_schema", "{}", '{"success":"boolean"}'),
        (ids[4], "name", "订单列表", "获取订单列表")
    ]
    cursor.executemany(
        "INSERT INTO change_logs (interface_id, field, old_value, new_value) VALUES (?, ?, ?, ?)",
        changes
    )
    # 联调状态（默认未开始）
    statuses = [(iid, "未开始", "") for iid in ids]
    cursor.executemany(
        "INSERT INTO integration_statuses (interface_id, status, notes) VALUES (?, ?, ?)",
        statuses
    )
    db.commit()
