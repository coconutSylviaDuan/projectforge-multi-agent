# 接口管理平台 - 集成运行说明

## 环境要求
- Python 3.8+
- pip

## 安装依赖
```bash
pip install -r backend/requirements.txt
```

## 启动后端服务
```bash
uvicorn backend.main:app --reload
```
服务将在 http://localhost:8000 启动。

## 访问前端
浏览器直接打开 [http://localhost:8000](http://localhost:8000) 即可进入接口管理平台。
前端使用 Hash 路由，无需额外构建步骤。

## 验收清单
| 编号 | 验收项 | 预期结果 |
|------|--------|----------|
| 1 | 接口目录页 | 显示分页列表，支持按方法筛选。默认展示5个示例接口。 |
| 2 | 接口详情页 | 点击接口名称进入详情，展示基本信息（方法、路径、描述、参数等）。 |
| 3 | Mock配置页 | 可在详情页切换至Mock配置标签，查看/编辑当前Mock配置（启用开关、状态码、响应头/体、延迟），保存后显示成功提示并刷新。 |
| 4 | 变更记录页 | 切换至变更记录标签，按时间倒序显示变更历史。 |
| 5 | 联调状态页 | 切换至联调状态标签，查看当前状态（未开始/联调中/已完成），可更新状态和备注，保存后状态标签颜色变化。 |
| 6 | 错误处理 | 表单验证（如JSON格式错误）时显示红色提示；网络错误显示alert。 |

## 快速演示脚本
1. 启动后端。
2. 打开浏览器访问 http://localhost:8000。
3. 查看接口列表，点击第一个接口进入详情。
4. 依次切换Mock配置、变更记录、联调状态标签进行操作验证。

## 项目结构说明
```
backend/
├── main.py          # FastAPI 应用入口
├── database.py      # SQLite 数据库初始化和连接
├── models.py        # 数据模型定义
├── schemas.py       # Pydantic 请求/响应模型
├── routes.py        # REST API 路由
├── seed.py          # 种子数据脚本
├── index.html       # 前端主页面
├── app.js           # 前端 JavaScript
├── style.css        # 自定义样式
└── requirements.txt # Python 依赖
```

## 备注
- 预置了5个示例接口，方便演示。
- 所有数据存储在 SQLite 数据库文件 `backend/interface_manager.db` 中，重启不会丢失（除非删除文件）。