# macOS 磁盘空间审计报告

审计日期：2026-07-26  
审计模式：只读  
执行结果：未删除文件、未修改系统设置、未修改项目文件  
敏感信息：未读取 `.env`、API Key、Token、SSH Key、Cookie 或密码文件内容

## 1. 当前磁盘状态

|指标|结果|
|---|---:|
|数据卷总容量|约 228.27 GiB|
|已使用空间|约 177.98 GiB|
|剩余可用空间|约 6.75 GiB|
|使用率|97%|

说明：

- 数值来自 `/System/Volumes/Data` 的 `df` 结果。
- APFS 的共享容器、purgeable 空间、快照、clone 和保留空间会导致“总容量－已使用”不等于 Finder 显示的可用空间。
- 本报告中的目录大小存在父子目录重叠，不应直接相加。
- Docker sparse image 和 code-sign clone 的逻辑大小不等于真实独占物理空间。

## 2. 重点目录概览

|路径|大小|结论|
|---|---:|---|
|`/Users/USER/Downloads`|约 21.74 MiB|占用很小；存在少量精确重复图片|
|`/Users/USER/Desktop`|约 8 KiB|无需清理|
|`/Users/USER/Documents`|约 24.65 GiB|主要来自慈善网站 Demo 和原点向量官网 V2|
|`/Users/USER/Library`|约 48.52 GiB|主要来自 Application Support、Containers、Caches 和 pnpm|
|`/private/tmp`|约 29.24 GiB|当前最大可治理来源；含活跃、未提交和不活跃副本|
|`/Users/USER/.codex`|约 8.16 GiB|会话、日志数据库、worktree 和生成资产；不能当普通缓存删除|
|`/Users/USER/.cache`|约 2.43 GiB|以 Codex runtime、uv、Prisma、Node 缓存为主|
|`/Users/USER/.npm`|约 1.68 GiB|可重新下载的 npm 缓存|
|`/Users/USER/Library/pnpm`|约 3.21 GiB|pnpm store；应使用官方 prune|

### 开发相关

|项目|结果|
|---|---|
|`node_modules`|可访问范围内 321 个，合计约 1.30 GiB|
|`.cache`|约 2.43 GiB|
|`.npm`|约 1.68 GiB|
|`.yarn`|未发现显著占用|
|`.pnpm-store`|未发现显著的用户级独立目录；主要 pnpm store 位于 `~/Library/pnpm`|
|`~/Library/Caches/pnpm`|约 0.87 GiB|

### AI 工具

|路径|大小|判断|
|---|---:|---|
|`/Users/USER/Library/Application Support/Claude-3p`|约 11.73 GiB|主要是 Claude VM；不用该功能时可确认清理|
|`/Users/USER/Library/Application Support/Claude`|约 350.45 MiB|应用数据，不按普通缓存处理|
|`/Users/USER/.codex`|约 8.16 GiB|历史、数据库、worktree；HIGH|
|`/Users/USER/Library/Caches/Codex`|约 955.98 MiB|可重建缓存；需退出 Codex|
|`/Users/USER/Library/Caches/com.openai.atlas`|约 1.13 GiB|可重建缓存；需退出 Atlas|
|`/Users/USER/Library/Application Support/com.openai.atlas`|约 218 MiB|可能含浏览器资料；HIGH|
|Hugging Face 缓存|未发现显著占用|
|Ollama/本地模型缓存|未发现显著占用|

### 开发工具

|工具|结果|
|---|---|
|Docker|容器目录约 1.18 GiB 实际占用；`Docker.raw` 逻辑长度约 228.27 GiB，必须通过 Docker UI 管理|
|Xcode|未发现显著的 Xcode/Simulator 目录|
|Android Studio|未发现显著的 Android/Gradle 目录|
|VS Code|`.vscode` 约 0.93 GiB，Application Support 约 0.48 GiB|
|JetBrains|未发现显著占用|
|Open Design|Application Support 约 2.77 GiB，且存在约 0.61 GiB 的 `node_modules`|

### 系统与应用缓存

`/Users/USER/Library/Caches` 合计约 5.83 GiB，主要为：

|路径|大小|风险|
|---|---:|---|
|`/Users/USER/Library/Caches/LarkShell`|约 1.25 GiB|MEDIUM：退出飞书后处理|
|`/Users/USER/Library/Caches/com.openai.atlas`|约 1.13 GiB|MEDIUM：退出 Atlas 后处理|
|`/Users/USER/Library/Caches/Google`|约 1.01 GiB|LOW：Chrome 已退出；不涉及 Chrome 用户资料|
|`/Users/USER/Library/Caches/Codex`|约 0.93 GiB|MEDIUM：退出 Codex 后处理|
|`/Users/USER/Library/Caches/pnpm`|约 0.87 GiB|LOW：使用包管理器清理|
|`/Users/USER/Library/Caches/com.apple.python`|约 235.27 MiB|LOW：Python 缓存，可重新生成|
|`/Users/USER/Library/Caches/node-gyp`|约 53.14 MiB|LOW：可重新生成|
|`/Users/USER/Library/Caches/pip`|约 37.36 MiB|LOW：可重新下载|

检测到 3 个系统更新快照标识。它们属于 macOS 更新流程，不建议手工处理。

## 3. Top 50 最大文件/目录

排序以扫描到的目录占用为主；`Docker.raw` 单独标记逻辑长度。父子路径会重叠，不能累计求和。

|路径|大小|类型|风险等级|建议|
|---|---:|---|---|---|
|`/Users/USER/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`|约 228.27 GiB 逻辑；所属容器实际约 1.18 GiB|稀疏磁盘镜像|HIGH|不要手工删除；使用 Docker Desktop 清理|
|`/private/var/folders/1q/6mf7kw2j1z19q1f9dydq60wh0000gn/X/com.google.Chrome.code_sign_clone`|约 145.60 GiB 逻辑|系统临时 APFS clone|HIGH|不要手工删除；重启/系统回收后复查|
|`/Users/USER/Library`|约 48.52 GiB|用户 Library 汇总|HIGH|只处理明确缓存子目录|
|`/private/tmp`|约 29.24 GiB|临时目录汇总|MEDIUM|分离活跃、未提交和不活跃目录后处理|
|`/Users/USER/Library/Application Support`|约 27.23 GiB|应用数据汇总|HIGH|禁止整目录清理|
|`/Users/USER/Documents`|约 24.65 GiB|用户文档/项目汇总|HIGH|只处理确认停用的项目或生成物|
|`/Users/USER/Documents/慈善网站demo`|约 18.85 GiB|项目目录|MEDIUM|项目仍有更新；逐子目录确认|
|`/Users/USER/Library/Application Support/Claude-3p`|约 11.73 GiB|AI VM/应用数据|MEDIUM|不用 Claude-3p 时退出应用并确认清理|
|`/Users/USER/Library/Containers`|约 10.96 GiB|应用沙盒汇总|HIGH|禁止整目录清理|
|`/Users/USER/Documents/慈善网站demo/.qa-runtime`|约 8.63 GiB|QA 运行副本|MEDIUM|核对无活跃任务、无唯一结果后清理|
|`/Users/USER/.codex`|约 8.16 GiB|Codex 数据汇总|HIGH|禁止整目录清理|
|`/Users/USER/Library/Application Support/LarkShell`|约 7.89 GiB|飞书应用数据|HIGH|含用户/应用数据；仅处理明确缓存|
|`/Users/USER/Library/Containers/com.tencent.xinWeChat`|约 5.95 GiB|微信数据|HIGH|不要删除|
|`/Users/USER/Library/Caches`|约 5.83 GiB|缓存汇总|MEDIUM|逐应用退出后处理|
|`/Users/USER/Documents/慈善网站demo/github-source`|约 4.71 GiB|源码/历史副本|HIGH|确认正式仓库与未提交改动前保留|
|`/Users/USER/Documents/原点向量官网V2`|约 3.98 GiB|项目目录|HIGH|当前项目，保留|
|`/Users/USER/.codex/archived_sessions`|约 3.89 GiB|归档会话|MEDIUM|按日期选择性归档/清理，不要整目录删除|
|`/Users/USER/Library/pnpm`|约 3.21 GiB|包存储|LOW|使用 `pnpm store prune`，不要手工随机删子项|
|`/private/var/folders/1q/6mf7kw2j1z19q1f9dydq60wh0000gn/T`|约 3.04 GiB|系统临时目录|MEDIUM|退出相关应用后按精确目录检查|
|`/Users/USER/Library/Application Support/Open Design`|约 2.77 GiB|应用运行数据|HIGH|应用正在使用；不要手工清理|
|`/Users/USER/.cache`|约 2.43 GiB|工具缓存汇总|MEDIUM|逐子目录确认；Codex runtime 当前可能使用|
|`/Users/USER/Library/Application Support/Google`|约 2.31 GiB|Google 用户/更新数据|HIGH|不要整目录删除|
|`/Users/USER/Documents/原点向量官网V2/.git`|约 2.23 GiB|Git 历史|HIGH|禁止手工删除|
|`/private/var/folders/1q/6mf7kw2j1z19q1f9dydq60wh0000gn/X/com.openai.atlas.web.code_sign_clone`|约 2.23 GiB 逻辑|系统临时 clone|HIGH|不要手工删除|
|`/Users/USER/Library/Containers/com.tencent.WeWorkMac`|约 2.18 GiB|企业微信数据|HIGH|不要删除|
|`/Users/USER/.npm`|约 1.68 GiB|npm 缓存|LOW|使用 npm 官方缓存清理|
|`/Users/USER/Documents/慈善网站demo/.git`|约 1.57 GiB|Git 历史|HIGH|禁止手工删除|
|`/Users/USER/Documents/慈善网站demo/workbench`|约 1.53 GiB|项目工作副本|MEDIUM|确认已合并/归档后处理|
|`/private/tmp/ysy-mapping-runtime-3118.UgY0Al`|约 1.52 GiB|临时 Git 工作副本|HIGH|含 27 项未提交改动，保留|
|`/Users/USER/Documents/原点向量官网V2/ovops-v1-color-exploration`|约 1.38 GiB|设计迭代项目|MEDIUM|确认已封板后再归档/清理|
|`/private/var/folders/1q/6mf7kw2j1z19q1f9dydq60wh0000gn/X/com.openai.codex.code_sign_clone`|约 1.34 GiB 逻辑|系统临时 clone|HIGH|不要手工删除|
|`/Users/USER/.codex/sessions`|约 1.28 GiB|当前/历史会话|HIGH|Codex 运行中，禁止处理|
|`/Users/USER/Library/Caches/LarkShell`|约 1.25 GiB|缓存|MEDIUM|退出飞书后可清理|
|`/private/tmp/ysy-29-1-runtime.9Zzgld`|约 1.19 GiB|不活跃临时运行副本|MEDIUM|确认无唯一输出后清理|
|`/Users/USER/Library/Containers/com.docker.docker`|约 1.18 GiB 实际占用|Docker 数据|HIGH|使用 Docker Desktop 管理|
|`/Users/USER/Documents/慈善网站demo/runtime`|约 1.17 GiB|项目运行副本|MEDIUM|确认正式运行入口后处理|
|`/Users/USER/.codex/logs_2.sqlite`|约 1.16 GiB|Codex 日志数据库|HIGH|Codex 运行中；禁止手工删除|
|`/Users/USER/Library/Caches/com.openai.atlas`|约 1.13 GiB|缓存|MEDIUM|退出 Atlas 后可清理|
|`/private/tmp/ysy-primary-actions-24-2.219aUY`|约 1.13 GiB|不活跃临时运行副本|MEDIUM|确认无唯一输出后清理|
|`/private/tmp/ysy-media-replace-24-2.ychFrq`|约 1.13 GiB|不活跃临时运行副本|MEDIUM|确认无唯一输出后清理|
|`/private/tmp/ovops-phase4-1c-operations-runtime`|约 1.12 GiB|不活跃临时运行副本|MEDIUM|确认任务已结束后清理|
|`/private/tmp/ovops-phase4-1c-production-runtime`|约 1.04 GiB|活跃运行目录|HIGH|当前进程工作目录，禁止触碰|
|`/Users/USER/Library/Caches/Google`|约 1.01 GiB|Chrome 缓存|LOW|Chrome 已退出，可作为低风险候选|
|`/Users/USER/Library/Caches/Codex`|约 0.93 GiB|Codex 缓存|MEDIUM|退出 Codex 后处理|
|`/Users/USER/.vscode`|约 0.93 GiB|VS Code 扩展/数据|MEDIUM|按不再使用的扩展清理|
|`/Users/USER/Documents/慈善网站demo/frontend`|约 0.90 GiB|项目源码/依赖|HIGH|当前项目，禁止整目录删除|
|`/Users/USER/Library/Caches/pnpm`|约 0.87 GiB|包缓存|LOW|使用包管理器清理|
|`/private/tmp/ysy-mapping-runtime.zN0aYF`|约 0.82 GiB|活跃运行目录|HIGH|当前进程工作目录，禁止触碰|
|`/private/tmp/ysy30-reverify.tzldkw`|约 0.81 GiB|不活跃临时副本|MEDIUM|确认验收结束后清理|
|`/private/tmp/ysy30-independent.w2NvD8`|约 0.81 GiB|不活跃临时副本|MEDIUM|确认验收结束后清理|

## 4. 垃圾与候选识别

### 4.1 明显垃圾或低风险缓存

|路径/范围|预计可释放|风险|建议|
|---|---:|---|---|
|`/Users/USER/Library/Caches/Google`|约 1.01 GiB|LOW|Chrome 已退出；只清缓存，不碰 Application Support|
|`/Users/USER/.npm`|最多约 1.68 GiB|LOW|使用 npm 官方缓存命令|
|`/Users/USER/Library/Caches/pnpm`|最多约 0.87 GiB|LOW|使用 pnpm 官方清理|
|`/Users/USER/Library/pnpm`|最多约 3.21 GiB，实际 prune 通常更少|LOW|使用 `pnpm store prune`|
|Python、pip、node-gyp、TypeScript 等明确缓存|约 0.36 GiB|LOW|逐目录清理，可重新生成|
|非敏感精确重复文件|理论约 280.32 MiB|LOW/MEDIUM|只删除已确认的冗余副本|

低风险候选的理论上限约 4.0–7.4 GiB；pnpm prune 和 APFS 实际释放量可能明显低于目录大小。

### 4.2 可重新生成文件

- 321 个 `node_modules`，合计约 1.30 GiB。
- `/private/tmp` 内的构建、测试和验收 runtime。
- `~/Library/Caches` 下的应用缓存。
- npm、pnpm、pip、node-gyp、Python 和 TypeScript 缓存。
- 慈善网站的 `.qa-runtime` 在确认验收工作结束、结果已回存后可重新生成。

`node_modules` 当前主要位于 Open Design 项目和工具运行目录；Open Design 正在使用，因此统一标记 MEDIUM，不建议当前批量处理。

### 4.3 潜在旧项目

仅按“目录超过 100 MiB，且目录修改时间超过 21 天”筛选；这不是删除授权。

|路径|大小|最后修改时间|风险|
|---|---:|---|---|
|`/Users/USER/Documents/Codex/2026-06-21`|约 358.70 MiB|2026-06-21 22:32:32|MEDIUM：历史任务资料|
|`/Users/USER/Documents/原点向量/ai-order-entry-mvp`|约 120.36 MiB|2026-07-02 21:39:54|MEDIUM：旧项目候选|

### 4.4 重复文件

扫描边界：

- 仅扫描 Downloads/Documents 中常见图片、文档、视频、音频和压缩包。
- 仅扫描单文件大于 1 MiB。
- 排除 `.git`、`node_modules`、`.next`、密钥/Token/Cookie/密码相关名称。
- 使用 SHA-256 确认内容完全一致。

结果：

- 扫描文件：397。
- 精确重复组：81。
- 冗余副本：143。
- 理论可释放：约 280.32 MiB。

Downloads 中可明确看见的重复组：

|重复内容|副本数|单文件大小|建议|
|---|---:|---:|---|
|`01_logo文件/中文logo透明背景.png` 与 `(1)` 目录副本|2|约 1.01 MiB|保留最新或权威目录|
|`logo中文.png`、`中文logo.png` 及 `(1)` 目录副本|4|约 1.51 MiB|确认命名后只留一份|
|两份 `ChatGPT Image 2026年7月25日 10_36_12...png`|2|约 1.05 MiB|保留最新一份|
|两份 `logo.png`|2|约 1.14 MiB|保留权威目录一份|
|两份 `9.png`|2|约 1.42 MiB|保留权威目录一份|

项目内部的大多数重复媒体来自源码、QA runtime、workbench 和生成目录之间的复制。单文件删除容易破坏交付完整性，建议优先清理整个已确认停用的 runtime，而不是逐张图片删除。

### 4.5 大型缓存

- `/private/tmp`：约 29.24 GiB。
- 同日进一步核对结果：
  - 活跃目录约 2.17 GiB：HIGH。
  - 含未提交 Git 改动的 11 项约 7.10 GiB：HIGH。
  - 其余不活跃、未发现 Git 未提交改动的临时副本约 20.53 GiB：MEDIUM。
- `~/Library/Caches`：约 5.83 GiB。
- npm/pnpm 缓存与 store：约 5.76 GiB。
- Claude VM bundle：约 11.13 GiB，只有确认不再使用 Claude-3p 时才处理。
- Codex archived sessions：约 3.89 GiB，不属于普通缓存。

### 4.6 安装包

- Downloads 当前没有显著的大型 DMG/PKG 安装包。
- 此前位于 `/private/tmp/Docker.dmg` 的安装包已不在当前审计范围中。
- Downloads 中的小型 ZIP/资料包占用很低，不是磁盘爆满主因。

## 5. 禁止删除列表

以下内容统一为 HIGH：

- 任意 `.git` 目录或 Git object/pack。
- 11 个含未提交 Git 改动的 `/private/tmp/ysy-*` 工作副本。
- 5 个仍作为进程工作目录的 `/private/tmp` 运行目录。
- `/Users/USER/Documents/原点向量官网V2` 当前项目源码。
- 慈善网站当前源码、正式交付物、数据库和 media。
- `/Users/USER/.codex/sessions`、SQLite 数据库、worktrees。
- 微信、企业微信、飞书、Telegram、Outlook 等聊天/办公应用数据。
- Google/Atlas 浏览器用户资料、Cookie、登录态和配置。
- Docker.raw 手工删除。
- macOS 更新快照和 code-sign clone 手工删除。
- Keychains、SSH、`.env`、密钥、Token、Cookie、密码文件。

## 6. 建议操作顺序

### 第一阶段：LOW，预计约 4.0–7.4 GiB

1. Chrome 已退出后，只清理 `/Users/USER/Library/Caches/Google`。
2. 使用 npm/pnpm/pip 官方清理机制处理缓存和未引用包。
3. 清理 Python、node-gyp、TypeScript 等明确可重建缓存。
4. 对 Downloads 的 5 组明确重复图片逐组确认，仅保留权威/最新副本。

### 第二阶段：MEDIUM，潜在约 20–45 GiB

1. 为 `/private/tmp` 中约 20.53 GiB 的不活跃、无 Git 未提交改动目录生成完整精确清单。
2. 单独确认慈善网站 `.qa-runtime` 是否已停用，理论约 8.63 GiB。
3. 确认 Claude-3p 是否仍使用；若不用，再评估约 11.13 GiB VM bundle。
4. 退出 Atlas、Codex、飞书后处理对应缓存。
5. 确认两个潜在旧项目和原点向量颜色探索目录是否归档。

### 第三阶段：HIGH，保持不动

1. Git 历史、未提交工作、活跃 runtime。
2. Docker.raw、系统快照、code-sign clone。
3. Codex 数据库/会话/worktree。
4. 浏览器资料、聊天数据、用户文档、数据库、凭据。

## 7. 预计释放空间

|范围|预计释放|可信度|
|---|---:|---|
|低风险缓存和明确重复副本|约 4.0–7.4 GiB|中；pnpm prune 实际值取决于引用情况|
|不活跃 `/private/tmp` 副本|约 20.53 GiB|高于缓存估算，但需完整路径确认|
|慈善网站 `.qa-runtime`|约 8.63 GiB|需项目 Owner 确认|
|Claude-3p VM bundle|约 11.13 GiB|仅在不再使用该功能时|
|旧项目候选|约 0.47 GiB|需人工确认|
|项目/资料重复文件|约 0.28 GiB|SHA-256 精确；逐文件清理风险较高|

不能把以上数字全部相加后当成必然释放量，因为部分目录存在父子重叠、APFS clone、稀疏文件及包存储共享。
