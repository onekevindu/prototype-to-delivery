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

直接在你使用的 Codex、Gemini CLI 或 Antigravity 聊天中提出安装要求即可。指定宿主和目标版本，由 Agent 根据宿主能力、配置和已有安装确定正确位置；用户无需判断目录或执行安装脚本，也无需安装 Python、Node.js 等运行环境。

### 通过聊天安装指定版本

把下面这段话发给 Agent，将“当前宿主”换成你实际使用的软件名称也可以：

```text
请为我当前使用的 Coding Agent 安装 prototype-to-delivery，指定版本 v1.0.3。
仓库：https://github.com/onekevindu/prototype-to-delivery

请根据实际宿主、配置和已有安装确定正确目录，优先使用宿主原生安装能力。
自行选择 Git 或下载对应标签 ZIP 的方式完成，不要求我安装额外运行环境。
若已有旧版本，先完整备份到技能扫描目录之外，再替换为指定版本；失败时恢复旧安装。
完成后告诉我安装版本、实际路径、备份位置，以及宿主是否已识别该 Skill。
如果无法确定目标宿主或发现多个有效安装位置，再向我确认。
```

### 更新、重新安装或回退

使用同样的聊天方式说明目标版本。更新到当前发布版本：

```text
请将当前宿主中已安装的 prototype-to-delivery 更新为 v1.0.3。
仓库：https://github.com/onekevindu/prototype-to-delivery
请查找实际安装位置，备份旧版本后完成替换，并验证宿主识别情况。
```

需要重装旧版本时，直接指定历史标签，例如：

```text
请将当前宿主中的 prototype-to-delivery 重新安装为 v1.0.1。
仓库：https://github.com/onekevindu/prototype-to-delivery
请先备份当前安装及本地修改，安装指定标签对应的版本，再核对版本与识别状态。
```

可安装的历史版本见 [GitHub 标签列表](https://github.com/onekevindu/prototype-to-delivery/tags)。已发布标签保留，不移动、不覆盖；Agent 可通过 Git 或该标签的 ZIP 获取相应版本。当前版本见 [VERSION](VERSION)，变更与迁移说明见 [CHANGELOG.md](CHANGELOG.md)。

安装完成后，以 Agent 报告的实际安装位置和宿主识别结果为准。文件已放入目录、宿主已识别、当前任务已激活该 Skill 是不同状态；尚未验证的部分应如实说明。

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

维护者可在开发环境中使用依赖 PyYAML 的 `scripts/verify.py` 校验文件与 YAML 元数据，相关回归测试位于 `tests/test_verify.py`。这些是可选维护工具，不是用户安装 Skill 的前置步骤。

发布时更新 `VERSION`、`CHANGELOG.md` 和本页聊天示例中的版本号，通过验证后提交并创建对应 Git 标签，再推送分支和标签。GitHub 会提供该标签的源码 ZIP，历史标签持续保留。

---

## 📄 License

[MIT License](LICENSE)
