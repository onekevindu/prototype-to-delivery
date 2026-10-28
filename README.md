<div align="center">

# 🚀 Prototype to Delivery (`prototype-to-delivery`)

### 一张截图直达可验收代码，告别“监工式”结对编程
**From UI Prototypes to Reviewable Designs and Verified Deliverables.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Compatible with Codex](https://img.shields.io/badge/Codex-Compatible-black?logo=openai)](https://chatgpt.com)
[![Compatible with Google Antigravity](https://img.shields.io/badge/Google%20Antigravity-Compatible-4285F4?logo=google)](https://deepmind.google)
[![No runtime required](https://img.shields.io/badge/Install-No%20Python%20Required-brightgreen)](#-安装重新安装与更新-installation--updates)

<p align="center">
  <b>减少重复提醒，让 Coding Agent 按确认的设计推进到可验收交付</b><br>
  <b>设计确认前：不凭空盲猜、不擅动代码 | 设计确认后：零催促推进、自主验证闭环</b>
</p>

---

</div>

## 📖 Design Philosophy (设计初衷)

> **为什么这个 Skill 存在？它解决了什么痛点？为什么坚决避免硬编码 Agent 的内部开发步骤？**

当给 Coding Agent 提供原型截图时，传统交互往往陷入两难：要么 **轻率编码盲猜业务**（把外观当业务，造成严重返工），要么 **缺乏自主推进力**（每改一个文件就停下来等用户喊“继续”）。

本 Skill 将成熟开发者的结对协作习惯固化为自动化契约：
👉 **深入阅读：[设计初衷与理念 (DESIGN_PHILOSOPHY.md)](DESIGN_PHILOSOPHY.md)**

---

## 🎯 什么样的项目适合用此 Skill？(Applicability & Scope)

### ✅ 最适合的项目画像 (Best Fit)

| 项目与需求特征 | 典型场景 | 为什么高度契合？ |
| :--- | :--- | :--- |
| **企业级业务系统 / SaaS / 中后台管理** | 医疗、慢病管理、CRM、ERP、OA、政企大屏等 | 这类系统页面背后隐藏大量**机构权限隔离（`orgId`）、状态流转、导出分页与软删除**。Skill 强制“先穿透业务盲区再确认”，防止写出外观相似但业务完全错误的半成品。 |
| **既有成熟代码库的增量开发** | 在现存的前后端、微服务工程中新增模块/页面 | Skill 强制 Agent 先查阅既有技术栈与公共组件库，严格沿用现有分层规范与设计风格，避免无依据造轮子。 |
| **全栈端到端功能闭环** | 提供了一张产品原型，要求把“前端交互 ↔ 后端 API ↔ 数据库持久化”一次性做完 | 坚决拒绝“仅写个纯静态假页面”，驱动 Agent 自主连通真实数据流与自测，直到可验收。 |
| **跨微服务调用与多状态业务** | 涉及数据入库后发 MQ、调远程 Feign 接口、表单防抖/幂等防重 | 驱动 Agent 主动梳理事务边界与失败策略，带着推荐项找你确认，绝不自作主张。 |

### ❌ 不建议使用的场景 (When NOT to Use)

| 不适合的场景 | 原因分析 | 推荐做法 |
| :--- | :--- | :--- |
| **无 UI 原型的底层重构 / 性能调优** | 如慢 SQL 优化、排查内存泄露、JVM 调优 | 无原型图与 UI 契约，强行套用“设计确认流”属于画蛇添足。直接让 Agent 发挥原生代码分析能力即可。 |
| **琐碎的临时 Bug 修复** | 如修复一个 NPE 空指针、修改一行配置文件 | 目标极其单一，“先出设计草案等确认”会徒增交互成本。让 Agent 直接修更快捷。 |
| **纯技术概念答疑或单图求解释** | 如“帮我看看这张截图里的报错是什么意思” | 属于只读咨询任务。Skill 的描述明确排除此类用途，帮助宿主准确选择。 |

---

## 🌟 核心特性 (Features)

1. **两阶段严格边界 (Two-Phase Boundary)**
   - **设计确认前（只读不改）**：深入分析现有代码规范，梳理原型表象背后的业务盲区（权限、状态流转、幂等、事务边界），形成可评审方案。未获确认前绝不擅动业务代码。
   - **设计确认后（自主闭环）**：用户一句“确认，开始开发”，Agent 连续完成“编码 → 真实自测 → 报错自修 → 遗漏自检 → 交付验收说明”，无需反复催促“继续”。
2. **保护 Agent 原生智能 (Zero Micro-Management)**
   - 绝不硬编码死板的步骤清单或伪状态机脚本，不把 Agent 已有的代码检索、推理、架构规划和调试能力弱化为死板模板。
3. **带着建议集中澄清 (Actionable Clarification)**
   - 技术实现细节自行决断；集中澄清当前关键业务分歧，新信息出现时允许继续提问。交互方式使用当前宿主和模式支持的能力，给出有依据的建议。
4. **拒绝伪完成 (Real Verification)**
   - 严格自检，如实区分编译构建、单元测试、本地脚本验证与真实联调，提供清晰可复现的验收路径。

---

## 📁 目录结构 (Repository Structure)

```text
prototype-to-delivery/
├── README.md                 # 项目介绍、适用画像与快速开始
├── DESIGN_PHILOSOPHY.md      # 核心设计理念与人机协作契约
├── SKILL.md                  # 主技能入口与行为约定
├── VERSION                   # Skill 包版本（MAJOR.MINOR.PATCH）
├── CHANGELOG.md               # 各版本变更及迁移说明
├── scripts/
│   └── verify.py             # 文件与元数据校验，可选检查安装文件和 Codex 运行时
├── tests/
│   └── test_verify.py        # 校验失败、退出码和协议处理的回归测试
├── agents/
│   └── openai.yaml           # Codex / UI 发现与调用元信息
└── references/
    ├── design-outline.md     # 5维快速审阅结构与高频业务盲区排查
    └── completion-check.md   # 4维完整性自检与交付标准
```

---

## 🚀 安装、重新安装与更新 (Installation & Updates)

三种方式任选一种，无需 Python、pip、Node.js 或安装器文件。**首次安装、更新和回退使用同一套步骤**：已有目录先完整备份，再放入所选版本，避免新旧文件混合。

以下自动安装命令默认安装到 Codex 的 `~/.agents/skills/prototype-to-delivery`。如果你已有安装，或使用其他宿主，只需把命令中的 `skill_dir` / `$skillDir` 改为实际目录：

| 产品 | 完整安装目录 |
| --- | --- |
| Codex | `~/.agents/skills/prototype-to-delivery`；已有 `~/.codex/skills/prototype-to-delivery` 时使用原目录；自定义 `CODEX_HOME` 时使用其 `skills/prototype-to-delivery` |
| Antigravity App / IDE | `~/.gemini/config/skills/prototype-to-delivery` |
| Antigravity CLI | `~/.gemini/antigravity-cli/skills/prototype-to-delivery` |
| Gemini CLI | `~/.gemini/skills/prototype-to-delivery`，也支持已有的 `~/.agents/skills/prototype-to-delivery` |

`~` 表示用户目录，Windows 中可用 `%USERPROFILE%` 定位。选择实际使用的一个位置即可，避免同一宿主重复发现同名 Skill。目录说明见 [Codex](https://learn.chatgpt.com/docs/build-skills)、[Antigravity](https://antigravity.google/docs/skills)、[Gemini CLI](https://geminicli.com/docs/cli/using-agent-skills/)。

### 方式一：Git 直接克隆安装

适合已有 Git 的用户。复制对应系统的整段命令执行；**克隆前会移走并备份旧安装**，克隆失败时恢复旧目录。

<details>
<summary>macOS / Linux：终端执行</summary>

```bash
(
  set -e
  version="v1.0.2"
  skill_dir="$HOME/.agents/skills/prototype-to-delivery"
  backup_dir=""
  mkdir -p "$(dirname "$skill_dir")" "$HOME/.skill-backups"
  if [ -e "$skill_dir" ] || [ -L "$skill_dir" ]; then
    backup_dir=$(mktemp -d "$HOME/.skill-backups/prototype-to-delivery.XXXXXX")
    mv "$skill_dir" "$backup_dir/prototype-to-delivery"
    printf '旧版本备份：%s\n' "$backup_dir/prototype-to-delivery"
  fi
  if git clone --depth 1 --branch "$version" https://github.com/onekevindu/prototype-to-delivery.git "$skill_dir"; then
    printf '已安装 %s：%s\n' "$version" "$skill_dir"
  else
    rm -rf "$skill_dir"
    [ -z "$backup_dir" ] || mv "$backup_dir/prototype-to-delivery" "$skill_dir"
    exit 1
  fi
)
```

</details>

<details>
<summary>Windows：PowerShell 执行</summary>

```powershell
& {
  $ErrorActionPreference = "Stop"
  $version = "v1.0.2"
  $skillDir = Join-Path $env:USERPROFILE ".agents\skills\prototype-to-delivery"
  $backupDir = $null
  New-Item -ItemType Directory -Force (Split-Path $skillDir) | Out-Null
  if (Test-Path -LiteralPath $skillDir) {
    $backupRoot = Join-Path $env:USERPROFILE ".skill-backups"
    New-Item -ItemType Directory -Force $backupRoot | Out-Null
    $backupDir = Join-Path $backupRoot ("prototype-to-delivery-" + [guid]::NewGuid().ToString("N"))
    Move-Item -LiteralPath $skillDir -Destination $backupDir
    Write-Host "旧版本备份：$backupDir"
  }
  try {
    git clone --depth 1 --branch $version https://github.com/onekevindu/prototype-to-delivery.git $skillDir
    if ($LASTEXITCODE -ne 0) { throw "Git 克隆失败" }
  } catch {
    if (Test-Path -LiteralPath $skillDir) { Remove-Item -LiteralPath $skillDir -Recurse -Force }
    if ($backupDir) { Move-Item -LiteralPath $backupDir -Destination $skillDir }
    throw
  }
  Write-Host "已安装 ${version}：$skillDir"
}
```

</details>

### 方式二：自动下载 ZIP 并安装（无需 Git）

复制对应系统的整段命令执行，自动下载、解压、备份旧安装并放入新版。下载或解压失败时，旧安装仍保留在原位置。macOS/Linux 使用 `curl` 和 `unzip`；Windows 使用系统自带的 PowerShell 下载与解压功能。

<details>
<summary>macOS / Linux：终端执行</summary>

```bash
(
  set -e
  version="v1.0.2"
  skill_dir="$HOME/.agents/skills/prototype-to-delivery"
  work_dir=$(mktemp -d)
  trap 'rm -rf "$work_dir"' EXIT
  curl -fL --retry 2 "https://github.com/onekevindu/prototype-to-delivery/archive/refs/tags/$version.zip" -o "$work_dir/skill.zip"
  unzip -q "$work_dir/skill.zip" -d "$work_dir"
  source_dir="$work_dir/prototype-to-delivery-${version#v}"
  test -f "$source_dir/SKILL.md"
  mkdir -p "$(dirname "$skill_dir")" "$HOME/.skill-backups"
  if [ -e "$skill_dir" ] || [ -L "$skill_dir" ]; then
    backup_dir=$(mktemp -d "$HOME/.skill-backups/prototype-to-delivery.XXXXXX")
    mv "$skill_dir" "$backup_dir/prototype-to-delivery"
    printf '旧版本备份：%s\n' "$backup_dir/prototype-to-delivery"
  fi
  mv "$source_dir" "$skill_dir"
  printf '已安装 %s：%s\n' "$version" "$skill_dir"
)
```

</details>

<details>
<summary>Windows：PowerShell 执行</summary>

```powershell
& {
  $ErrorActionPreference = "Stop"
  $version = "v1.0.2"
  $skillDir = Join-Path $env:USERPROFILE ".agents\skills\prototype-to-delivery"
  $workDir = Join-Path ([IO.Path]::GetTempPath()) ("prototype-to-delivery-" + [guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory $workDir | Out-Null
  try {
    $zipPath = Join-Path $workDir "skill.zip"
    Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/onekevindu/prototype-to-delivery/archive/refs/tags/$version.zip" -OutFile $zipPath
    Expand-Archive -LiteralPath $zipPath -DestinationPath $workDir
    $sourceDir = Join-Path $workDir ("prototype-to-delivery-" + ($version -replace '^v', ''))
    if (-not (Test-Path -LiteralPath (Join-Path $sourceDir "SKILL.md"))) { throw "ZIP 内容不完整" }
    New-Item -ItemType Directory -Force (Split-Path $skillDir) | Out-Null
    if (Test-Path -LiteralPath $skillDir) {
      $backupRoot = Join-Path $env:USERPROFILE ".skill-backups"
      New-Item -ItemType Directory -Force $backupRoot | Out-Null
      $backupDir = Join-Path $backupRoot ("prototype-to-delivery-" + [guid]::NewGuid().ToString("N"))
      Move-Item -LiteralPath $skillDir -Destination $backupDir
      Write-Host "旧版本备份：$backupDir"
    }
    Move-Item -LiteralPath $sourceDir -Destination $skillDir
    Write-Host "已安装 ${version}：$skillDir"
  } finally {
    Remove-Item -LiteralPath $workDir -Recurse -Force
  }
}
```

</details>

### 方式三：手动安装

1. 下载 [v1.0.2 ZIP](https://github.com/onekevindu/prototype-to-delivery/archive/refs/tags/v1.0.2.zip) 并解压。
2. 若已有安装，将整个旧目录移到用户目录下的 `.skill-backups` 中，并用版本号或日期区分。
3. 将解压得到的 `prototype-to-delivery-1.0.2` 文件夹改名为 `prototype-to-delivery`，放到上表中对应的位置。
4. 确认最终路径直接是 `…/skills/prototype-to-delivery/SKILL.md`，在宿主中刷新或开始新任务。

### 更新与安装历史版本

在 [GitHub 历史版本](https://github.com/onekevindu/prototype-to-delivery/tags) 选择需要的标签，例如 `v1.0.1`：

- **Git / ZIP 自动安装**：把命令里的 `version` 改成对应标签，重新执行整段命令。
- **手动安装**：下载该标签的 ZIP，按方式三重新安装。

已发布标签保留，不移动、不覆盖；不同版本可以重新下载。当前版本见 [VERSION](VERSION)，变化见 [CHANGELOG.md](CHANGELOG.md)。旧目录备份包含本地定制、安装记录和旧 `.git`；需要保留定制时，从备份中取回并比较合并。

这些命令只处理选定的安装目录；已有其他位置的同名副本时，应先整理为一个有效安装位置。备份在 skills 扫描目录之外，确认新版正常后可自行清理。

---

## 🔍 验证安装是否成功 (Verification)

安装完成后直接在宿主中检查：

### 1. 在 Codex 中验证

- **输入联想测试**：在 Codex 聊天输入框中输入字符 `$`，查看弹出的快捷技能列表中是否存在 `$prototype-to-delivery`（显示名称为“原型到交付”）。若能正常联想，说明识别成功。
- **设置面板查看**：在 Codex 的 Settings -> Skills 列表中查看 `prototype-to-delivery` 是否处于已启用状态。

### 2. 在 Antigravity 中验证

- **App / IDE**：检查产品的技能列表或 Customizations 中是否发现并启用该技能。App 支持显式输入 `/prototype-to-delivery`。
- **CLI**：检查 `/prototype-to-delivery` 是否可调用；使用插件分发时，可通过 `agy plugin list --json` 核对插件提供的技能。
- Agent 的口头“已加载”回复不能单独证明发现成功；结合宿主列表、实际调用和读取该 Skill 的执行记录确认。

### 3. 在 Gemini CLI 中验证

- 执行 `/skills list` 查看发现及启用状态，必要时执行 `/skills reload` 后重查。
- 显式要求使用 `prototype-to-delivery` 并查看激活过程，按当前宿主的授权机制确认。

随后可用一项小型原型任务检查行为：设计确认前是否保持分析，确认后是否自主完成实现与验证。发现、启用和实际遵循是不同的检查层次。

---

## 💡 日常使用方法 (Usage)

安装并确认可被宿主发现后，在会话中提供原型图或可交互链接及简短说明，让宿主按任务匹配此 Skill：
```text
按这份原型和说明完成这个功能。[粘贴原型图/链接 + 关键业务说明]
```
*(在 Codex 中也可通过 `$prototype-to-delivery` 显式唤起)*

---

## 📦 可选的维护者验证与发布

普通用户安装时无需执行本节。维护者可在已有的 Python 开发环境安装 PyYAML，运行 YAML 校验与回归测试：

```bash
python3 -m pip install PyYAML
python3 scripts/verify.py
python3 -m unittest discover -s tests -v
```

`verify.py` 默认只检查本地文件与 YAML 元数据；显式使用 `--platform codex --runtime --timeout 10` 时检查本地 Codex 的发现与启用状态。文件检查、运行时发现和实际业务行为应分别验证。

发布时更新 `VERSION`、`CHANGELOG.md` 和本页命令中的版本号，通过验证后提交并创建对应 Git 标签，再推送分支和标签。GitHub 会提供该标签的源码 ZIP，历史标签持续保留。

---

## 📄 License

[MIT License](LICENSE)
