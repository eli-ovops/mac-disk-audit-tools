# 四台 XCTest Clone 条件式清理执行报告

状态：受阻（执行沙箱未授予目标路径写入范围，未执行删除）  
时间：2026-09-05 20:00 +08:00  
执行 Owner：任务 `01a040ee-13e0-7463-a980-ab3ef7cedf60`

## 用户授权范围

仅允许在完成 Lexar 应用容器备份、逐文件 SHA-256、源稳定性和隔离恢复验证后，通过官方自定义设备集入口逐台删除：

- `147A407F-FB0A-4452-8458-06858F66B8B5`
- `86057072-EF39-4FCA-8D18-F915D179C714`
- `450560D4-0D4D-4CF5-8B7E-1D0EDED49CC3`
- `EFF53654-9CD0-4518-A44C-506A32BAAA2C`

未授权其他设备、缓存、项目、Runtime或目录。

## 实时只读门禁结果

- 四台目录均存在，目录UDID与 `device.plist` 的UDID一致。
- 名称均为 `Clone 2 of EarthOnlineGuide-QA-Clean-20260826`。
- Runtime均为 `com.apple.CoreSimulator.SimRuntime.iOS-26-5`。
- `device.plist` 状态字段均为 `1`；权威r2报告将其解释为Shutdown。
- 四个应用容器的 `MCMMetadataIdentifier` 均为 `com.earthonline.EarthOnlineGuide`。
- 实时 `lsof` 未发现四台精确设备目录的打开句柄；也未列出 `xcodebuild`、`xctest` 或 `XCTRunner`。
- 项目PMO补充确认：截至2026-09-05 19:59:59未新增对四UUID的构建、测试、安装或配置依赖。
- 正式QA设备 `E89636C7-7F62-46F2-8781-6B592C3103C2` 存在且未触碰。

## 计划备份路径

`/Volumes/EXTERNAL/XCTestCloneBackups/20260905T200027+0800-earthonline-four-clones`

执行前确认父目录和批次目录均不存在，避免覆盖旧备份。

## 阻断错误

本任务申请写入以下最小范围：

- `/Volumes/EXTERNAL/XCTestCloneBackups`
- `/Users/USER/Library/Developer/XCTestDevices`
- `/Users/USER/Library/Logs/CoreSimulator`

当时平台注入的执行政策为 `sandbox_mode=workspace-write`、`approval_policy=never`；额外可写根仅包含本任务工作区、visualizations和临时目录，不包含Lexar、XCTestDevices或CoreSimulator日志路径。权限接口未授予文件写权限。随后对精确备份批次进行一次创建尝试，返回：

```text
mkdir: /Volumes/EXTERNAL/XCTestCloneBackups: Operation not permitted
```

因此没有创建备份目录，没有复制文件，没有生成备份manifest，没有进行隔离恢复验证，也没有执行任何 `simctl delete`。按照用户门禁，不降级为内置盘备份、Finder绕过或无备份删除。

## 删除与空间结果

四台目标目录最终复核全部仍存在；正式QA设备也仍存在。

- 删除前Data卷：`Available=5,175,520 KiB`
- 受阻后Data卷：`Available=5,170,956 KiB`
- 变化：`-4,564 KiB`，属于同期写入波动；实际释放 `0 KiB`
- Lexar最终：`Available=1,867,505,820 KiB`
- 计划备份父目录最终确认不存在。

## 恢复范围

本轮没有形成备份，因此没有可用恢复副本。原四台设备完整保留，当前无需恢复。未来权限获得并成功备份后，保护范围仅是四个EarthOnline应用数据容器；即使成功删除，原Simulator UUID、OS状态和整机现场也不保证原样恢复。

## 唯一下一步

必须由平台为当前任务实际注入上述三个精确写入范围，或由平台提供的权限机制返回明确授予后，才能继续。当前执行上下文没有可验证的具体UI入口，不能猜测设置位置。获得权限后仍必须从备份、哈希、隔离恢复和实时状态门禁重新开始，不能复用本次失败当作通过。

## 20:37 权限重试

用户在项目PMO再次确认相同业务授权后，本任务通过官方权限机制重新申请原三个精确写入范围。权限返回仍为：

```text
{"permissions":{"network":null,"file_system":null},"scope":"turn"}
```

随后使用新的、不覆盖旧文件的预定批次路径进行实际可写核验：

`/Volumes/EXTERNAL/XCTestCloneBackups/20260905T203754+0800-earthonline-four-clones`

结果仍为：

```text
mkdir: /Volumes/EXTERNAL/XCTestCloneBackups: Operation not permitted
```

复核结果：备份父目录及新批次目录均不存在；四台获批UUID和正式QA设备均仍存在；没有执行备份、哈希、隔离恢复或删除。20:38快照中Data卷 `Available=5,027,432 KiB`，Lexar `Available=1,867,495,796 KiB`；实际释放仍为 `0 KiB`。

## 新回合政策复核

本回合平台注入状态仍为：

- `sandbox_mode=workspace-write`
- `approval_policy=never`
- 可写根：本任务工作区、visualizations、`/private/tmp`及任务临时目录
- `/Volumes/EXTERNAL/XCTestCloneBackups`：未授予
- `/Users/USER/Library/Developer/XCTestDevices`：未授予
- `/Users/USER/Library/Logs/CoreSimulator`：未授予

没有新的官方权限授予证据。故本回合没有原样重试 `mkdir`，没有执行任何备份或删除，也没有修改安全配置、身份、环境或使用Finder等方式绕过。失败原因现明确归类为执行沙箱边界，而非普通目录owner权限。
