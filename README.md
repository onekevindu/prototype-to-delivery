<div align="center">

# 🚀 Prototype to Delivery (`prototype-to-delivery`)

### 一张截图直达可验收代码，告别“监工式”结对编程
**Turn UI Prototypes into Verified, Production-Ready Deliverables — Zero Micromanagement, Zero Blind Guessing.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Compatible with Codex](https://img.shields.io/badge/Codex-Compatible-black?logo=openai)](https://chatgpt.com)
[![Compatible with Google Antigravity](https://img.shields.io/badge/Google%20Antigravity-Compatible-4285F4?logo=google)](https://deepmind.google)
[![Python 3 Ready](https://img.shields.io/badge/Python-3.8+-brightgreen?logo=python)](scripts/verify.py)

<p align="center">
  <b>让 Coding Agent 真正拥有交付确定性</b><br>
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

## 🌟 核心特性 (Features)

1. **两阶段严格边界 (Two-Phase Boundary)**
   - **设计确认前（只读不改）**：深入分析现有代码规范，梳理原型表象背后的业务盲区（权限、状态流转、幂等、事务边界），形成可评审方案。未获确认前绝不擅动业务代码。
   - **设计确认后（自主闭环）**：用户一句“确认，开始开发”，Agent 连续完成“编码 → 真实自测 → 报错自修 → 遗漏自检 → 交付验收说明”，无需反复催促“继续”。
2. **保护 Agent 原生智能 (Zero Micro-Management)**
   - 绝不硬编码死板的步骤清单或伪状态机脚本，不把 Agent 已有的代码检索、推理、架构规划和调试能力弱化为死板模板。
3. **带着建议集中澄清 (Actionable Clarification)**
   - 技术实现细节自行决断；对影响业务结果的关键分歧集中提问，优先结合宿主交互式工具并置顶推荐项 `(Recommended)`，降低用户回复负担。
4. **拒绝伪完成 (Real Verification)**
   - 严格自检，如实区分编译构建、单元测试、本地脚本验证与真实联调，提供清晰可复现的验收路径。

---

## 📁 目录结构 (Repository Structure)

```text
prototype-to-delivery/
├── README.md                 # 项目介绍与快速开始
├── DESIGN_PHILOSOPHY.md      # 核心设计理念与人机协作契约
├── SKILL.md                  # 主技能入口与行为约定
├── scripts/
│   └── verify.py             # 一键自动化验证脚本 (纯标准库，零依赖)
├── agents/
│   └── openai.yaml           # Codex / UI 发现与调用元信息
└── references/
    ├── design-outline.md     # 5维快速审阅结构与高频业务盲区排查
    └── completion-check.md   # 4维完整性自检与交付标准
```

---

## 🚀 安装指南 (Installation)

本 Skill 遵循现代 Coding Agent 通用规范，开箱即用支持 **Codex** 与 **Google Antigravity / Gemini**。

### 1. 安装到 Codex
将本仓库克隆或复制到个人 Codex skills 目录：
```bash
git clone https://github.com/onekevindu/prototype-to-delivery.git ~/.codex/skills/prototype-to-delivery
```

### 2. 安装到 Google Antigravity / Gemini
复制到 Antigravity 全局技能目录：
```bash
git clone https://github.com/onekevindu/prototype-to-delivery.git ~/.gemini/config/skills/prototype-to-delivery
```

---

## 🔍 验证安装是否成功 (Verification)

### 方法一：一键自动验证脚本（推荐）
在本项目根目录下直接运行自带的验证脚本（无第三方依赖，纯 Python 3 标准库）：
```bash
python3 scripts/verify.py
```
脚本会自动检查：
- [x] 当前仓库与必要配置文件的完整性；
- [x] `~/.codex/skills/prototype-to-delivery` 的安装与 YAML 解析；
- [x] `~/.gemini/config/skills/prototype-to-delivery` 的安装与全局生效状态。

---

### 方法二：交互式界面 / 会话中检查

#### 1. 在 Codex 中验证
- **输入联想测试**：在 Codex 聊天输入框中输入字符 `$`，查看弹出的快捷技能列表中是否存在 `$prototype-to-delivery`（显示名称为“原型到交付”）。若能正常联想，说明识别成功。
- **设置面板查看**：在 Codex 的 Settings -> Skills 列表中查看 `prototype-to-delivery` 是否处于已启用状态。

#### 2. 在 Google Antigravity 中验证
- **会话自检问答**：直接在对话框中向 Agent 提问：
  > *“当前已加载了 prototype-to-delivery 技能吗？”*  
  若 Agent 回复已从 `~/.gemini/config/skills/prototype-to-delivery/` 挂载加载，即证明安装成功。
- **场景触发验证**：直接给 Agent 发送一张界面截图并附带一句开发需求（如 *“按这个页面做新增弹窗”*），Agent 会自动主动遵循该技能的阶段一流程（分析代码、澄清疑问、输出设计草案等待您确认，而非直接改代码）。

---

## 💡 日常使用方法 (Usage)

在会话中直接提供原型图或可交互链接，附带一句简短说明即可触发：
```text
按这份原型和说明完成这个功能。[粘贴原型图/链接 + 关键业务说明]
```
*(在 Codex 中也可通过 `$prototype-to-delivery` 显式唤起)*

---

## 📄 License

[MIT License](LICENSE)
