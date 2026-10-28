<div align="center">

# 🚀 Prototype to Delivery (`prototype-to-delivery`)

### 一张截图直达可验收代码，告别“监工式”结对编程
**From UI Prototypes to Reviewable Designs and Verified Deliverables.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Compatible with Codex](https://img.shields.io/badge/Codex-Compatible-black?logo=openai)](https://chatgpt.com)
[![Compatible with Google Antigravity](https://img.shields.io/badge/Google%20Antigravity-Compatible-4285F4?logo=google)](https://deepmind.google)
[![Python 3 Ready](https://img.shields.io/badge/Python-3.8+-brightgreen?logo=python)](scripts/verify.py)

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
│   ├── install.py            # 安装、更新、重新安装、状态检查
│   └── verify.py             # 文件与元数据校验，可选检查安装文件和 Codex 运行时
├── requirements.txt         # 安装/验证工具依赖，运行 Skill 本身不需要安装
├── tests/
│   ├── test_install.py       # 安装生命周期、本地修改保护和失败恢复
│   └── test_verify.py        # 校验失败、退出码和协议处理的回归测试
├── agents/
│   └── openai.yaml           # Codex / UI 发现与调用元信息
└── references/
    ├── design-outline.md     # 5维快速审阅结构与高频业务盲区排查
    └── completion-check.md   # 4维完整性自检与交付标准
```

---

## 🚀 安装、重新安装与更新 (Installation & Updates)

主 Skill 是文本指令，使用时无需 Python。仓库内的维护工具需要 Python 3.8+ 和 PyYAML。**源码仓库与安装目录分开**：从源码运行维护命令，只把 `SKILL.md`、两个引用文档、`agents/openai.yaml`、`LICENSE` 和 `VERSION` 部署给宿主。不会把测试、虚拟环境或整个 Git 仓库放进新安装。

### 1. 准备源码（仅首次克隆）

已有本仓库时进入现有源码目录即可，不必重复 `git clone`。此前直接克隆到 skills 目录的用户，请另建一个源码目录，再按下面的重新安装流程迁移。

```bash
mkdir -p ~/src
git clone https://github.com/onekevindu/prototype-to-delivery.git ~/src/prototype-to-delivery
cd ~/src/prototype-to-delivery
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

以下命令均在这个源码目录中执行，并使用上述虚拟环境。

### 2. 首次安装与状态检查

按实际使用的宿主选择一个平台；不要把同一宿主的多个兼容目录都安装一遍。

```bash
python3 scripts/install.py install --platform codex
python3 scripts/install.py status --platform codex
```

| `--platform` | 新安装默认目录 | 已有安装处理 |
| --- | --- | --- |
| `codex` | `~/.agents/skills/prototype-to-delivery`；显式配置 `CODEX_HOME` 时使用其 `skills/` | 自动复用已存在的 `~/.codex/skills/` 或 `.agents/skills/` 安装，避免额外复制 |
| `antigravity` | `~/.gemini/config/skills/prototype-to-delivery` | Antigravity App / IDE |
| `antigravity-cli` | `~/.gemini/antigravity-cli/skills/prototype-to-delivery` | Antigravity CLI |
| `gemini-cli` | `~/.gemini/skills/prototype-to-delivery` | 也识别已有的 `~/.agents/skills/` 安装 |

将命令中的 `codex` 替换为对应平台即可。发现多个候选安装时，脚本会停止并列出位置，不猜测覆盖顺序。可用 `--dest /完整路径/prototype-to-delivery` 代替 `--platform` 精确选择；该参数必须指向技能目录本身。跨宿主共用 `.agents/skills/` 时，更新会影响读取该目录的所有宿主。项目级或插件安装仍应在宿主中检查，以排除额外的同名副本。

目录与发现方法参考：[Codex Skills](https://learn.chatgpt.com/docs/build-skills)、[Antigravity Skills](https://antigravity.google/docs/skills)、[Gemini CLI Skills](https://geminicli.com/docs/cli/using-agent-skills/)。

### 3. 更新到新版本

先检查源码 `git status --short`；若有本地改动，先自行保留或合并。然后更新源码、工具依赖和安装：

```bash
git switch main && git pull --ff-only &&
python3 -m pip install -r requirements.txt &&
python3 scripts/install.py update --platform codex
```

- `install` 重复安装相同版本和内容时直接跳过；已有不同内容时提示使用 `update` 或 `reinstall`。
- `update` 先核对 `.installation.json` 记录的版本与文件摘要；只接受更高版本，相同内容则跳过。本地修改、删除、额外文件或损坏记录会使更新停止，不会静默覆盖。
- 更新源码不会自动更新安装目录；脚本也不会自行联网、修改宿主配置或改变正在进行的任务。

### 4. 重新安装、旧安装迁移与修复

适用于旧的手工复制/Git 安装、安装损坏、同版本重装，或明确决定用仓库版本替换本地定制：

```bash
python3 scripts/install.py reinstall --platform codex
python3 scripts/install.py status --platform codex
```

每次替换已有目录前都会保留**完整旧安装**，包括本地修改和旧 `.git`。备份在安装目录的上两级下的 `skill-backups/prototype-to-delivery/<时间-标识>/`，例如 `~/.codex/skill-backups/…`；不会放在 `skills/` 扫描目录内，实际路径会打印出来。备份保留到你自行清理，脚本不自动删除。

新文件先准备完成再替换；可捕获的替换失败会恢复旧目录。强制终止进程或断电仍需检查打印路径及备份目录。安装锁遗留时，仅在确认原安装进程已结束后删除提示的锁目录。符号链接安装会停止，避免修改链接背后的源码；应在链接源维护或先人工迁移。

`reinstall` 不自动合并本地定制。需要保留定制时，从备份中评估并合入源码后再部署。若备份是本工具管理的版本，可以使用当前工具恢复它：

```bash
python3 scripts/install.py reinstall --platform codex --source /完整备份路径
```

旧式无 `VERSION` 的备份保留用于人工恢复或提取修改，不会被误当成带版本的安装源。

### 5. 固定版本与回退

版本号保存在 [VERSION](VERSION)，变更记录见 [CHANGELOG.md](CHANGELOG.md)。Git 标签 `vMAJOR.MINOR.PATCH` 固定对应源码；`main` 可能包含尚未发布的改动，不应把它当作不可变版本。

例如固定到首个带版本的发布 `v1.0.0`（首次安装用 `install`，已有安装用 `reinstall`）：

```bash
git fetch origin --tags && git switch --detach v1.0.0 &&
python3 -m pip install -r requirements.txt &&
python3 scripts/install.py reinstall --platform codex
```

回退使用相同流程，替换为需要的已发布标签。`update` 拒绝降级，`reinstall` 会备份当前安装后切换到选定版本。回到持续更新时使用上一节的 `git switch main` 流程。

安装与更新完成后，在宿主中核对发现和启用状态。Codex 会自动检测技能变更；未出现时重启。Gemini CLI 可执行 `/skills reload`。新任务使用新版本；正在进行的任务是否重新读取已加载内容取决于宿主，不应假定会即时替换。

安装工具退出码：`0` 操作完成或内容相同；`1` 安装/状态检查失败；`2` 参数错误或缺少依赖。安装状态检查通过不表示运行时已经加载。

---

## 🔍 验证安装是否成功 (Verification)

### 方法一：验证工具

验证工具使用 PyYAML 解析实际 YAML。建议在项目目录创建独立环境：
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/verify.py
```

默认只检查当前 Skill 的文件与元数据，不把文件存在当成运行时已加载。根据需要显式选择检查：

```bash
python3 scripts/verify.py --path /path/to/prototype-to-delivery
python3 scripts/verify.py --platform codex
python3 scripts/verify.py --platform codex --runtime --timeout 10
python3 scripts/verify.py --platform antigravity
python3 scripts/verify.py --platform antigravity-cli
python3 scripts/verify.py --platform gemini-cli
```

`--platform` 检查所选产品的安装文件与元数据；未安装其他产品不会影响结果。仅 `--platform codex --runtime` 会启动本地 Codex app-server，通过 `skills/list` 检查目标安装是否被识别且启用。CLI 不在常见位置时，可用 `--codex-cli /path/to/codex` 指定。该检查有超时限制并清理子进程，不创建开发会话。

Antigravity 与 Gemini CLI 的运行时加载需在相应产品中另行确认，脚本不会把安装文件检查描述成全局生效。启用的发现状态也不等于当前任务已经激活该 Skill。

退出码：`0` 表示本次明确请求的检查通过；`1` 表示检查失败；`2` 表示参数错误或缺少验证依赖。文件校验通过不代表业务行为或实现质量已验证。

维护安装与验证工具时运行回归测试：

```bash
python3 -m unittest discover -s tests -v
```

---

### 方法二：交互式界面 / 会话中检查

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

## 📦 维护者发布约定

- 修改 Skill 行为、安装资源或维护工具时，按兼容性更新 `VERSION`，并在 `CHANGELOG.md` 说明变化。修复递增 PATCH，兼容能力递增 MINOR，不兼容的协作/安装契约变化递增 MAJOR。
- 新增执行 Skill 必需的资源时，同步更新 `scripts/install.py` 的 `PAYLOAD`；维护文档与测试不进入宿主安装。
- 运行文件验证与回归测试后提交，在对应提交创建同名版本标签，例如 `git tag -a v1.0.0 -m "Release 1.0.0"`，然后推送分支和该标签。已发布标签不移动、不覆盖；后续修复发布新版本。
- 安装记录只用于追踪版本与检测修改，不是发布者签名或真实性认证。文件、运行时发现和业务行为的验证结果应分别报告。

---

## 📄 License

[MIT License](LICENSE)
