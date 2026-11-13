# `/private/tmp` 不活跃 Runtime 清理候选

审计时间：2026-07-26 13:11:41 CST

审计范围仅为 `/private/tmp`。本报告只记录只读检查结果，没有删除文件、修改 Git 或读取 `.env`、数据库、媒体文件的内容。

## 判定口径

- 只统计最外层目录，避免父目录、`.next`、`cache`、`webpack` 重复计算。
- 大小门槛为 500 MiB。
- 必须没有当前进程占用。
- 目录自身及内部均不得存在带未提交修改的 Git 仓库。
- 明确排除 `/private/tmp/ovops-phase4-1c-production-runtime` 和 `/private/tmp/ysy-mapping-runtime.zN0aYF`。
- `HIGH CONFIDENCE`：名称和结构明确属于可重新生成的 runtime/build/test/QA 缓存，且未发现数据库、媒体目录或 `.env*` 文件。
- `MEDIUM CONFIDENCE`：满足大小、进程和 Git 条件，但发现数据库、媒体目录或 `.env*` 文件，或目录名称可能承载阶段性成果，需要人工确认。

## 清理候选

|路径|大小|类型|是否安全删除|理由|
|---|---:|---|---|---|
|`/private/tmp/ovops-phase4-1c-operations-runtime`|1,176,168 KiB（1.12 GiB）|Next.js runtime / `node_modules`|是（HIGH CONFIDENCE）|无进程占用、无 Git 仓库；名称明确为 runtime，含可重新生成的 `.next`/依赖目录；未发现数据库、媒体目录或 `.env*` 文件。|
|`/private/tmp/ysy-29-1-runtime.9Zzgld`|1,248,544 KiB（1.19 GiB）|Next.js / QA runtime 副本|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，且含 `.next`/webpack/依赖；但发现 1 个数据库文件、2 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy-primary-actions-24-2.219aUY`|1,189,368 KiB（1.13 GiB）|Next.js QA 工作副本|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，含 `.next`/webpack/依赖；但发现 1 个数据库文件，且名称可能对应阶段性功能验证。|
|`/private/tmp/ysy-media-replace-24-2.ychFrq`|1,189,200 KiB（1.13 GiB）|媒体替换 QA / Next.js 副本|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库；发现 1 个数据库文件和 1 个媒体类目录，需确认媒体替换结果已留存在权威项目。|
|`/private/tmp/ysy30-reverify.tzldkw`|853,736 KiB（833.7 MiB）|复验 runtime / `.next` cache|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，名称明确为复验副本；但发现 1 个数据库文件、2 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy30-independent.w2NvD8`|846,132 KiB（826.3 MiB）|独立验收 runtime / `.next` cache|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，名称指向独立验证；但发现 2 个数据库文件、2 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy-media-replace-3119.5LgA5N`|811,492 KiB（792.5 MiB）|媒体替换测试构建|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，含 `.next`/webpack；但发现 1 个数据库文件和 1 个媒体类目录。|
|`/private/tmp/ysy30-role.vawnf9`|640,640 KiB（625.6 MiB）|角色权限 QA runtime|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，含 `.next`/webpack/依赖；但发现 1 个数据库文件、2 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy-main-sync-run.HoPaZ3`|636,864 KiB（621.9 MiB）|同步验证运行副本|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，含 `.next`/webpack；但名称含 `main-sync`，且发现 2 个数据库文件、1 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy30-final.4PYMHZ`|634,496 KiB（619.6 MiB）|最终验收 runtime|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，含 `.next`/webpack/依赖；但名称含 `final`，且发现 4 个数据库文件、1 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy-about-rework.hRqhsJ`|631,660 KiB（616.9 MiB）|页面返工 QA / Next.js 副本|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，含 `.next`/webpack/依赖；但发现 1 个媒体类目录和 1 个 `.env*` 文件，需确认返工成果已回写权威项目。|
|`/private/tmp/ysy-26-acceptance.m6kjCJ`|631,460 KiB（616.7 MiB）|验收 runtime / `.next` cache|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，名称明确为验收副本；但发现 1 个数据库文件、1 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy-25-1-runtime-prod.Ee1M6O`|629,224 KiB（614.5 MiB）|模拟生产 runtime|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，含 `.next`/webpack/依赖；名称含 `prod`，并发现 1 个数据库文件、1 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy-25-1-sidebar-runtime-fixed.XP0wMo`|628,720 KiB（614.0 MiB）|修复验证 runtime|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，名称明确为修复验证 runtime；但发现 1 个数据库文件、1 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy-25-1-admin-simplify-build.OuBnnC`|627,528 KiB（612.8 MiB）|后台简化测试构建|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，名称明确为 build；但发现 1 个数据库文件、1 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy-25-1-copy-build.F0Mpvl`|627,120 KiB（612.4 MiB）|文案测试构建|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，名称明确为 build；但发现 1 个数据库文件、1 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy-27-retest.aCyPLg`|626,136 KiB（611.5 MiB）|回归测试 runtime|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，名称明确为 retest；但发现 1 个数据库文件、1 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy26-2-build-direct.UpbyG7`|625,788 KiB（611.1 MiB）|直接构建产物|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，名称明确为 build；但发现 1 个数据库文件、1 个媒体类目录和 1 个 `.env*` 文件。|
|`/private/tmp/ysy27-build.mvydSf`|625,536 KiB（610.9 MiB）|测试构建产物|需人工确认（MEDIUM CONFIDENCE）|无进程占用、无 Git 仓库，名称明确为 build；但发现 1 个数据库文件、1 个媒体类目录和 1 个 `.env*` 文件。|

## 预计释放空间

- **HIGH CONFIDENCE：可以删除**  
  1 个最外层目录，逻辑占用 **1,176,168 KiB（约 1.12 GiB）**。

- **MEDIUM CONFIDENCE：需要人工确认**  
  18 个最外层目录，逻辑占用 **13,703,644 KiB（约 13.07 GiB）**。

- **全部候选合计**  
  19 个最外层目录，逻辑占用 **14,879,812 KiB（约 14.19 GiB）**。

以上为 `du` 统计的逻辑占用。受 APFS 共享块、稀疏文件等影响，未来实际释放空间可能低于该数值。

## 已明确排除

以下目录没有进入候选表：

- 当前进程占用且用户明确排除：
  - `/private/tmp/ovops-phase4-1c-production-runtime`
  - `/private/tmp/ysy-mapping-runtime.zN0aYF`
- 包含未提交 Git 修改：
  - `/private/tmp/ysy-mapping-runtime-3118.UgY0Al`：27 项
  - `/private/tmp/ysy-frontend-six-rerun.rlGnFb`：81 项
  - `/private/tmp/ysy-council-actions-green.R0aWA1`：95 项
  - `/private/tmp/ysy-nav-hover-tests-green.4kYtqh`：102 项
  - `/private/tmp/ysy-26-2-bugtest.ZuQRfb`：61 项
  - `/private/tmp/ysy-25-1-sidebar-arrow.NuHEnA`：60 项
  - `/private/tmp/ysy-25-1-code-build.yXXmvq`：59 项
  - `/private/tmp/ysy-home-submenu.3Ep0RQ`：102 项

## 安全结论

本报告没有执行删除，也不构成对 `MEDIUM CONFIDENCE` 项的删除授权。后续若要实际清理，应重新复核精确路径、进程占用、Git 状态及受保护数据标记，并由用户逐类明确批准。
