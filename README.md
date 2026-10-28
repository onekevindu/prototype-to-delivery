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
│   ├── install.sh            # macOS/Linux 安装管理，无需 Python
│   ├── install.py            # v1.0.0 旧流程兼容，可选
│   └── verify.py             # 文件与元数据校验，可选检查安装文件和 Codex 运行时
├── requirements.txt         # 仅 Python 维护工具依赖，普通安装无需使用
├── tests/
│   ├── test_install_shell.py # 无 Python 环境的安装、更新和失败恢复测试
│   ├── test_install.py       # 旧 Python 安装器的兼容测试
│   └── test_verify.py        # 校验失败、退出码和协议处理的回归测试
├── agents/
│   └── openai.yaml           # Codex / UI 发现与调用元信息
└── references/
    ├── design-outline.md     # 5维快速审阅结构与高频业务盲区排查
    └── completion-check.md   # 4维完整性自检与交付标准
```

---

## 🚀 安装、重新安装与更新 (Installation & Updates)

**安装和使用本 Skill 不需要 Python、pip、Node.js 或虚拟环境。** 它是一组文本指令，下载 ZIP 后复制目录即可；Git 和下述 Shell 脚本都是可选方式。Python 文件只用于维护验证或兼容旧安装流程，不会由 Skill 自动执行。

### 1. 直接下载 ZIP（适用于 Windows、macOS、Linux）

1. 下载 [v1.0.1 ZIP](https://github.com/onekevindu/prototype-to-delivery/archive/refs/tags/v1.0.1.zip) 并解压。
2. 将解压得到的 `prototype-to-delivery-1.0.1` 文件夹改名为 `prototype-to-delivery`。
3. 放到下表中对应产品的 skills 目录，使路径直接成为 `…/skills/prototype-to-delivery/SKILL.md`，不要多套一层文件夹。
4. 在宿主的技能列表中检查发现与启用状态，然后开始新任务。

**目标已存在时，先按“重新安装与回退”备份旧目录，不要选择合并覆盖。** 直接复制整个目录也无需运行其中的 Python 文件。

| 产品 | 用户级目录（最后放入 `prototype-to-delivery` 文件夹） |
| --- | --- |
| Codex | 新安装使用 `~/.agents/skills/`；已安装在 `~/.codex/skills/` 时继续使用原位置；配置 `CODEX_HOME` 时核对其 `skills/` |
| Antigravity App / IDE | `~/.gemini/config/skills/` |
| Antigravity CLI | `~/.gemini/antigravity-cli/skills/` |
| Gemini CLI | `~/.gemini/skills/`，也支持已有的 `~/.agents/skills/` |

`~` 表示用户目录。在 Windows 文件管理器中可用 `%USERPROFILE%` 定位用户目录，再进入对应的 `.agents\skills` 等子目录；不存在时创建。不要在同一宿主的多个兼容目录重复安装。使用 `.agents/skills/` 共用位置时，更新会影响读取它的所有宿主；项目级和插件提供的同名副本也应在宿主中核对。

目录与发现方法参考：[Codex Skills](https://learn.chatgpt.com/docs/build-skills)、[Antigravity Skills](https://antigravity.google/docs/skills)、[Gemini CLI Skills](https://geminicli.com/docs/cli/using-agent-skills/)。

### 2. 可选：用 Shell 管理安装（macOS / Linux）

macOS/Linux 可使用系统自带的 Bash 与标准命令，无需安装 Python。进入下载解压的源码目录后运行；源码与安装目录需分开：

```bash
bash scripts/install.sh install --platform codex
bash scripts/install.sh status --platform codex
```

`--platform` 还支持 `antigravity`、`antigravity-cli`、`gemini-cli`。也可用 `--dest /完整路径/prototype-to-delivery` 明确指定目录。脚本复用已有安装位置；发现多个候选位置时会停止，请明确选择并排除重复安装。

脚本只部署 `SKILL.md`、两个引用文档、`agents/openai.yaml`、`LICENSE`、`VERSION`，并写入 `.installation.cksum`。相同内容重复安装直接跳过；有不同内容时要求明确选择更新或重装。

Windows 用户可直接使用上面的 ZIP 方式，无需为此安装 Bash 或 Python。

### 3. 更新与本地修改

**ZIP 安装用户**：下载新版本 ZIP，先将旧安装完整移到 skills 目录外作为备份，再放入新版目录。有自己修改的内容时，先比较和保留，不要直接覆盖。

**Shell 管理用户**：下载并解压新版本，在新源码目录执行：

```bash
bash scripts/install.sh update --platform codex
```

它检查安装记录和文件校验值，只接受更高版本；相同版本且内容相同则跳过。本地修改、删除或额外文件会阻止自动更新。校验值用于检测文件变化，不是发布者签名或安全认证。

已有 Git 源码仓库也可先确认工作区干净，再运行以下命令；Git 不是 ZIP 安装的前置条件：

```bash
git switch main && git pull --ff-only &&
bash scripts/install.sh update --platform codex
```

更新源码不会自动改变安装目录。`main` 可能含未发布改动；需要可重复安装时使用发布标签对应的 ZIP 或 Git 标签。

### 4. 重新安装、旧版本迁移与回退

**无需命令行的方式**：将整个旧安装移到 skills 扫描目录外，例如用户目录下自己创建的 `skill-backups`，然后放入新版本目录。重新安装、升级或回退都使用这一流程。需要恢复时，先保存当前目录，再将原备份移回原位置。

**Shell 方式**（也适用于 v1.0.0 Python 安装、手工复制、损坏修复、同版本重装及回退）：

```bash
bash scripts/install.sh reinstall --platform codex
bash scripts/install.sh status --platform codex
```

脚本先准备新文件，再将旧目录完整备份到安装目录上两级下的 `skill-backups/prototype-to-delivery/<时间-标识>/`，例如 `~/.codex/skill-backups/…`，随后替换安装。备份包括本地修改和旧 `.git`，实际路径会打印出来，不会自动删除或放进 skills 扫描目录。

v1.0.0 的 `.installation.json` 和手工复制目录需要先执行一次 `reinstall` 迁移，之后可用 Shell 的 `update`。原 `scripts/install.py` 保留供旧流程兼容；无需为迁移安装或运行 Python，也不要混用两种安装器管理同一个目录。

Shell 安装器可捕获的替换失败会恢复旧目录；强制结束进程或断电后需检查备份与安装状态。出现遗留锁时，仅在确认原进程已经结束后移除提示的锁目录。符号链接安装需在链接源维护，脚本不会覆盖它。

需要回退时下载目标版本 ZIP，按上述备份替换流程操作。Shell 用户也可从当前工具恢复一个包含完整六个安装文件的备份：

```bash
bash scripts/install.sh reinstall --platform codex --source /完整备份路径
```

没有 `VERSION` 的旧备份用文件管理器恢复，或取回其中的定制修改。`reinstall` 不自动合并定制；需要保留的改动应先比较并合入准备安装的源码。

版本号见 [VERSION](VERSION)，迁移说明见 [CHANGELOG.md](CHANGELOG.md)。Git 标签固定对应源码，已发布标签不会覆盖。

安装或更新后核对宿主发现状态。Codex 会自动检测技能变更，未出现时重启；Gemini CLI 可执行 `/skills reload`。已经进行中的任务可能仍保留旧上下文，不应假定会即时重新读取。

Shell 安装器退出码：`0` 操作完成或内容相同；`2` 参数错误；其他非零值表示操作失败。它检查文件完整性、版本和变化情况，不承担完整 YAML 解析或运行时加载验证。

---

## 🔍 验证安装是否成功 (Verification)

普通用户直接在宿主中验证，无需执行 Python 脚本。



#### 1. 在 Codex 中验证
- **输入联想测试**：在 Codex 聊天输入框中输入字符 `$`，查看弹出的快捷技能列表中是否存在 `$prototype-to-delivery`（显示名称为“原型到交付”）。若能正常联想，说明识别成功。
- **设置面板查看**：在 Codex 的 Settings -> Skills 列表中查看 `prototype-to-delivery` 是否处于已启用状态。

#### 2. 在 Antigravity 中验证
- **App / IDE**：检查产品的技能列表或 Customizations 中是否发现并启用该技能。App 支持显式输入 `/prototype-to-delivery`。
- **CLI**：检查 `/prototype-to-delivery` 是否可调用；使用插件分发时，可通过 `agy plugin list --json` 核对插件提供的技能。
- Agent 的口头“已加载”回复不能单独证明发现成功；结合宿主列表、实际调用和读取该 Skill 的执行记录确认。

#### 3. 在 Gemini CLI 中验证
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

**本节只面向维护源码和发布版本的人，不是安装或使用 Skill 的步骤。** 完整 YAML 校验和自动化测试使用 Python 3.8+ 与 PyYAML；普通用户可跳过本节。

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/verify.py
python3 -m unittest discover -s tests -v
```

`verify.py` 默认只验证指定 Skill 的文件与 YAML 元数据。可用 `--path /path/to/skill` 指定目录，`--platform codex` 等检查对应平台的安装文件。仅显式添加 `--platform codex --runtime --timeout 10` 才启动本地 Codex app-server 检查发现与启用状态；CLI 位置特殊时加 `--codex-cli /path/to/codex`。其他产品的运行时状态请在宿主内检查。

验证工具退出码：`0` 本次请求的检查通过，`1` 检查失败，`2` 参数错误或缺少可选维护依赖。文件校验和宿主发现成功都不等于业务行为已验证。

- 修改时按兼容性更新 `VERSION`，在 `CHANGELOG.md` 记录变化与迁移方法。修复递增 PATCH，兼容能力递增 MINOR，不兼容契约变化递增 MAJOR。
- 新增执行 Skill 必需的资源时，同步更新安装器的文件清单与相关测试；维护工具不进入 Shell 管理的安装目录。
- Shell 安装器测试在只提供系统命令、不提供 Python/Node/pip 的 PATH 中运行实际子进程，验证普通安装不会调用这些工具。测试执行器使用 Python，不代表被测安装过程依赖 Python。
- 校验通过后提交并创建对应版本标签，再推送分支与该标签。GitHub 自动提供标签对应的源码 ZIP；更新 README 的下载链接。已发布标签不移动、不覆盖。

---

## 📄 License

[MIT License](LICENSE)
