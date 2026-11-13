# 本机缓存与闲置文件只读盘点计划

## 边界

- 只读；不删除、移动、重命名、压缩、归档、清缓存、卸载、改配置、Git 操作或外部写入。
- 不读文件正文，不打开媒体，不读取或输出 secret/token/cookie/私钥/密码/API key/.env/凭证/数据库内容。
- 扫描范围限于用户授权路径；`/Volumes/EXTERNAL` 仅项目、归档、缓存、生成物目录；不扫隐藏系统目录。

## 阶段与门禁

1. 基线与范围核对（已完成）
   - 证据：`work/baseline.txt`（开工时间、df、范围、排除项）
   - 结论：主数据卷开工时约 4.24 GiB 可用；`.Trash` 权限受限；未绕过。
2. 受控元数据盘点（已完成）
   - 证据：`work/scan-evidence.txt`（浅层 du/find/stat/lsof 实际输出摘要）
   - 补充证据：`work/dir-sizes.txt`、`work/large-files.txt`、`work/artifact-scan.txt`、`work/candidate-metadata.txt`、`work/current-recheck.txt`、`work/age-scan.txt`、`work/recheck.txt`
   - 结论：扫描期间出现并发状态漂移；首轮 Downloads 大文件复核时不存在，不纳入当前候选。
3. 分类与报告（已完成）
   - 证据：`outputs/本机缓存与闲置文件只读盘点.md`、`outputs/本机缓存与闲置文件只读盘点.csv`
4. 交付前验证（已完成）
   - 证据：`work/verification.txt`（文件存在、CSV 可解析、无清理命令、覆盖/缺口核验）
