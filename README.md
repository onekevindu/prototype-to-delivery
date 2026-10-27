# Prototype to Delivery (`prototype-to-delivery`)

> **根据原型、界面截图或图片说明开展软件功能开发：先形成可确认的开发设计，确认后自主完成实现、验证与交付，减少用户反复提醒。**  
> *Transform prototypes and screenshots into verified, production-ready deliverables with autonomous execution and strict human-in-the-loop design approval.*

---

## 📖 Design Philosophy

Why this skill exists, what problems it solves, and why it deliberately avoids prescribing the Coding Agent's internal development workflow.

👉 **[设计初衷与理念 (DESIGN_PHILOSOPHY.md)](DESIGN_PHILOSOPHY.md)**

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
├── README.md
├── DESIGN_PHILOSOPHY.md      # 设计初衷与理念
├── SKILL.md                  # 主技能入口与协作约定
├── agents/
│   └── openai.yaml           # Codex / UI 发现与调用元信息
└── references/
    ├── design-outline.md     # 快速审阅提纲与原型隐含盲区清单
    └── completion-check.md   # 交付前四维完整性检查清单
```

---

## 🚀 安装与使用 (Installation & Usage)

本 Skill 遵循现代 Coding Agent 通用 Skill 规范，开箱即用支持 **Codex** 与 **Google Antigravity / Gemini**。

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

### 3. 日常使用方法
在会话中直接提供原型图或可交互链接，附带一句简短说明即可触发：
```text
按这份原型和说明完成这个功能。[粘贴原型图/链接 + 关键业务说明]
```
*(在 Codex 中也可通过 `$prototype-to-delivery` 显式唤起)*

---

## 📄 License

[MIT License](LICENSE)
