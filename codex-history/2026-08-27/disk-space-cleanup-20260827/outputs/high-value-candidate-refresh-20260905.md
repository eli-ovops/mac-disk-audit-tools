# 内置盘最高价值候选刷新（只读）

时间：2026-09-05 21:17 +08:00  
状态：只读完成；未删除、移动、压缩或清缓存。

## 当前空间

`/System/Volumes/Data`：总量 `239,362,496 KiB`，已用 `205,929,888 KiB`，可用 `6,689,460 KiB`（约6.38GiB），容量97%。

这是当前快照；不把与其他任务并发发生的空间变化归因给任何单一操作。

## 优先候选：Docker安装中副本

精确路径：

`/Users/USER/Library/Application Support/com.docker.install/in_progress`

- 分配大小：`2,199,272 KiB`（约2.10GiB）。
- 顶层仅见 `Docker.app`，占用同为2.10GiB。
- 应用版本：Docker Desktop `4.84.0`，build `234817`。
- `in_progress` mtime：2026-07-31 16:25:18 +08:00；`Docker.app` mtime：2026-07-17 23:06:05 +08:00。mtime不是最后使用时间。
- 当前 `/Applications/Docker.app` 不存在，因此不能证明这是正式安装旁边的重复副本。
- `lsof` 未发现该精确目录或内部Docker.app的打开句柄；launchctl未给出Docker服务线索，但这不是永久无依赖证明。
- 可重建性：应用二进制可重新下载安装；Docker本地镜像、容器与卷不在该目录，且本轮明确保护。
- 建议：**需用户决定**。若确认暂时不需要Docker Desktop，可把该精确路径列为后续删除候选，理论表观收益约2.10GiB；若仍需Docker，应先走官方安装/修复流程，不能把它当已证实垃圾直接删。

## 另外5个大文件

### 1. Docker虚拟磁盘——必须保留

`/Users/USER/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`

- 逻辑大小：245,106,737,152 bytes（约228.27GiB）。
- 实际分配：2,453,912 × 512 bytes（约1.17GiB）。
- mtime：2026-08-01 08:31:17 +08:00；不是最后使用时间。
- 当前未见该文件打开句柄，但Docker使用状态仍为UNKNOWN。
- 可能包含唯一镜像、容器和卷；受当前保护要求约束。
- 建议：**保留**。它不是228GiB可释放机会，删除后果严重。

### 2. Codex日志数据库——必须保留且正在使用

`/Users/USER/.codex/logs_2.sqlite`

- 逻辑/分配大小：约1.82GiB。
- mtime：2026-09-05 21:17:11 +08:00。
- `lsof` 显示多个Codex文件描述符正在打开该数据库。
- 建议：**保留**；数据库且活动中，不属于缓存授权。

### 3. Codex任务历史数据库——必须保留且正在使用

`/Users/USER/.codex/thread_history_1.sqlite`

- 逻辑/分配大小：约1.80GiB。
- mtime：2026-09-05 21:02:05 +08:00。
- `lsof` 显示Codex正在打开该数据库。
- 建议：**保留**；删除会损害任务历史。

### 4. iOS Simulator Runtime镜像——系统管理，保留

`/System/Volumes/Data/System/Library/AssetsV2/com_apple_MobileAsset_iOSSimulatorRuntime/26c9174130fa5962f3e60f2a49963194dadbae4c.asset/AssetData/Restore/094-56039-099.dmg`

- 逻辑大小：8,494,282,293 bytes；实际分配约7.91GiB。
- mtime：2026-08-01 19:34:57 +08:00。
- 当前未见文件句柄，不代表Runtime无依赖。
- 建议：**保留**；不得直接删除系统MobileAsset文件。未来只有确认对应Runtime不用后，才通过Xcode官方管理入口处理。

### 5. Google Updater下载缓存——关闭相关应用后候选

`/Users/USER/Library/Application Support/Google/GoogleUpdater/crx_cache/0669f2316ad15a15d22cb1a58861b45e6b91ce20b19511ba233f3dd8d5344a98`

- 逻辑/分配大小：约0.69GiB。
- mtime：2026-09-04 05:48:19 +08:00。
- 当前未见该精确文件的打开句柄；Google/Chrome后台状态仍不能完全证明为空闲。
- 可重建性：属于Updater下载缓存，可重新下载。
- 建议：**关闭Chrome及Google更新进程后优先候选**；删除前仍需实时复核并获得该精确路径授权。

## 保护边界

- 不操作已由另一Owner删除的四台Clone、其Lexar备份或incident证据。
- 不操作正式QA `E89636C7-7F62-46F2-8781-6B592C3103C2` 或其他Simulator。
- 不删除Docker.raw、Codex数据库/会话、源码、`.git`、锁文件或UNKNOWN项目资产。
- 本报告中的大小是分配/逻辑元数据，不等于删除后 `df` 独占净增。
