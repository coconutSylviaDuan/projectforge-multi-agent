# UI Design Drafts - AI策略系统MVP

Design tone: 专业、数据密集、高效、无营销风格，符合内部业务系统特征
Global layout: 侧边栏主导航 + 顶部用户信息栏 + 主内容区域，侧边栏固定宽度220px，顶部栏高度56px

## Navigation
- 首页 (/)
- 策略列表 (/strategies)
- 回测结果 (/backtest-results)

## 主页（AI对话）
- Route: `/`
- New page: yes

### Layout Wireframe
顶部全局导航栏（侧边栏+顶部栏），主区域居中，宽800px。上方显示LOGO和简短说明，中间一个大型输入框（高度120px），下方预留生成代码预览区域（初始隐藏）。

### Key Components
- 文本输入框（带placeholder：'描述你的策略需求，例如：生成一个双均线策略'）
- 发送按钮（与输入框融为一体，右侧）
- 加载状态指示器（输入框内右侧或覆盖层）
- 代码预览卡片（生成后显示代码摘要和'正在跳转...'）

### Interaction States
- 输入框focus时边框高亮
- 输入时按钮图标变为可点击
- 按回车或点击发送：输入框禁用，显示spinner
- 生成成功：预览区域淡入，显示代码片段，2秒后自动跳转编辑页
- 生成失败：预览区域显示错误红色提示

### Visual Handoff
- 背景色：#F5F7FA，卡片圆角8px，阴影
- 输入框高度120px，字体16px，内边距16px
- 按钮颜色：#1890FF，悬停变深
- 代码块使用等宽字体，背景#282C34，文字#ABB2BF

### Frontend Handoff
- 使用受控组件管理输入框
- 调用POST /api/chat/generate，携带{prompt}
- 成功响应后获取strategy_id和code，使用React Router的useNavigate跳转至/strategy/edit/{id}
- 错误处理使用antd的message或notification

## 策略编辑页
- Route: `/strategy/edit/:id`
- New page: yes

### Layout Wireframe
左右两栏布局，左侧占比60%为代码编辑器，右侧占比40%为Tab面板。顶部操作栏：保存、快速回测、运行回测绩效分析三个按钮并排。右侧Tab默认'多轮对话'，第二个Tab'快速回测结果'。

### Key Components
- Monaco Editor组件（Python语言，行号，折叠）
- Tab切换组件（antd Tabs）
- 多轮对话：消息列表（滚动），输入框+发送按钮
- 快速回测结果：指标摘要（收益率、最大回撤等），放置一张占位图表
- 三个操作按钮：保存（主要）、快速回测（默认）、分析（危险）

### Interaction States
- 加载策略时整个页面遮罩spinner
- 编辑器内容变化时顶部'保存'按钮可点击
- 保存时按钮loading，成功后提示，失败error
- 快速回测时按钮loading，右侧Tab自动切换到结果并显示数据
- 运行分析时按钮loading，完成后跳转到绩效分析页

### Visual Handoff
- 编辑器区域高度全屏减去顶部栏和底部边距
- 顶部按钮组间距8px，保存按钮蓝色，快速回测绿色，分析橙色
- 多轮对话：消息气泡，用户靠右蓝色，AI靠左灰色
- 回测结果：使用Card组件展示指标，图表使用nivo或recharts

### Frontend Handoff
- 路由参数id用于获取策略详情（GET /api/strategies/{id}）
- 编辑器使用@monaco-editor/react，language='python'
- 保存调用POST /api/strategies，传递id、name、description、code
- 快速回测调用POST /api/backtest/quick，传递code和strategy_id
- 分析调用POST /api/backtest/analysis，传递strategy_id和code
- 多轮对话调用POST /api/chat/continue，返回code后更新编辑器内容（不自动保存）

## 策略列表页
- Route: `/strategies`
- New page: yes

### Layout Wireframe
顶部操作栏：左侧标题'我的策略'，右侧新建按钮（跳转首页）。下方为策略列表表格，占满剩余高度。

### Key Components
- 按钮：新建策略（antd Button type='primary'）
- Table组件（antd）：列：名称、描述、创建时间、操作（编辑/删除）
- 删除确认弹窗（antd Modal）

### Interaction States
- 加载数据时表格显示loading或骨架屏
- 空数据时显示Empty状态组件
- 点击编辑跳转到对应编辑页
- 点击删除弹出确认框，确认后从列表移除并刷新

### Visual Handoff
- 表格斑马纹行，操作列图标按钮
- 新建按钮图标为+，位置右上角
- 删除按钮红色图标，编辑蓝色图标
- 时间格式：YYYY-MM-DD HH:mm

### Frontend Handoff
- 页面加载调用GET /api/strategies
- 删除调用DELETE /api/strategies/{id}（需后端实现）
- 点击编辑使用useNavigate/useHistory
- 新建跳转至'/'

## 回测结果列表页
- Route: `/backtest-results`
- New page: yes

### Layout Wireframe
顶部：标题'回测结果'，一个下拉过滤器（全部/快速回测/绩效分析）。下方为结果列表表格。

### Key Components
- Select过滤器（antd）
- Table组件：列：类型（标签）、关联策略名、创建时间、操作（查看详情）

### Interaction States
- 页面加载时获取全部结果
- 切换过滤器重新获取对应类型结果
- 查看详情：若type='full'跳转绩效分析页；若type='quick'使用Drawer或Modal展示摘要

### Visual Handoff
- 类型列使用Tag：quick为蓝色，full为绿色
- 查看详情按钮为链接样式
- 过滤器与标题同行，靠右

### Frontend Handoff
- 调用GET /api/backtest-results?type=xxx
- type='quick'时详情可调用GET /api/backtest-results/{id}展示
- type='full'时跳转到/strategy/performance/{id}

## 策略绩效分析页
- Route: `/strategy/performance/:backtestId`
- New page: yes

### Layout Wireframe
顶部：返回按钮（← 返回）和标题'绩效分析'。主体分上下：上部分为指标卡片行（4个卡片并排），中部分为两个图表（净值曲线和回撤曲线）左右并排，下部分为交易明细表格。

### Key Components
- 返回按钮（antd Button type='link'）
- 指标卡片（antd Card）：总收益率、年化收益率、最大回撤、夏普比率
- 图表组件（recharts LineChart for 净值曲线，AreaChart for 回撤曲线）
- 交易明细Table：日期、操作（买入/卖出）、价格、数量、盈亏

### Interaction States
- 加载中：卡片、图表、表格均显示骨架屏或loading
- 数据加载完成后渲染图表（响应式宽度）
- 返回按钮点击回到上一页或策略列表

### Visual Handoff
- 指标卡片字体加粗，数值使用大号字体，正收益绿色，负收益红色
- 图表使用750px高度，曲线颜色：净值蓝色，回撤红色
- 交易表格默认分页每页20行

### Frontend Handoff
- 调用GET /api/backtest-results/{backtestId}获取result_data
- 指标数据从result_data中提取
- 图表数据需转换格式（x:日期, y:值）
- resize时图表自适应，使用ResizeObserver或组件响应式
