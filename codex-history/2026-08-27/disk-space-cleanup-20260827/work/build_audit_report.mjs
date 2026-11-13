import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const root = '/Users/USER/Documents/Codex/2026-08-27/disk-space-cleanup-20260827';
const work = path.join(root, 'work');
const outputs = path.join(root, 'outputs');
const reportPath = path.join(outputs, 'internal-disk-full-audit-20260905.md');
const csvPath = path.join(outputs, 'internal-disk-full-audit-20260905.csv');
const errorsPath = path.join(outputs, 'internal-disk-audit-errors-20260905.txt');
const dfFields = execFileSync('/bin/df', ['-k', '/System/Volumes/Data'], {encoding:'utf8'}).trim().split('\n').at(-1).trim().split(/\s+/);
const currentAvailGiB = (Number(dfFields[3]) / 1048576).toFixed(2);
const currentCapacity = dfFields[4];

const gib = n => (Number(n) / 1073741824).toFixed(2);
const kibGib = n => (Number(n) / 1048576).toFixed(2);
const iso = epoch => new Intl.DateTimeFormat('sv-SE', {
  timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
}).format(new Date(Number(epoch) * 1000)).replace(' ', 'T') + '+08:00';
const esc = value => `"${String(value ?? '').replaceAll('"', '""')}"`;

const rawFiles = fs.readFileSync(path.join(work, 'large-files-over-100MiB.raw.tsv'), 'utf8')
  .trim().split('\n').filter(Boolean).map(line => {
    const [blocks, logical, mtime, ...rest] = line.split('\t');
    return { itemType: 'file>100MiB', allocatedBytes: Number(blocks) * 512,
      logicalBytes: Number(logical), mtime: iso(mtime), itemPath: rest.join('\t') };
  }).sort((a, b) => b.allocatedBytes - a.allocatedBytes);

const topDirs = [
  [165215752,'2026-09-05 12:49:57 +0800','/Users/USER/Library/Developer/XCTestDevices'],
  [36305256,'2026-09-05 19:14:45 +0800','/Users/USER/.codex'],
  [29333488,'2026-09-05 18:43:41 +0800','/Users/USER/Library/Developer/CoreSimulator/Devices'],
  [19532976,'2026-05-30 18:39:07 +0800','/Users/USER/.codex/sessions'],
  [17116284,'2026-09-05 10:46:35 +0800','/Users/USER/Documents'],
  [16541928,'2026-08-29 10:27:14 +0800','/Users/USER/Library/Application Support'],
  [11655596,'2026-08-25 10:21:33 +0800','/Users/USER/Library/Containers'],
  [9964372,'2026-08-26 09:24:46 +0800','/Users/USER/Documents/app'],
  [9052352,'2026-09-03 14:11:47 +0800','/Users/USER/.codex/archived_sessions'],
  [6825068,'2026-09-05 11:21:54 +0800','/Users/USER/Documents/app/.git'],
  [4517944,'2026-09-05 19:11:17 +0800','/Users/USER/Library/Caches'],
  [4350240,'2026-09-05 06:32:41 +0800','/Users/USER/Library/Developer/Xcode'],
  [3674320,'2026-08-15 10:30:34 +0800','/Users/USER/Library/Application Support/LarkShell'],
  [3642940,'2026-08-19 09:26:28 +0800','/Users/USER/Library/Containers/com.tencent.xinWeChat'],
  [3193916,'2026-09-05 10:24:19 +0800','/Users/USER/Documents/skills'],
  [3096256,'2026-07-17 22:13:41 +0800','/Users/USER/Library/Application Support/Open Design'],
  [3055000,'2026-09-05 14:19:02 +0800','/Users/USER/Documents/skills/external-candidates'],
  [2824884,'2026-08-27 09:04:38 +0800','/Users/USER/Documents/Codex'],
  [2429472,'2026-09-02 23:46:18 +0800','/Users/USER/.codex/generated_images'],
  [2199272,'2026-07-31 16:25:18 +0800','/Users/USER/Library/Application Support/com.docker.install/in_progress'],
].map(([kib, mtime, itemPath]) => ({ itemType: 'top_directory', allocatedBytes: kib * 1024,
  logicalBytes: null, mtime, itemPath }));

const candidateDirs = [
  [1988112,'2026-08-16 17:08:30 +0800','/Users/USER/Library/Caches/Google'],
  [1683808,'UNKNOWN','/Users/USER/Library/Caches/Codex'],
  [3010708,'2026-08-24 20:17:39 +0800','/Users/USER/Library/Developer/Xcode/UserData/Previews'],
  [1091864,'2026-09-02 16:20:25 +0800','/Users/USER/Library/Developer/Xcode/DerivedData'],
  [777884,'UNKNOWN','/Users/USER/.cache/uv'],
  [470868,'UNKNOWN','/Users/USER/.npm/_npx'],
  [180108,'UNKNOWN','/Users/USER/.npm/_cacache'],
].map(([kib, mtime, itemPath]) => ({ itemType: 'candidate_directory', allocatedBytes: kib * 1024,
  logicalBytes: null, mtime, itemPath }));

function classify(itemPath) {
  if (itemPath.includes('/XCTestDevices')) return ['C-PMO确认','是','未见该精确目录打开句柄；EarthOnline执行任务active','可能承载当前/唯一测试现场','删除测试Clone数据；可由后续测试重建','Xcode测试设备元数据+du+lsof','目录/内部文件重复，禁止相加'];
  if (itemPath.includes('/CoreSimulator/Devices/E89636C7-7F62-46F2-8781-6B592C3103C2')) return ['D-必须保留','否','当前有大量打开句柄','当前EarthOnline验收设备','会破坏运行中Simulator现场','lsof','包含于CoreSimulator父目录'];
  if (itemPath.includes('/CoreSimulator')) return ['D-系统/工具管理','可由Xcode重装','Simulator服务/设备有活动','运行时或设备依赖UNKNOWN','直接删文件可破坏Xcode；只能用官方入口','路径用途+mount/lsof/simctl失败','与设备/镜像父目录重叠'];
  if (itemPath.includes('/System/Library/AssetsV2')) return ['D-系统管理','系统可管理','UNKNOWN','系统MobileAsset','不得直接删除系统资产','系统路径+mount','可能与只读运行时镜像共享'];
  if (itemPath.includes('/.codex/sessions') || itemPath.includes('/.codex/archived_sessions') || itemPath.includes('/.codex/generated_images') || itemPath.includes('/.codex/logs_2.sqlite') || itemPath.includes('/.codex/thread_history_1.sqlite') || itemPath === '/Users/USER/.codex') return ['D-必须保留','否/不适用','Codex当前活动','会话/历史/媒体/数据库','会丢失会话、历史或用户生成媒体','路径用途+任务活动','Codex各子项包含于父目录'];
  if (itemPath.includes('/Documents/app')) return ['D-必须保留','否','Git mtime当日；App项目仍有任务','源码/Git/项目证据','整项目或Git删除会丢失唯一工作与历史','du+stat+任务列表','子目录包含于Documents/app'];
  if (itemPath.includes('/Documents/skills/external-candidates')) return ['C-用户/Skills PMO决定','大多可重新下载但未核验全部','mtime当日；Skills PMO存在','候选仓库可能含筛选结果/本地修改','删除会丢失未提交改动或评估材料','目录名+du+stat+任务列表','包含于Documents/skills'];
  if (itemPath.includes('/com.docker.install/in_progress')) return ['C-核验后可清','安装包可重装','无精确打开句柄；应用状态UNKNOWN','需确认正式Docker已安装','删除遗留安装副本；若安装未完成则需重装','du+stat+lsof','包含于Application Support'];
  if (itemPath.includes('/Docker.raw')) return ['D-当前保留','否/数据可能唯一','Docker活动状态UNKNOWN；文件稀疏','容器/镜像/卷可能含数据','删除将丢失Docker全部本地数据','stat逻辑/分配大小','逻辑228.28GiB但分配约1.17GiB'];
  if (itemPath.includes('/Library/Caches/Google')) return ['B-关闭Chrome后','是','已见Chrome打开缓存文件','活动缓存','清理后会重建，首次加载变慢','du+lsof','包含于Library/Caches'];
  if (itemPath.includes('/Library/Caches/Codex')) return ['B-关闭Codex后','是','Codex当前活动','活动缓存','清理后会重建；不得触碰会话/数据库','du+当前任务','包含于Library/Caches'];
  if (itemPath.includes('/Xcode/UserData/Previews')) return ['B-Xcode空闲后','是','Xcode/EarthOnline任务active','SwiftUI Preview生成数据','预览需重新生成','du+stat+任务活动','包含于Xcode/UserData'];
  if (itemPath.includes('/Xcode/DerivedData')) return ['C-App PMO确认','是','EarthOnline构建任务active','构建缓存可能被当前任务使用','下次构建重建','du+stat+任务活动','包含于Xcode'];
  if (itemPath.includes('/.cache/uv')) return ['B-确认uv空闲后','是','未见打开句柄；进程枚举受限','包下载/构建缓存','后续依赖重新下载','du+lsof','包含于.cache'];
  if (itemPath.includes('/.npm/_npx') || itemPath.includes('/.npm/_cacache')) return ['B-Node/npm空闲后','是','活动进程UNKNOWN','npm/npx缓存','后续包重新下载','du','包含于.npm'];
  if (itemPath.includes('/Library/Caches/')) return ['C-逐应用确认','通常','UNKNOWN','可能为活动应用缓存','可能导致重新下载或状态丢失','du+路径用途','包含于Library/Caches'];
  if (itemPath.includes('/Applications/') || itemPath.startsWith('/Applications/')) return ['C-用户决定卸载','可重装','UNKNOWN','已安装应用','删除应用会失去该软件；应使用正常卸载','du+路径','Applications内项目相互独立'];
  if (itemPath.includes('/LarkShell') || itemPath.includes('/com.tencent.xinWeChat') || itemPath.includes('/Open Design') || itemPath.includes('/Telegram Desktop')) return ['D-当前保留','否/UNKNOWN','有应用打开句柄或应用资料属性','聊天/应用数据可能唯一','可能丢失用户数据或应用组件','du+lsof+路径用途','包含于Application Support/Containers'];
  if (itemPath.startsWith('/System/') || itemPath.startsWith('/Library/') || itemPath.startsWith('/private/')) return ['D-系统管理','UNKNOWN','UNKNOWN','系统/开发工具组件','不得手工删除','系统路径','可能与系统卷/APFS共享'];
  return ['D-UNKNOWN保留','UNKNOWN','UNKNOWN','用途或唯一性未证明','误删风险未排除','只读元数据','目录可能与父项重叠'];
}

const allRows = [...rawFiles, ...topDirs, ...candidateDirs]
  .sort((a,b) => b.allocatedBytes - a.allocatedBytes)
  .map((r, i) => {
    const [category,rebuildable,activity,risk,consequence,evidence,overlap] = classify(r.itemPath);
    return {...r, rank:i+1, category,rebuildable,activity,risk,consequence,evidence,overlap};
  });

const csvHeader = ['rank','item_type','allocated_gib','logical_gib','mtime','path','category','rebuildable','recent_activity_or_open_state','dependency_risk','deletion_consequence','evidence','overlap_note'];
const csv = [csvHeader.map(esc).join(',')];
for (const r of allRows) csv.push([
  r.rank,r.itemType,gib(r.allocatedBytes),r.logicalBytes == null ? 'UNKNOWN' : gib(r.logicalBytes),r.mtime,r.itemPath,r.category,r.rebuildable,r.activity,r.risk,r.consequence,r.evidence,r.overlap
].map(esc).join(','));
fs.writeFileSync(csvPath, csv.join('\n') + '\n');

const firstLevel = [
  [296926692,'/System/Volumes/Data/Users'],[26395528,'/System/Volumes/Data/System'],
  [14529044,'/System/Volumes/Data/Library'],[14469012,'/System/Volumes/Data/Applications'],
  [6396096,'/System/Volumes/Data/private'],[3368,'/System/Volumes/Data/.PreviousSystemInformation'],
  [3184,'/System/Volumes/Data/usr'],[284,'/System/Volumes/Data/MobileSoftwareUpdate']
];

const topFileMd = rawFiles.slice(0,30).map((r,i) => `| ${i+1} | ${gib(r.allocatedBytes)} | ${gib(r.logicalBytes)} | ${r.mtime} | \`${r.itemPath}\` | ${classify(r.itemPath)[0]} |`).join('\n');
const topDirMd = topDirs.map((r,i) => `| ${i+1} | ${gib(r.allocatedBytes)} | ${r.mtime} | \`${r.itemPath}\` | ${classify(r.itemPath)[0]} |`).join('\n');
const firstMd = firstLevel.map(([k,p]) => `| \`${p}\` | ${kibGib(k)} |`).join('\n');

const report = `# 内置盘全盘只读空间审计（2026-09-05）

## 结论

内置数据卷在审计开始时余8.1GiB，报告生成瞬间仅余 **${currentAvailGiB} GiB（${currentCapacity}）**，需要尽快清理。审计产物合计不足160KiB，无法解释期间超过2GiB的余量下降；同期存在Codex、Chrome和Simulator/Xcode相关活动，具体新增写入来源为 **UNKNOWN**。该值仍可能继续波动，应以读报告时的新鲜 \`df\` 为准。最大异常不是普通缓存，而是 Xcode 的测试 Clone：\`/Users/USER/Library/Developer/XCTestDevices\` 的 \`du\` 表观值为 **157.56 GiB**。但 EarthOnlineGuide 当前仍有构建/运行时验收任务，且这些目录可能是 APFS 共享克隆；未经 App PMO逐项确认不能删除，实际可回收量只能在删除后用 \`df\` 验证。

除测试 Clone 外，较现实的低影响候选约 **8–10 GiB（不可直接相加保证）**：旧 Docker 安装副本2.10GiB、Xcode Previews2.87GiB、DerivedData1.04GiB、Chrome缓存1.90GiB、Codex缓存1.61GiB、uv缓存0.74GiB。各项均有关闭应用或依赖确认前置条件。

本阶段严格只读，删除/迁移/清缓存均为 **0**。

## 1. 时间、磁盘与挂载边界

- 审计日期：2026-09-05，Asia/Shanghai。
- 数据卷：\`/dev/disk3s5\`，APFS，挂载于 \`/System/Volumes/Data\`。
- 起始 \`df -h /System/Volumes/Data\`：228Gi总量、196Gi已用、8.1Gi可用、97%。
- 报告生成瞬间复核：可用 ${currentAvailGiB}GiB、容量 ${currentCapacity}；四舍五入的Used列无法清楚展示短时变化，Avail列为准。
- 系统卷 \`/\`：\`/dev/disk3s1s1\`，同一APFS容器，不与Data卷数字相加。
- 外接盘：\`/dev/disk7s1\` 挂载于 \`/Volumes/EXTERNAL\`，1.9TiB总量、126Gi已用、1.7TiB可用；未计入内置盘候选。
- 三个只读Simulator Runtime镜像挂载于 \`/Library/Developer/CoreSimulator/Volumes/...\`，\`du -x\` 未跨入这些文件系统。
- \`tmutil listlocalsnapshots\` 对 \`/\` 和Data卷均未列出本地快照；这不证明不存在其他APFS共享块。

## 2. 一级完整分布（可访问部分，分配空间）

| 一级目录 | du GiB |
|---|---:|
${firstMd}

注意：根目录可访问项的 \`du\` 合计约342.11GiB，显著高于 \`df\` 的196GiB已用。它们不能相加解释为物理占用或可回收量；可见证据包括大量重复测试Clone文件，以及Docker.raw的稀疏分配。是否由APFS clone共享造成某个具体差额仍为 **UNKNOWN**。

## 3. 最大20个项目/目录

这些行存在父子包含关系，不可相加。

| # | du GiB | mtime（不是最后使用） | 精确路径 | 分类 |
|---:|---:|---|---|---|
${topDirMd}

## 4. 最大30个可访问文件

分配大小按 \`stat st_blocks × 512\` 计算；逻辑大小取文件长度。文件内容未读取。

| # | 分配GiB | 逻辑GiB | mtime | 精确路径 | 分类 |
|---:|---:|---:|---|---|---|
${topFileMd}

## 5. 可操作候选与前置条件

| 分类 | 精确路径 | 表观大小 | 用途/来源 | 前置条件与后果 |
|---|---|---:|---|---|
| C-PMO确认 | \`/Users/USER/Library/Developer/XCTestDevices\` | 157.56GiB | 53个有效Xcode并行测试Clone，另16个空目录 | 当前EarthOnline任务active；需App PMO逐UUID确认。删除会丢失Clone现场，但可通过测试重建；实际释放UNKNOWN。 |
| C-优先批次 | 最大10个XCTestDevices UUID，见CSV | 38.30GiB | 全为EarthOnlineGuide测试Clone | 当前不能删；待构建/验收停止并复核状态、打开文件、PMO依赖。 |
| C-核验后可清 | \`/Users/USER/Library/Application Support/com.docker.install/in_progress\` | 2.10GiB | 2026-07-31的Docker.app安装中副本 | 未见打开句柄；需确认正式Docker已安装。删除后如安装不完整需重装。 |
| B-关闭Xcode后 | \`/Users/USER/Library/Developer/Xcode/UserData/Previews\` | 2.87GiB | SwiftUI Preview生成设备 | 可重建；删除后预览首次重新生成。 |
| C-App PMO确认 | \`/Users/USER/Library/Developer/Xcode/DerivedData\` | 1.04GiB | Xcode构建缓存 | 当前EarthOnline构建任务active；需逐项目确认，不能全局清。 |
| B-关闭Chrome后 | \`/Users/USER/Library/Caches/Google\` | 1.90GiB | Chrome/Google缓存 | 已有Chrome打开文件；关闭后仅用应用/官方窄入口清理。 |
| B-关闭Codex后 | \`/Users/USER/Library/Caches/Codex\` | 1.61GiB | Codex缓存 | 当前任务自身活动；绝不触碰sessions、DB、memory、worktrees。 |
| B-确认uv空闲后 | \`/Users/USER/.cache/uv\` | 0.74GiB | uv包缓存 | 未见打开句柄，但进程枚举受限；后续需要重新下载包。 |
| C-用户决定 | \`/Users/USER/Documents/skills/external-candidates\` | 2.91GiB | clawwork、goose等下载候选仓库 | mtime为当日且Skills PMO存在；可能含本地评估/修改，不是已证实垃圾。 |

## 6. 必须保留或不得直接处理

- \`/Users/USER/.codex/sessions\` 18.63GiB、\`archived_sessions\` 8.63GiB、\`generated_images\` 2.32GiB：会话、历史和用户媒体；不属于缓存授权。
- \`/Users/USER/Documents/app\` 9.50GiB，其中 \`.git\` 6.51GiB：源码和Git历史，mtime当日，禁止删除或git clean。
- \`/Users/USER/Library/Developer/CoreSimulator/Devices/E89636C7-7F62-46F2-8781-6B592C3103C2\`：lsof显示大量打开句柄，是当前Simulator现场。
- \`/System/Library/AssetsV2\` 内两个iOS Simulator Runtime DMG分别约7.91/7.50GiB分配空间；系统管理，不得直接删文件。
- \`/Library/Developer/CoreSimulator/Images/...dmg\` 约7.04GiB及dyld缓存：由Xcode/CoreSimulator管理，只能在确认不用对应Runtime后通过官方Xcode入口处理。
- Docker.raw逻辑约228.28GiB，但实际分配仅约1.17GiB；删除会丢失Docker镜像、容器和卷，不是228GiB清理机会。
- LarkShell、WeChat、Open Design、Telegram、VS Code扩展、Hermes、应用本体：属于应用数据/运行组件或用途未证明，保留。
- Archives、数据库、SQLite、用户文档、媒体、secret-bearing目录、系统/private数据均未列为可清项。

## 7. 活动与“最后使用”证据边界

- mtime只代表目录项或文件修改时间，**不是最后使用时间**；无法证明的最近使用全部为UNKNOWN。
- lsof明确看到Chrome缓存有写句柄；Open Design有读取句柄；Simulator设备E896...有大量读取句柄；Xcode Archive被Storage Management读取。
- 未发现Docker安装副本、uv缓存或XCTestDevices精确目录的打开句柄，但这不是无进程的充分证明。
- 进程枚举受沙箱限制；\`simctl list devices\` 因CoreSimulatorService连接失败及日志路径无权限而失败，所以Simulator状态不能从simctl闭环。
- Codex任务列表显示EarthOnlineGuide PMO/执行仍active；Skills项目也有近期任务。线程标题和摘要只作为活动线索，不替代项目PMO确认。

## 8. 覆盖限制与失败摘要

- 全Data卷 \`du -x\`：373条成功目录记录，372条错误；大文件 \`find -x\`：249个大于100MiB文件，438条错误。
- 主要未读区域：TCC、Spotlight、Photos、Mail、Messages、Safari、Keychains、MobileSync、CloudDocs、FileProvider、AddressBook、系统/private数据库、若干Apple缓存与容器。
- 主动跳过：Codex sessions/memory正文、浏览器配置/历史、钥匙串、邮件/消息、云端目录和照片库，避免秘密泄露或云端占位文件下载。
- 典型原错：\`Operation not permitted\`、\`Permission denied\`、\`CoreSimulatorService connection became invalid\`、\`Unable to use the DiskManagement framework\`。
- 因此这是“全盘覆盖尝试 + 可访问元数据完整排序”，不是100%可读的完整磁盘画像。

## 9. 验收与下一步

- 执行Owner：已生成本报告、CSV和错误摘要，并核对CSV行数/数值来源。
- PMO：应审查父子重复、项目依赖和候选分类；当前跨任务发送受approval policy限制。
- 用户：下一步应从第5节选择精确路径或UUID批次授权；没有精确批准前不得删除。
- 删除阶段必须重新读取df、状态、lsof/进程、PMO结论；每批后用df实测净增。

## 原始统计入口

- \`work/du-data-depth3.raw.tsv\`
- \`work/du-focused-depth2.raw.tsv\`
- \`work/du-secondary-depth1.raw.tsv\`
- \`work/large-files-over-100MiB.raw.tsv\`
- \`work/du-data-depth3.errors.txt\`
- \`work/large-files.errors.txt\`
`;
fs.writeFileSync(reportPath, report);

const duErrors = fs.readFileSync(path.join(work, 'du-data-depth3.errors.txt'), 'utf8').trim().split('\n');
const findErrors = fs.readFileSync(path.join(work, 'large-files.errors.txt'), 'utf8').trim().split('\n');
const errorSummary = [
  '内置盘只读审计错误摘要 2026-09-05',
  `du_errors=${duErrors.length}`,
  `find_errors=${findErrors.length}`,
  '',
  '代表性原错（未绕过）：',
  ...duErrors.slice(0, 25),
  '',
  'simctl: CoreSimulatorService connection became invalid; Error opening log file: Operation not permitted',
  'diskutil: Unable to run because unable to use the DiskManagement framework.',
  '',
  '完整错误原文位于 work/du-data-depth3.errors.txt 与 work/large-files.errors.txt。',
].join('\n') + '\n';
fs.writeFileSync(errorsPath, errorSummary);

console.log(JSON.stringify({reportPath,csvPath,errorsPath,csvRows:allRows.length,largeFiles:rawFiles.length,topDirectories:topDirs.length}, null, 2));
