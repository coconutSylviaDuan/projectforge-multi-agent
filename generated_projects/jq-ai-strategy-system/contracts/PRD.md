# AI策略系统产品需求文档

Version: v0.1

## Background
量化交易领域，用户通常需要编写和回测策略代码，但学习曲线陡峭。通过AI自然语言对话生成策略代码，并内嵌编辑器与回测功能，可大幅降低门槛。本项目为MVP版本，聚焦核心功能闭环，确保本地可运行演示。

## Goals
- 用户可通过自然语言描述快速生成聚宽格式策略代码
- 提供代码编辑、AI多轮对话修改、快速回测验证的交互环境
- 支持完整回测绩效分析并绑定策略
- 提供策略和回测结果的管理列表

## User Roles
- 普通用户（已登录）

## Business Modules
- AI对话生成模块
- 策略编辑与保存模块
- 回测执行模块（快速/完整）
- 绩效分析展示模块
- 策略与回测结果管理模块
- 用户认证模块

## Page Requirements
### 主页（AI对话）
- Route: `/`
- Purpose: 用户输入需求，AI生成策略代码并跳转编辑页
- Primary actions: 输入策略需求文本, 点击回车调用AI生成代码, 显示生成结果, 跳转到策略编辑页

### 策略编辑页
- Route: `/strategy/edit/:id`
- Purpose: 编辑策略代码，继续AI对话修改，执行快速回测或完整回测绩效分析
- Primary actions: 显示代码编辑器（左侧）, 右侧Tab：多轮对话，快速回测结果, 点击保存按钮: 保存策略到列表, 点击快速回测: 运行快速回测并显示结果, 点击运行回测绩效分析: 跳转到绩效分析页

### 策略列表页
- Route: `/strategies`
- Purpose: 查看当前用户所有策略，支持新建和删除
- Primary actions: 展示策略列表, 点击策略进入编辑页, 新建策略（跳转主页）, 删除策略

### 回测结果列表页
- Route: `/backtest-results`
- Purpose: 查看所有回测结果（包括快速回测和绩效分析）
- Primary actions: 展示回测结果列表, 点击查看详细数据, 筛选按类型查看

### 策略绩效分析页
- Route: `/strategy/performance/:backtestId`
- Purpose: 展示完整回测绩效分析的详细结果
- Primary actions: 展示绩效指标图表, 展示交易明细, 返回策略列表或编辑页

## Interface Management

### 用户认证 / 用户注册
- Method: `POST`
- Path: `/api/auth/register`
- Description: 注册新用户
- Frontend usage: 注册页面调用，创建账户
- Backend notes: 密码使用bcrypt哈希存储，返回JWT token（可后续扩展）
- Request fields:
  - `username` (string): 用户名
  - `password` (string): 密码
- Response fields:
  - `id` (integer): 用户ID
  - `username` (string): 用户名

### 用户认证 / 用户登录
- Method: `POST`
- Path: `/api/auth/login`
- Description: 登录获取token
- Frontend usage: 登录页面调用，保存token到本地存储
- Backend notes: 验证密码并签发JWT，过期时间30分钟
- Request fields:
  - `username` (string): 用户名
  - `password` (string): 密码
- Response fields:
  - `access_token` (string): JWT access token
  - `token_type` (string): bearer

### AI对话 / 生成策略代码
- Method: `POST`
- Path: `/api/chat/generate`
- Description: 根据用户输入使用大模型生成策略代码
- Frontend usage: 主页输入框提交后调用，成功后跳转编辑页
- Backend notes: 本地模拟返回固定模板代码，或调用大模型API。若使用模拟，返回预设双均线策略。
- Request fields:
  - `prompt` (string): 用户需求文本
  - `history` (array): 多轮对话历史（可选）
- Response fields:
  - `code` (string): 生成的策略代码
  - `strategy_id` (integer): 新创建的策略ID

### 策略管理 / 保存策略
- Method: `POST`
- Path: `/api/strategies`
- Description: 创建或更新策略
- Frontend usage: 编辑页点击保存按钮调用，成功后提示并更新列表
- Backend notes: 支持新建和更新，更新时根据id查找并覆盖code等信息
- Request fields:
  - `id` (integer): 策略ID，更新时提供; 新建时不传
  - `name` (string): 策略名称
  - `description` (string): 策略描述
  - `code` (string): 策略代码
- Response fields:
  - `id` (integer): 策略ID
  - `created_at` (string): 创建时间

### 策略管理 / 获取策略列表
- Method: `GET`
- Path: `/api/strategies`
- Description: 获取当前用户的所有策略
- Frontend usage: 策略列表页加载时调用
- Backend notes: 根据当前登录用户ID查询
- Request fields:
- Response fields:
  - `strategies` (array): 策略对象数组，包含id,name,description,created_at

### 策略管理 / 获取策略详情
- Method: `GET`
- Path: `/api/strategies/{id}`
- Description: 获取单个策略的详细信息（含代码）
- Frontend usage: 编辑页打开时加载已有策略
- Backend notes: 验证策略属于当前用户
- Request fields:
- Response fields:
  - `id` (integer): 
  - `name` (string): 
  - `description` (string): 
  - `code` (string): 
  - `created_at` (string): 
  - `bound_backtest_id` (integer): 

### 回测 / 快速回测
- Method: `POST`
- Path: `/api/backtest/quick`
- Description: 执行快速回测并返回结果
- Frontend usage: 编辑页点击快速回测按钮调用，结果显示在右侧tab
- Backend notes: 本地模拟回测引擎，返回预设的模拟结果。结果保存到BacktestResult表，type为quick。
- Request fields:
  - `code` (string): 策略代码
  - `strategy_id` (integer): 关联策略ID（可为null）
- Response fields:
  - `backtest_id` (integer): 回测结果ID
  - `result` (object): 回测结果数据（模拟）

### 回测 / 运行回测绩效分析
- Method: `POST`
- Path: `/api/backtest/analysis`
- Description: 执行完整回测绩效分析，结果绑定到策略
- Frontend usage: 编辑页点击运行回测绩效分析按钮调用，成功后跳转到绩效分析页
- Backend notes: 执行更详细的回测（模拟），保存结果至BacktestResult（type=full），并更新strategy.bound_backtest_id。
- Request fields:
  - `strategy_id` (integer): 策略ID（必须）
  - `code` (string): 策略代码
- Response fields:
  - `backtest_id` (integer): 回测结果ID
  - `redirect_url` (string): 绩效分析页URL

### 回测结果 / 获取回测结果列表
- Method: `GET`
- Path: `/api/backtest-results`
- Description: 获取当前用户的所有回测结果（支持type过滤）
- Frontend usage: 回测结果列表页加载
- Backend notes: 根据user_id查询，支持按type过滤
- Request fields:
  - `type` (string): 可选过滤：quick/full
- Response fields:
  - `results` (array): 回测结果对象数组

### 回测结果 / 获取绩效分析详情
- Method: `GET`
- Path: `/api/backtest-results/{id}`
- Description: 获取单个回测结果的详细数据
- Frontend usage: 绩效分析页加载详情
- Backend notes: 返回结果数据，包括绩效指标、交易记录等
- Request fields:
- Response fields:
  - `id` (integer): 
  - `type` (string): 
  - `result_data` (object): 
  - `strategy_id` (integer): 

### AI对话 / 多轮对话
- Method: `POST`
- Path: `/api/chat/continue`
- Description: 在编辑页继续AI对话，修改策略代码
- Frontend usage: 编辑页右侧对话Tab，发送消息后更新代码编辑器内容
- Backend notes: 模拟返回或调用大模型，更新策略代码（注意不自动保存）
- Request fields:
  - `strategy_id` (integer): 当前策略ID
  - `message` (string): 用户新的需求或修改指令
  - `history` (array): 对话历史
- Response fields:
  - `code` (string): 更新后的策略代码
  - `reply` (string): AI回复文本

## Data Requirements
- 用户表：存储用户认证信息
- 策略表：存储策略元数据和代码，外键关联用户
- 回测结果表：存储回测类型、结果数据，外键关联策略（可空）和用户
- 所有表使用SQLite存储
- 回测结果数据以JSON格式存储，便于扩展

## Acceptance Criteria
- 用户注册登录后，主页显示AI对话输入框
- 输入“生成一个双均线策略”，回车后显示生成的代码并跳转编辑页（代码预填）
- 编辑页左侧显示代码编辑器，右侧默认显示多轮对话tab，可切换至快速回测结果tab
- 点击保存按钮，策略保存至列表，提示成功
- 点击快速回测，右侧tab显示模拟回测结果（含净值曲线等图表占位）
- 点击运行回测绩效分析，跳转至绩效分析页，显示详细绩效指标（收益率、最大回撤、夏普等）
- 策略列表页显示所有已保存策略，点击可编辑
- 回测结果列表页显示所有回测记录，可按类型筛选
- 所有操作需登录认证，未登录跳转登录页

## Frontend Handoff
- 使用React/Vite + TypeScript
- 页面路由：首页(/)、策略编辑页(/strategy/edit/:id)、策略列表(/strategies)、回测结果(/backtest-results)、绩效分析(/strategy/performance/:backtestId)、登录(/login)、注册(/register)
- AI对话输入框在主页，回车后调用POST /api/chat/generate
- 代码编辑器可使用CodeMirror或Monaco Editor，语言设为python
- 多轮对话tab：消息列表+输入框，调用POST /api/chat/continue
- 快速回测结果tab：展示表格/图表数据
- 绩效分析页：展示多个指标卡片、图表（如回撤曲线、每月收益热力图）
- 认证：登录后保存token到localStorage，axios拦截器添加Authorization头
- 本地启动mock数据时，可先不依赖后端，使用静态json数据

## Backend Handoff
- 使用FastAPI, SQLite (SQLAlchemy ORM)
- 实现JWT认证中间件，所有接口（除注册登录）需验证token
- 数据库模型：User, Strategy, BacktestResult
- 回测引擎：提供快速回测和完整回测的模拟实现，结果以JSON返回
- AI对话：可选集成OpenAI API或使用本地模拟返回（开发阶段建议模拟）
- 接口文档建议使用FastAPI自动生成Swagger
- 注意CORS配置，允许前端localhost:5173访问
- 提供初始化数据库的脚本
