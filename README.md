# 衡远联运 · 中转网络韧性推演

面向衡远18人联运规划组的模拟网络图册。逐边保存容量与时长，锁定源汇和停用边快照，对比Edmonds–Karp最大流/最小割证据与独立Dijkstra最短时长。平行边、反向边均保留各自ID，不把最大流分配解释为沿最短路发运。

## 场景与工作日

团队过去用静态箭头图讨论故障绕行，边容量没有入账、割集与最短路被混用、停边影响没有量化。上游是模拟枢纽/有向弧清单；系统替代节点边核查、容量推演和人工复核；下游是规划讨论与站内CSV归档，不连接真实调度服务。

09:00分析员登录；09:03核对 hengyuan_transfer_202611.json 的10枢纽、22有向边；09:08逐条检查e01/e19平行边、e04/e20反向边的独立ID；09:12锁定S→T并停用e13；09:15后台worker计算同一快照的基线与停用状态；09:20核对最大流与割容量；09:24查看逐边正反残量和节点守恒；09:28切换独立最短路径，核对时长与可达性；09:32记录容量/路径解释边界；09:36管理员批准最新接受复核；09:40下载两状态逐边CSV。

|角色|页面|权限和典型动作|
|---|---|---|
|admin|全部|读写、运行、人工复核及批准归档|
|analyst|节点/边/停用/流量/复核|创建和排队推演、提交意见；归档后端403|
|viewer|全部只读和报告下载|核对守恒、割集与路径；可下载有效或已失效版本（失效版带原因）；写操作后端403|

## 启动

```sh
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
```

前端 http://localhost:18229 ，后端文档 http://localhost:19229/docs ，MySQL映射17729。账号：admin@hengyuan.demo、analyst@hengyuan.demo、viewer@hengyuan.demo；密码均为 `Network2026!`。开发JWT密钥应在部署前替换。

恰好frontend/backend/worker/db/redis五服务，全部healthcheck。backend等待MySQL/Redis健康，worker再等待backend完成种子，frontend等待backend。数据库、Redis AOF和worker心跳分别命名卷。结束演示：`docker compose down -v --remove-orphans`，会清除本项目演示数据。

SEED_DEMO=true初次建表并幂等填充固定ID/自然键，不重复新增、不覆盖用户修改。种子10节点22弧，容量箱/小时、时长分钟，含平行和反向边；预置无停用、停e13、源站出弧全停三方案，以及真实完成的停e13结果、接受复核与绑定该意见的第1版有效报告。节点坐标仅作布局，无真实地理含义。所有数据模拟。

## 六实体与页面

NetworkDataset保存节点和来源；TransferArc单独持久化每条ID/端点/非负整数容量/非负时长，唯一键为(dataset_id,arc_id)，允许端点重复或反向；OutageScenario在建立时冻结全部边快照，记录源汇与停用ID；NetworkRun经Redis独立worker计算并保存证据；ResilienceReview保存人工判断；Report仅在最新意见accepted后由admin归档，绑定该次接受意见、当时推演结果与快照校验码，每次归档为run内递增版本。

归档版本与失效：最新复核意见变为needs_attention时，该run所有有效版本立即失效，记录失效时间、操作者、失效原因和触发意见ID；新接受意见归档时旧有效版本标记为已被取代。失效版本的CSV仍可下载，但响应头X-Report-Status: invalid并带URL编码的X-Report-Reason，CSV首行report_status也写出原因；旧版内容（接受意见原文、证据快照、校验码）保留，不覆盖。同一接受意见重复归档返回原版本，不新增版本；不同接受意见重新接受后归档为新版本，版本号只增不减。归档与复核都以run行锁串行，提交后再做一次有效性对账，保证并发下每个run至多一个有效版本；`/reports/runs/{run_id}/versions`返回各版内容、绑定意见与有效性，Reviews页展示版本列表并标注失效原因。

六业务页：韧性总览、网络与节点、容量与时长、停用方案、流量与绕行、韧性复核（含操作留痕）。平行/反向边曲线错开，逐边台账和残量表保留完整ID；近竖直平行/反向标签向两侧外置，避免中点重叠。图中最大流视图与独立最短路径视图分开，基线/停用两组数值明确；手机图在局部横向容器滚动，页面本身不横溢。

新增边不会改变旧推演；如需纳入比较，必须新建方案冻结新快照，保证前后比较来自同一份容量和时长。

## 两个算法与证据

### Edmonds–Karp最大流/最小割

每条原始边创建独立的正/反残量对，并用全局索引相互引用；不以(u,v)字典覆盖平行或反向边。BFS寻找正残量增广路径，按瓶颈整数增广；走某原始边的反残量只取消该边已有流量，不与另一条反向原始边混淆。

增广终止后，从源按正残量可达节点得到源侧集合，汇侧为其补集；跨源侧→汇侧的有效容量之和为割容量。停用边有效容量0，但原容量保留。对每原始边输出flow、effective_capacity、residual_forward=capacity−flow、residual_reverse=flow和停用状态。

输出逐边0≤flow≤有效容量、每节点流入/流出/余额，源余额=最大流、汇余额=负最大流、其余0；同时验证maxflow=mincut和汇不在残量源侧。检查失败则运行失败，不输出伪证据。增广记录保留边ID与正/反方向，UI预览前10次，结果保留全部。

### 独立Dijkstra最短时长

只使用启用且容量>0的有向边，以非负travel_minutes为权重。平行边按ID独立参与；零容量捷径不进入图。正容量零时长路径合法返回minutes=0.0且reachable=true；不可达明确返回minutes=null、reachable=false与空路径，不用0假扮不可达。

输出节点路径、边ID路径和总分钟。最大流是容量问题，最短路是独立时长问题；没有求最小费用流，也不声称全部最大流沿这条路径分配。基线与停用用同一冻结快照，分别输出这两类结果及流量减少、时长变化/可达性变化。

### 输入与失败态

节点2—30、边最多200，ID唯一；源汇不同且都存在；容量严格非负整数（上限100万），时长有限非负（上限100万分钟），零时长允许。未知边停用、未知端点、重复ID、分数容量、负值、非有限值都后端拒绝。没有边也能真实得到最大流0/割0与不可达，而非报伪路径。算法确定性；相同快照与源汇/停用配置产生同一结果，附SHA256校验码。

## 报告版本与失效规则

- 归档请求必须携带run与review；后端校验该review是run当前最新的接受意见，并复制其原文、作者、时间，以及推演的两状态证据快照和SHA256校验码。
- needs_attention意见提交即失效该run的有效报告，无需等待新归档；CSV下载以`X-Report-Status`/`X-Report-Reason`与首行说明原因，不做静默降级。
- 同一review_id重复归档幂等返回原版本（幂等键review_id唯一）；review_id留空时绑定当前最新接受意见以兼容旧客户端。版本号在同run内唯一且连续递增。
- 失效只改状态与失效元数据，原快照与接受意见保留；重新接受后归档新增版本，旧版本仍可按ID下载和核对。
- 旧部署需执行backend/migrations/002-report-versioning.sql；重复run_id唯一索引应被移除，改为(run_id,version)唯一。

## 技术与开发

|部分|技术|
|---|---|
|前端|Vue3.5、TypeScript5.7、Vite6、Nginx1.28|
|后端|Python3.11、FastAPI、SQLAlchemy、PyJWT，图算法为标准库实现|
|持久化|MySQL8.4，整数容量、DOUBLE时长、JSON冻结快照/证据|
|后台|Redis7.4 AOF、独立Python worker与心跳|

frontend/src含api/stores/types/components/common/hooks/pages/router/utils/constants；backend/src含routes/controllers/services/models/schemas/middlewares/utils/constants/config；backend/scripts为seed，backend/migrations说明初次模型建表。测试、截图、日志、TESTING/verification均在批次test-artifacts/gb-2310，不混入源码。

本地后端安装requirements.txt，配置DATABASE_URL/REDIS_URL/JWT_SECRET，在backend执行`uvicorn src.main:app --reload`，另开`python -m src.worker`。前端`npm ci && npm run dev`，Vite已将/api代理到19229并去前缀，Docker Nginx同样处理。Vue已验证锁文件只JSON修改根名/根package名，依赖节点不变，Docker使用npm ci。

环境：COMPOSE_PROJECT_NAME=transfer-resilience；FRONTEND_PORT=18229；BACKEND_PORT=19229；DB_PORT=17729；JWT_SECRET；SEED_DEMO。DATABASE_URL/REDIS_URL由Compose传入；`.env`忽略，`.env.example`可复制。

共享Role/RunStatus/Decision在backend/src/constants/enums.py和frontend/src/constants/enums.ts；controllers/auth.py执行角色规则，services/runs.py/worker.py更新状态，Status组件消费；复核decision由schemas/review.py验证、Reviews页消费。基线/outage与证据检查标签在前端constants，PhaseCompare/Results/ConservationTable消费后端同名字段。

## 适用边界

静态容量网络只量化模拟上界与单次停边影响，没有时间展开、排队、发运批次或动态调度。最短路与最大流分配分别计算，不是联合优化。JSON表单导入，无CSV解析器。单worker启动恢复queued/running，无分布式租约；初次SQLAlchemy建表，无生产迁移回滚。Google Fonts加载Noto Sans SC/Noto Serif SC，失败时字体回退。开发密钥和演示账号供本地模拟。

MIT License。
