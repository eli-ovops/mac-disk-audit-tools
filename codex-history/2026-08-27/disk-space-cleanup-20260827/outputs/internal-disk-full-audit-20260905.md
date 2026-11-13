# 内置盘全盘只读空间审计（2026-09-05）

## 结论

内置数据卷在审计开始时余8.1GiB，报告生成瞬间仅余 **5.22 GiB（98%）**，需要尽快清理。审计产物合计不足160KiB，无法解释期间超过2GiB的余量下降；同期存在Codex、Chrome和Simulator/Xcode相关活动，具体新增写入来源为 **UNKNOWN**。该值仍可能继续波动，应以读报告时的新鲜 `df` 为准。最大异常不是普通缓存，而是 Xcode 的测试 Clone：`/Users/USER/Library/Developer/XCTestDevices` 的 `du` 表观值为 **157.56 GiB**。但 EarthOnlineGuide 当前仍有构建/运行时验收任务，且这些目录可能是 APFS 共享克隆；未经 App PMO逐项确认不能删除，实际可回收量只能在删除后用 `df` 验证。

除测试 Clone 外，较现实的低影响候选约 **8–10 GiB（不可直接相加保证）**：旧 Docker 安装副本2.10GiB、Xcode Previews2.87GiB、DerivedData1.04GiB、Chrome缓存1.90GiB、Codex缓存1.61GiB、uv缓存0.74GiB。各项均有关闭应用或依赖确认前置条件。

本阶段严格只读，删除/迁移/清缓存均为 **0**。

## 1. 时间、磁盘与挂载边界

- 审计日期：2026-09-05，Asia/Shanghai。
- 数据卷：`/dev/disk3s5`，APFS，挂载于 `/System/Volumes/Data`。
- 起始 `df -h /System/Volumes/Data`：228Gi总量、196Gi已用、8.1Gi可用、97%。
- 报告生成瞬间复核：可用 5.22GiB、容量 98%；四舍五入的Used列无法清楚展示短时变化，Avail列为准。
- 系统卷 `/`：`/dev/disk3s1s1`，同一APFS容器，不与Data卷数字相加。
- 外接盘：`/dev/disk7s1` 挂载于 `/Volumes/EXTERNAL`，1.9TiB总量、126Gi已用、1.7TiB可用；未计入内置盘候选。
- 三个只读Simulator Runtime镜像挂载于 `/Library/Developer/CoreSimulator/Volumes/...`，`du -x` 未跨入这些文件系统。
- `tmutil listlocalsnapshots` 对 `/` 和Data卷均未列出本地快照；这不证明不存在其他APFS共享块。

## 2. 一级完整分布（可访问部分，分配空间）

| 一级目录 | du GiB |
|---|---:|
| `/System/Volumes/Data/Users` | 283.17 |
| `/System/Volumes/Data/System` | 25.17 |
| `/System/Volumes/Data/Library` | 13.86 |
| `/System/Volumes/Data/Applications` | 13.80 |
| `/System/Volumes/Data/private` | 6.10 |
| `/System/Volumes/Data/.PreviousSystemInformation` | 0.00 |
| `/System/Volumes/Data/usr` | 0.00 |
| `/System/Volumes/Data/MobileSoftwareUpdate` | 0.00 |

注意：根目录可访问项的 `du` 合计约342.11GiB，显著高于 `df` 的196GiB已用。它们不能相加解释为物理占用或可回收量；可见证据包括大量重复测试Clone文件，以及Docker.raw的稀疏分配。是否由APFS clone共享造成某个具体差额仍为 **UNKNOWN**。

## 3. 最大20个项目/目录

这些行存在父子包含关系，不可相加。

| # | du GiB | mtime（不是最后使用） | 精确路径 | 分类 |
|---:|---:|---|---|---|
| 1 | 157.56 | 2026-09-05 12:49:57 +0800 | `/Users/USER/Library/Developer/XCTestDevices` | C-PMO确认 |
| 2 | 34.62 | 2026-09-05 19:14:45 +0800 | `/Users/USER/.codex` | D-必须保留 |
| 3 | 27.97 | 2026-09-05 18:43:41 +0800 | `/Users/USER/Library/Developer/CoreSimulator/Devices` | D-系统/工具管理 |
| 4 | 18.63 | 2026-05-30 18:39:07 +0800 | `/Users/USER/.codex/sessions` | D-必须保留 |
| 5 | 16.32 | 2026-09-05 10:46:35 +0800 | `/Users/USER/Documents` | D-UNKNOWN保留 |
| 6 | 15.78 | 2026-08-29 10:27:14 +0800 | `/Users/USER/Library/Application Support` | D-UNKNOWN保留 |
| 7 | 11.12 | 2026-08-25 10:21:33 +0800 | `/Users/USER/Library/Containers` | D-UNKNOWN保留 |
| 8 | 9.50 | 2026-08-26 09:24:46 +0800 | `/Users/USER/Documents/app` | D-必须保留 |
| 9 | 8.63 | 2026-09-03 14:11:47 +0800 | `/Users/USER/.codex/archived_sessions` | D-必须保留 |
| 10 | 6.51 | 2026-09-05 11:21:54 +0800 | `/Users/USER/Documents/app/.git` | D-必须保留 |
| 11 | 4.31 | 2026-09-05 19:11:17 +0800 | `/Users/USER/Library/Caches` | D-UNKNOWN保留 |
| 12 | 4.15 | 2026-09-05 06:32:41 +0800 | `/Users/USER/Library/Developer/Xcode` | D-UNKNOWN保留 |
| 13 | 3.50 | 2026-08-15 10:30:34 +0800 | `/Users/USER/Library/Application Support/LarkShell` | D-当前保留 |
| 14 | 3.47 | 2026-08-19 09:26:28 +0800 | `/Users/USER/Library/Containers/com.tencent.xinWeChat` | D-当前保留 |
| 15 | 3.05 | 2026-09-05 10:24:19 +0800 | `/Users/USER/Documents/skills` | D-UNKNOWN保留 |
| 16 | 2.95 | 2026-07-17 22:13:41 +0800 | `/Users/USER/Library/Application Support/Open Design` | D-当前保留 |
| 17 | 2.91 | 2026-09-05 14:19:02 +0800 | `/Users/USER/Documents/skills/external-candidates` | C-用户/Skills PMO决定 |
| 18 | 2.69 | 2026-08-27 09:04:38 +0800 | `/Users/USER/Documents/Codex` | D-UNKNOWN保留 |
| 19 | 2.32 | 2026-09-02 23:46:18 +0800 | `/Users/USER/.codex/generated_images` | D-必须保留 |
| 20 | 2.10 | 2026-07-31 16:25:18 +0800 | `/Users/USER/Library/Application Support/com.docker.install/in_progress` | C-核验后可清 |

## 4. 最大30个可访问文件

分配大小按 `stat st_blocks × 512` 计算；逻辑大小取文件长度。文件内容未读取。

| # | 分配GiB | 逻辑GiB | mtime | 精确路径 | 分类 |
|---:|---:|---:|---|---|---|
| 1 | 7.91 | 7.91 | 2026-08-01T19:34:57+08:00 | `/System/Volumes/Data/System/Library/AssetsV2/com_apple_MobileAsset_iOSSimulatorRuntime/26c9174130fa5962f3e60f2a49963194dadbae4c.asset/AssetData/Restore/094-56039-099.dmg` | D-系统管理 |
| 2 | 7.49 | 7.49 | 2026-08-01T23:28:58+08:00 | `/System/Volumes/Data/System/Library/AssetsV2/com_apple_MobileAsset_iOSSimulatorRuntime/312ad20be7722c392982b68ca7f24a2146cee1e5.asset/AssetData/Restore/094-14693-107.dmg` | D-系统管理 |
| 3 | 7.04 | 7.04 | 2026-08-18T09:27:02+08:00 | `/System/Volumes/Data/Library/Developer/CoreSimulator/Images/48EFAFC1-D104-409A-888E-E6D074C7B752.dmg` | D-系统/工具管理 |
| 4 | 2.62 | 2.62 | 2026-08-19T09:29:48+08:00 | `/System/Volumes/Data/Library/Developer/CoreSimulator/Caches/dyld/25G83/com.apple.CoreSimulator.SimRuntime.iOS-26-5.23F77/dyld_sim_shared_cache_arm64` | D-系统/工具管理 |
| 5 | 1.82 | 1.82 | 2026-09-05T19:10:01+08:00 | `/System/Volumes/Data/Users/USER/.codex/logs_2.sqlite` | D-必须保留 |
| 6 | 1.79 | 1.79 | 2026-09-05T18:44:00+08:00 | `/System/Volumes/Data/Users/USER/.codex/thread_history_1.sqlite` | D-必须保留 |
| 7 | 1.37 | 1.37 | 2026-08-19T09:30:34+08:00 | `/System/Volumes/Data/Library/Developer/CoreSimulator/Caches/dyld/25G83/com.apple.CoreSimulator.SimRuntime.iOS-17-0.21A328/dyld_sim_shared_cache_arm64` | D-系统/工具管理 |
| 8 | 1.17 | 228.27 | 2026-08-01T08:31:17+08:00 | `/System/Volumes/Data/Users/USER/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw` | D-当前保留 |
| 9 | 1.01 | 1.01 | 2026-06-30T21:34:09+08:00 | `/System/Volumes/Data/System/Library/AssetsV2/com_apple_MobileAsset_AppleDeveloperDocumentation/11569b51f72c899da19ba24b044ec58978ba2e6a.asset/AssetData/documentation-db/index.sql` | D-系统管理 |
| 10 | 0.90 | 0.90 | 2026-05-18T21:43:18+08:00 | `/System/Volumes/Data/System/Library/AssetsV2/com_apple_MobileAsset_AppleDeveloperDocumentation/7c2022e8d3519b34e3b9e89513d9d73c4c7abef7.asset/AssetData/documentation-db/index.sql` | D-系统管理 |
| 11 | 0.69 | 0.69 | 2026-09-04T05:48:19+08:00 | `/System/Volumes/Data/Users/USER/Library/Application Support/Google/GoogleUpdater/crx_cache/0669f2316ad15a15d22cb1a58861b45e6b91ce20b19511ba233f3dd8d5344a98` | D-系统管理 |
| 12 | 0.63 | 0.63 | 2026-08-29T17:17:30+08:00 | `/System/Volumes/Data/System/Library/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/4d6968efdc76b1ebcd5745a054c54d922d92a329.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_MAC_H16G_Cryptex.dmg` | D-系统管理 |
| 13 | 0.63 | 0.63 | 2026-08-24T20:16:04+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/Xcode/UserData/Previews/Simulator Devices/CE7DBE33-2864-4228-B0D6-2C44DB48102A/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/330dff32e8a1cee42aa95016cac3be4d38ac4169.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | B-Xcode空闲后 |
| 14 | 0.63 | 0.63 | 2026-08-30T13:36:42+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/CoreSimulator/Devices/7DDC2A41-46E2-4F2A-BC2C-A97C1F6819CA/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | D-系统/工具管理 |
| 15 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/CoreSimulator/Devices/E89636C7-7F62-46F2-8781-6B592C3103C2/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | D-必须保留 |
| 16 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/60047CF2-826F-4578-807A-B43D7B9E5BF1/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 17 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/EFF53654-9CD0-4518-A44C-506A32BAAA2C/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 18 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/AF7C845D-7994-4D8E-AB73-6B51761828AE/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 19 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/E8F6A81C-C1F0-494F-B3D0-5C71737AB5EB/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 20 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/96E1CC85-CDF7-49A1-9414-8E53408FD17A/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 21 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/F1B757EC-CAB4-44EE-8AD8-32A816E36460/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 22 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/4A61DF46-D8C6-4D8F-BBD3-0D923C92AC39/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 23 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/298DBD2A-F8B2-4046-9B0D-53728746DD8C/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 24 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/5456EAD1-DF20-470E-9975-623FF19F88CF/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 25 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/7461DA61-3D93-43A0-8C5C-A2CCE3D2D25A/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 26 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/339E73D6-B077-4C66-A38A-172506D968F1/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 27 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/B181B783-0FD9-408A-B427-FCBFE5E3BC3A/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 28 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/86057072-EF39-4FCA-8D18-F915D179C714/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 29 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/974C0E33-A12D-4EBB-A8A6-67A9537FFA30/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |
| 30 | 0.63 | 0.63 | 2026-08-29T09:45:02+08:00 | `/System/Volumes/Data/Users/USER/Library/Developer/XCTestDevices/133FE5B1-FC18-4548-A524-B35F254AE5ED/data/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_UAF_Siri_Understanding/purpose_auto/c079bfa6b8856202dc8cb2135fef3b06229ced6e.asset/AssetData/Restore/UC_SIRI_ASR_ASSISTANT_EN_US_EN_US_H18P_Cryptex.dmg` | C-PMO确认 |

## 5. 可操作候选与前置条件

| 分类 | 精确路径 | 表观大小 | 用途/来源 | 前置条件与后果 |
|---|---|---:|---|---|
| C-PMO确认 | `/Users/USER/Library/Developer/XCTestDevices` | 157.56GiB | 53个有效Xcode并行测试Clone，另16个空目录 | 当前EarthOnline任务active；需App PMO逐UUID确认。删除会丢失Clone现场，但可通过测试重建；实际释放UNKNOWN。 |
| C-优先批次 | 最大10个XCTestDevices UUID，见CSV | 38.30GiB | 全为EarthOnlineGuide测试Clone | 当前不能删；待构建/验收停止并复核状态、打开文件、PMO依赖。 |
| C-核验后可清 | `/Users/USER/Library/Application Support/com.docker.install/in_progress` | 2.10GiB | 2026-07-31的Docker.app安装中副本 | 未见打开句柄；需确认正式Docker已安装。删除后如安装不完整需重装。 |
| B-关闭Xcode后 | `/Users/USER/Library/Developer/Xcode/UserData/Previews` | 2.87GiB | SwiftUI Preview生成设备 | 可重建；删除后预览首次重新生成。 |
| C-App PMO确认 | `/Users/USER/Library/Developer/Xcode/DerivedData` | 1.04GiB | Xcode构建缓存 | 当前EarthOnline构建任务active；需逐项目确认，不能全局清。 |
| B-关闭Chrome后 | `/Users/USER/Library/Caches/Google` | 1.90GiB | Chrome/Google缓存 | 已有Chrome打开文件；关闭后仅用应用/官方窄入口清理。 |
| B-关闭Codex后 | `/Users/USER/Library/Caches/Codex` | 1.61GiB | Codex缓存 | 当前任务自身活动；绝不触碰sessions、DB、memory、worktrees。 |
| B-确认uv空闲后 | `/Users/USER/.cache/uv` | 0.74GiB | uv包缓存 | 未见打开句柄，但进程枚举受限；后续需要重新下载包。 |
| C-用户决定 | `/Users/USER/Documents/skills/external-candidates` | 2.91GiB | clawwork、goose等下载候选仓库 | mtime为当日且Skills PMO存在；可能含本地评估/修改，不是已证实垃圾。 |

## 6. 必须保留或不得直接处理

- `/Users/USER/.codex/sessions` 18.63GiB、`archived_sessions` 8.63GiB、`generated_images` 2.32GiB：会话、历史和用户媒体；不属于缓存授权。
- `/Users/USER/Documents/app` 9.50GiB，其中 `.git` 6.51GiB：源码和Git历史，mtime当日，禁止删除或git clean。
- `/Users/USER/Library/Developer/CoreSimulator/Devices/E89636C7-7F62-46F2-8781-6B592C3103C2`：lsof显示大量打开句柄，是当前Simulator现场。
- `/System/Library/AssetsV2` 内两个iOS Simulator Runtime DMG分别约7.91/7.50GiB分配空间；系统管理，不得直接删文件。
- `/Library/Developer/CoreSimulator/Images/...dmg` 约7.04GiB及dyld缓存：由Xcode/CoreSimulator管理，只能在确认不用对应Runtime后通过官方Xcode入口处理。
- Docker.raw逻辑约228.28GiB，但实际分配仅约1.17GiB；删除会丢失Docker镜像、容器和卷，不是228GiB清理机会。
- LarkShell、WeChat、Open Design、Telegram、VS Code扩展、Hermes、应用本体：属于应用数据/运行组件或用途未证明，保留。
- Archives、数据库、SQLite、用户文档、媒体、secret-bearing目录、系统/private数据均未列为可清项。

## 7. 活动与“最后使用”证据边界

- mtime只代表目录项或文件修改时间，**不是最后使用时间**；无法证明的最近使用全部为UNKNOWN。
- lsof明确看到Chrome缓存有写句柄；Open Design有读取句柄；Simulator设备E896...有大量读取句柄；Xcode Archive被Storage Management读取。
- 未发现Docker安装副本、uv缓存或XCTestDevices精确目录的打开句柄，但这不是无进程的充分证明。
- 进程枚举受沙箱限制；`simctl list devices` 因CoreSimulatorService连接失败及日志路径无权限而失败，所以Simulator状态不能从simctl闭环。
- Codex任务列表显示EarthOnlineGuide PMO/执行仍active；Skills项目也有近期任务。线程标题和摘要只作为活动线索，不替代项目PMO确认。

## 8. 覆盖限制与失败摘要

- 全Data卷 `du -x`：373条成功目录记录，372条错误；大文件 `find -x`：249个大于100MiB文件，438条错误。
- 主要未读区域：TCC、Spotlight、Photos、Mail、Messages、Safari、Keychains、MobileSync、CloudDocs、FileProvider、AddressBook、系统/private数据库、若干Apple缓存与容器。
- 主动跳过：Codex sessions/memory正文、浏览器配置/历史、钥匙串、邮件/消息、云端目录和照片库，避免秘密泄露或云端占位文件下载。
- 典型原错：`Operation not permitted`、`Permission denied`、`CoreSimulatorService connection became invalid`、`Unable to use the DiskManagement framework`。
- 因此这是“全盘覆盖尝试 + 可访问元数据完整排序”，不是100%可读的完整磁盘画像。

## 9. 验收与下一步

- 执行Owner：已生成本报告、CSV和错误摘要，并核对CSV行数/数值来源。
- PMO：应审查父子重复、项目依赖和候选分类；当前跨任务发送受approval policy限制。
- 用户：下一步应从第5节选择精确路径或UUID批次授权；没有精确批准前不得删除。
- 删除阶段必须重新读取df、状态、lsof/进程、PMO结论；每批后用df实测净增。

## 原始统计入口

- `work/du-data-depth3.raw.tsv`
- `work/du-focused-depth2.raw.tsv`
- `work/du-secondary-depth1.raw.tsv`
- `work/large-files-over-100MiB.raw.tsv`
- `work/du-data-depth3.errors.txt`
- `work/large-files.errors.txt`
