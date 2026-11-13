# Xcode 双版本与磁盘只读审计

**状态：READONLY_AUDIT_COMPLETE**  
审计时间：2026-08-07 18:41 +0800  
边界：仅对指定应用、Developer 目录、受限项目元数据和运行进程取证；未删除、移动、压缩、卸载、切换、启动 GUI、构建、清缓存或修改任何内容。

## 结论

**当前暂不可删除。** 身份已经明确，但 Xcode 26.6、其 Simulator 和 iOS 27.0 模拟器设备正在运行。当前链结束前，任何 Xcode、Runtime 或 CoreSimulator 数据清理都应视为阻断。

待用户结束当前开发/模拟器任务后，**首选删除候选是唯一精确路径 `/Applications/Xcode-beta.app`**：它是 Xcode 27.0 beta（27A5228h），当前未运行，`xcode-select` 未指向它，限定项目元数据也未发现必须使用 Xcode 27.0 的明确要求。执行删除前仍须由用户再次明确确认这一个绝对路径；本审计没有执行删除。

不要删除当前稳定链 `/Applications/Xcode.app`：它是当前选中且正在使用的 Xcode 26.6，也是所查项目已明确留下 26.0/26.6 创建或升级痕迹的工具链。

## 两个完整 Xcode App

| 精确路径 | 身份 | 线索 | 目录占用 | owner / 权限 / mtime | SDK / 工具链摘要 |
|---|---|---|---:|---|---|
| `/Applications/Xcode.app` | Xcode 26.6，build 17F113 | 稳定命名；当前选中、正在运行 | 分配 3.75 GiB；表观 8.30 GiB | root:wheel / `drwxr-xr-x` / 2026-08-01 19:14 +0800 | iPhoneOS/Simulator、macOS、watchOS、tvOS、xrOS、DriverKit；`XcodeDefault.xctoolchain` |
| `/Applications/Xcode-beta.app` | Xcode 27.0，build 27A5228h | `-beta` 路径及预发布 build 后缀；当前未运行 | 分配 3.57 GiB；表观 8.66 GiB | cczij:staff / `drwxr-xr-x` / 2026-07-17 15:52 +0800 | 同类平台 SDK；`XcodeDefault.xctoolchain` |

`du` 的“分配”值不是保证释放量；APFS clone、压缩和共享块会令删除后的 `df` 增量更低。故删除 beta 的保守即时回收估算为 **0–3.57 GiB**，而不是把 8.66 GiB 表观体积直接当作可释放空间。稳定版对应上界约 3.75 GiB，但不建议删。

## 当前选择与使用状态

- `xcode-select -p`：`/Applications/Xcode.app/Contents/Developer`
- `xcodebuild -version`：Xcode 26.6 / 17F113
- shell `DEVELOPER_DIR`：未设置，因此没有环境变量覆盖当前选择。
- 正在运行：Xcode 26.6 PID 95007；其 Simulator PID 91250；其构建服务子进程 PID 95362；CoreSimulator 核心服务 PID 1394、1396、1453、1454。
- 没有独立 `xcodebuild` 或 `simctl` 命令进程，但这不能抵消上述 GUI、构建服务和模拟器仍在使用的事实。
- 启动设备：iPhone 17，UDID `B146FAD8-F69A-4428-89A2-F4A2DE0EE935`，运行 iOS 27.0 Runtime。未停止或干预。

## Runtime 与其他大项（彼此独立）

| 类型 / 路径 | 占用或身份 | 判断 |
|---|---:|---|
| iOS Simulator Runtime 26.5（23F77） | 7.91 GiB；Ready；本日有使用记录 | 不是 Xcode 26.5 App；当前未启动，但近期使用，不列为立即清理项 |
| iOS Simulator Runtime 27.0（24A5390f） | 7.49 GiB；Ready；当前设备正在运行 | 不是 Xcode 27.0 App；当前严格阻断删除 |
| `/Users/USER/Library/Developer/Xcode/iOS DeviceSupport` | 分配 18.70 GiB | 真机调试支持，不是 Simulator Runtime；删除会影响相应真机调试链 |
| └ `iPhone18,3 26.5.2 (23F84)` | 5.67 GiB | 仅在确认不再调试该系统版本真机后才可另行评估 |
| └ `iPhone18,3 27.0 (24A5390f)` | 13.03 GiB | 可能关联当前/近期 iPhone 17 真机链；信息不足，勿删 |
| `/Users/USER/Library/Developer/CoreSimulator` | 分配 11.75 GiB；表观 11.80 GiB | 几乎全部为 `Devices`；当前有已启动设备，严格阻断 |
| `/Users/USER/Library/Developer/Xcode/DerivedData` | 分配 0.81 GiB；表观 1.08 GiB | 通常可重建，但会丢失缓存并触发重编译；须关闭任务并另行精确授权 |
| `/Users/USER/Library/Developer/Xcode/Archives` | 不存在 | 没有可清理项；未触碰归档、签名或发布证据 |
| `/Library/Developer/CoreSimulator/Profiles/Runtimes` | 不存在 | 当前 Runtime 由系统 MobileAsset/Cryptex 管理，不在此传统目录 |

`simctl runtime list` 报告两个 Runtime 合计 15.4 GiB。Runtime 与 Xcode App、设备数据、DerivedData、Archives、DeviceSupport 是五类不同对象，不能根据相同的版本数字互相替代。

磁盘：`/System/Volumes/Data` 当前 `df` 可用约 **7.52 GiB**，显示 **97%** 使用，确属高压；删除 Xcode 只增加磁盘空间，**不会增加 RAM**。

## 项目依赖最小判断

仅在 `/Users/USER/Documents/app` 的 `project.pbxproj`、`Package.resolved`、项目 `AGENTS.md` 等元数据中定向检索，未构建、未读取业务文件：

- HairTryOnMVP：`CreatedOnToolsVersion = 26.6`，`LastUpgradeCheck = 2660`。
- IChingReflectionMVP：`CreatedOnToolsVersion = 26.6`，`LastUpgradeCheck = 2660`。
- LocalStampMVP：`CreatedOnToolsVersion = 26.0`，`LastUpgradeCheck = 2600`。
- 三者均以 iOS 17.0 为 deployment target；没有发现 `.xcode-version`、Package 锁定或项目规则明确要求 Xcode 27.0。
- 这只能证明“未发现明确锁定 27.0”，不能证明所有未落盘的人工流程或未来测试都不需要 beta。

## 第一性原理与对抗式判断

- **前提：** 根目标是安全释放磁盘；必要条件是候选身份清楚、未被当前链使用、项目兼容性有证据、用户确认唯一精确路径。
- **攻击/误用方式：** 把 iOS 26.5 Runtime 误当 Xcode 26.5；按表观 8.66 GiB 承诺回收；删当前 `xcode-select` 目标；因 27.0 数字相同而误删正在运行的 Runtime；把 DeviceSupport、Archives 或证书链当缓存。
- **阻断证据：** 当前选择和 Xcode 进程都指向 26.6；iOS 27.0 设备已启动；27.0 beta App 没有运行；项目元数据只显示 26.0/26.6；Archives 不存在；占用同时报告分配值与表观值。
- **残余风险：** 尚无用户对 beta 后续用途的人工确认；APFS 实际释放不可只读精确预测；两个 Runtime 本日均使用；DeviceSupport 27.0 是否仍服务真机任务无法仅凭元数据排除。
- **闭环修正：** 先正常结束 Xcode/Simulator/真机任务，由用户确认不再需要 beta，再仅确认 `/Applications/Xcode-beta.app`；任何后续清理应重新核进程、`xcode-select`、精确路径和 `df` 前后差值。

## 推荐顺序（本轮只列，不执行）

1. **现在不删。** 正常结束当前 Xcode 26.6、Simulator 和相关真机/模拟器任务，不强制停止进程。
2. 确认近期无需 Xcode 27.0 beta 后，把 `/Applications/Xcode-beta.app` 作为第一候选；预计实际新增可用空间保守为 0–3.57 GiB。
3. 若仍缺空间，再单独评估可重建的 DerivedData（约 0.81 GiB 分配占用）。
4. 再按具体真机系统版本评估 DeviceSupport；其收益更大，但误删会破坏真机调试支持，尤其 27.0 项当前信息不足。
5. Runtime 必须按“是否仍需该模拟器系统”单独决策；iOS 27.0 正在运行，iOS 26.5 本日也使用过，当前均不建议删。
6. CoreSimulator `Devices` 当前含启动设备；不要整目录处理。Archives、证书、账号、签名材料不进入清理范围。

**删除前必须由用户确认的唯一精确路径：`/Applications/Xcode-beta.app`。**
