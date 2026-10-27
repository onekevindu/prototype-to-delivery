#!/usr/bin/env python3
"""
Verification script for prototype-to-delivery skill.
Zero-dependency: uses only Python 3 standard library.
"""

import os
import re
import sys
import json
import subprocess

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def log_pass(msg):
    print(f"  {GREEN}✔{RESET} {msg}")


def log_fail(msg):
    print(f"  {RED}✘{RESET} {msg}")


def log_warn(msg):
    print(f"  {YELLOW}⚠{RESET} {msg}")


def parse_frontmatter(content):
    if not content.startswith("---"):
        return None
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return None
    data = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            data[k.strip()] = v
    return data


def verify_skill_folder(folder_path, label):
    print(f"\n{BLUE}[1/2] 检查 {label} 文件完整性:{RESET} ({folder_path})")
    if not os.path.isdir(folder_path):
        log_fail(f"目录不存在: {folder_path}")
        return False

    required_files = [
        ("SKILL.md", True),
        ("agents/openai.yaml", False),
        ("references/design-outline.md", True),
        ("references/completion-check.md", True),
        ("DESIGN_PHILOSOPHY.md", False),
    ]

    all_ok = True
    for rel_path, required in required_files:
        p = os.path.join(folder_path, rel_path)
        if os.path.exists(p):
            log_pass(f"文件存在: {rel_path}")
        else:
            if required:
                log_fail(f"缺少必要文件: {rel_path}")
                all_ok = False
            else:
                log_warn(f"可选文件不存在: {rel_path}")

    # Check SKILL.md frontmatter
    skill_file = os.path.join(folder_path, "SKILL.md")
    if os.path.exists(skill_file):
        with open(skill_file, "r", encoding="utf-8") as f:
            fm = parse_frontmatter(f.read())
        if fm and fm.get("name") == "prototype-to-delivery":
            log_pass("SKILL.md YAML 元信息有效 (name: prototype-to-delivery)")
        else:
            log_fail("SKILL.md YAML 元信息格式异常或缺少 name")
            all_ok = False

    return all_ok


def check_installations():
    print(f"\n{BLUE}[2/2] 检查全局安装状态:{RESET}")
    home = os.path.expanduser("~")

    targets = [
        ("Codex", os.path.join(home, ".codex/skills/prototype-to-delivery")),
        ("Google Antigravity", os.path.join(home, ".gemini/config/skills/prototype-to-delivery")),
    ]

    results = {}
    for name, path in targets:
        print(f"\n  👉 平台: {name}")
        if os.path.isdir(path):
            skill_md = os.path.join(path, "SKILL.md")
            if os.path.exists(skill_md):
                with open(skill_md, "r", encoding="utf-8") as f:
                    fm = parse_frontmatter(f.read())
                if fm and fm.get("name") == "prototype-to-delivery":
                    log_pass(f"已正确安装在: {path}")
                    results[name] = True
                    continue
            log_warn(f"目录存在但 SKILL.md 无效: {path}")
            results[name] = False
        else:
            log_warn(f"未安装至 {name} 默认路径: {path}")
            results[name] = False

    # Optional: check Codex CLI runtime app-server if present
    codex_cli = "/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex"
    if os.path.exists(codex_cli):
        try:
            print("\n  👉 测试 Codex App Server 实时注册协议:")
            proc = subprocess.Popen(
                [codex_cli, "app-server", "--stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            # init
            proc.stdin.write(json.dumps({"id": 1, "method": "initialize", "params": {"clientInfo": {"name": "verify", "version": "1.0"}}}) + "\n")
            proc.stdin.flush()
            proc.stdout.readline()
            proc.stdin.write(json.dumps({"method": "initialized"}) + "\n")
            proc.stdin.flush()

            # query
            proc.stdin.write(json.dumps({"id": 2, "method": "skills/list", "params": {"forceReload": True}}) + "\n")
            proc.stdin.flush()
            resp_line = proc.stdout.readline()
            resp = json.loads(resp_line)
            proc.terminate()

            found = False
            for entry in resp.get("result", {}).get("data", []):
                for s in entry.get("skills", []):
                    if s.get("name") == "prototype-to-delivery" and s.get("enabled"):
                        found = True
                        break
            if found:
                log_pass("Codex App Server 运行时识别状态: ENABLED (已激活)")
            else:
                log_warn("Codex App Server 运行时未在列表中返回该技能 (可能需要重启客户端)")
        except Exception as e:
            log_warn(f"无法完成 Codex App Server 协议测试: {e}")

    return results


def main():
    print(f"{BLUE}========================================{RESET}")
    print(f"{BLUE} prototype-to-delivery 安装与有效性验证 {RESET}")
    print(f"{BLUE}========================================{RESET}")

    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    repo_ok = verify_skill_folder(repo_dir, "当前仓库")
    install_results = check_installations()

    print(f"\n{BLUE}================ 验证汇总 ================{RESET}")
    if repo_ok:
        log_pass("本地项目源码完整无误")
    else:
        log_fail("本地项目缺少关键文件")

    for name, ok in install_results.items():
        if ok:
            log_pass(f"{name}: 安装成功且元数据有效")
        else:
            log_warn(f"{name}: 尚未安装或路径未就绪")

    print("\n💡 提示:")
    print("  • Codex: 在输入框输入 $ 检查是否出现 $prototype-to-delivery 自动联想项")
    print("  • Antigravity: 在对话中发送原型截图+说明，Agent 将自动阅读并遵循该 Skill 协作\n")


if __name__ == "__main__":
    main()
