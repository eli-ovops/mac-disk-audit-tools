# Mac磁盘审计工具

用于盘点和分析磁盘文件的工具资料；发布过程不执行清理。

GitHub：[eli-ovops/mac-disk-audit-tools](https://github.com/eli-ovops/mac-disk-audit-tools)

## 内容

本次公开副本包含 46 个来源文件。

- [`disk-audit/App保留性复制-20261004.py`](disk-audit/App%E4%BF%9D%E7%95%99%E6%80%A7%E5%A4%8D%E5%88%B6-20261004.py)
- [`disk-audit/App副本可用性与释放候选-20261004.json`](disk-audit/App%E5%89%AF%E6%9C%AC%E5%8F%AF%E7%94%A8%E6%80%A7%E4%B8%8E%E9%87%8A%E6%94%BE%E5%80%99%E9%80%89-20261004.json)
- [`disk-audit/App副本补验-20261004.py`](disk-audit/App%E5%89%AF%E6%9C%AC%E8%A1%A5%E9%AA%8C-20261004.py)
- [`disk-audit/Codex会话按项目清理清单.md`](disk-audit/Codex%E4%BC%9A%E8%AF%9D%E6%8C%89%E9%A1%B9%E7%9B%AE%E6%B8%85%E7%90%86%E6%B8%85%E5%8D%95.md)
- [`disk-audit/HTTP缓存剩余刷新-20261005.json`](disk-audit/HTTP%E7%BC%93%E5%AD%98%E5%89%A9%E4%BD%99%E5%88%B7%E6%96%B0-20261005.json)
- [`disk-audit/ModuleCache-index最小复核-20261004.json`](disk-audit/ModuleCache-index%E6%9C%80%E5%B0%8F%E5%A4%8D%E6%A0%B8-20261004.json)
- [`disk-audit/ModuleCache-index精确删除-20261004.回执.json`](disk-audit/ModuleCache-index%E7%B2%BE%E7%A1%AE%E5%88%A0%E9%99%A4-20261004.%E5%9B%9E%E6%89%A7.json)
- [`disk-audit/npm-cacache精确删除-20261004.回执.json`](disk-audit/npm-cacache%E7%B2%BE%E7%A1%AE%E5%88%A0%E9%99%A4-20261004.%E5%9B%9E%E6%89%A7.json)
- [`disk-audit/npm-pnpm候选只读核验-20261004.json`](disk-audit/npm-pnpm%E5%80%99%E9%80%89%E5%8F%AA%E8%AF%BB%E6%A0%B8%E9%AA%8C-20261004.json)
- [`disk-audit/pnpm-v10依赖有限核验-20261004.json`](disk-audit/pnpm-v10%E4%BE%9D%E8%B5%96%E6%9C%89%E9%99%90%E6%A0%B8%E9%AA%8C-20261004.json)

文件类型：.txt（15）、.json（15）、.md（12）、.py（3）、.mjs（1）。

## 使用与阅读入口

先查看保留的原项目 README、包清单与直接相关源码；运行环境和依赖以项目内实际说明为准。

## 来源与许可

本仓库新增介绍及用户原创部分按 MIT 许可公开；第三方材料按其各自许可证和署名使用，不以本许可证重新授权第三方内容。

来源文件中记录的公开 GitHub 链接（不表示已逐项独立验证）：
- https://github.com/tuist/tuist/tree/b8dff299786964cc91c2febaab28a161777b0076/examples/xcode/generated_ios_app_with_signing

## 当前状态与验证边界

- 本次完成公开副本整理和静态检查；没有运行来源代码、构建 App、安装 Skill 或启动服务。
- 项目可能处于原型、实验或研究阶段；没有将其表述为生产交付、客户验收或经过验证的投资收益。
- 图片、视频、数据库、真实账户记录及未确认可公开的附件没有随本次文本/源码副本上传。
- 部分相对链接、运行依赖或素材可能仍需补齐；原始快照中的静态引用缺口数为 0，该数字不是运行失败数。
- [本次来源文件清单](SOURCE_MANIFEST.csv)
