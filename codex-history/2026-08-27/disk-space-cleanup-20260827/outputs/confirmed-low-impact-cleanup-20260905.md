# 低影响精确清理回报（2026-09-05）

## 结论

- 已删除：`/Users/USER/Library/Application Support/com.docker.install/in_progress`
- 删除前占用：2,199,272 KiB（约 2.10 GiB）
- 删除方法：对该精确绝对路径使用 macOS `find -depth -delete`；未使用变量、glob 或父目录递归目标
- 实测净释放：2,195,564 KiB（约 2.09 GiB，以最终复核时 `df -k /System/Volumes/Data` 相对清理前的差值计）
- 当前内置数据卷可用：7,741,492 KiB（约 7.38 GiB），容量显示 97%

## df 证据

- 清理前 Available：5,545,928 KiB
- 删除命令完成后的首次 Available：7,742,204 KiB
- 最终复核时 Available：7,741,492 KiB
- 最终复核相对清理前的差值：2,195,564 KiB（复核期间有 712 KiB 并发写入）

## 验证

- 删除目标：不存在
- 父目录 `/Users/USER/Library/Application Support/com.docker.install`：仍存在
- Docker 数据盘 `Docker.raw`：仍存在
- Google Updater 精确缓存文件：仍存在（723,940 KiB）；Chrome 活动中，因此本轮保留
- 受保护 Simulator `E89636C7-7F62-46F2-8781-6B592C3103C2`：仍存在

## 可恢复性与边界

删除的 Docker 安装残留不能直接恢复，但其内容是未完成安装中的 Docker 应用包，可重新下载。未删除 Docker 用户数据、Simulator、源码、Git、证据或其他未授权路径；未退出或终止任何应用。
