#!/usr/bin/env python3
"""Validate skill files and explicitly requested installation checks."""

import argparse
import json
import math
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import time

try:
    import yaml
except ImportError:
    yaml = None


SKILL_NAME = "prototype-to-delivery"
PLATFORMS = ("codex", "antigravity", "antigravity-cli", "gemini-cli")


class VerificationError(Exception):
    """A requested check could not establish success."""


def parse_frontmatter(content):
    """Parse actual YAML and validate fields needed for skill discovery."""
    if yaml is None:
        raise VerificationError("缺少 PyYAML；请运行 python3 -m pip install -r requirements.txt")
    lines = content.splitlines()
    if not lines or lines[0] != "---":
        raise VerificationError("SKILL.md 必须以 YAML frontmatter 开始")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise VerificationError("SKILL.md 缺少 frontmatter 结束标记")
    try:
        metadata = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as exc:
        raise VerificationError("SKILL.md YAML 无效: {}".format(exc))
    if not isinstance(metadata, dict):
        raise VerificationError("SKILL.md frontmatter 必须为映射")
    if metadata.get("name") != SKILL_NAME:
        raise VerificationError("name 必须为 {}".format(SKILL_NAME))
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        raise VerificationError("description 必须为非空字符串")
    if len(description) > 1024:
        raise VerificationError("description 不能超过 1024 个字符")
    return metadata


def verify_skill_folder(folder_path, label="skill"):
    folder = Path(folder_path)
    if yaml is None:
        print("FAIL 缺少 PyYAML；请运行 python3 -m pip install -r requirements.txt")
        return False
    required = ("SKILL.md", "references/design-outline.md", "references/completion-check.md")
    errors = []
    for relative in required:
        if not (folder / relative).is_file():
            errors.append("缺少必要文件: {}".format(relative))
    if (folder / "SKILL.md").is_file():
        try:
            parse_frontmatter((folder / "SKILL.md").read_text(encoding="utf-8"))
        except (OSError, UnicodeError, VerificationError) as exc:
            errors.append(str(exc))
    interface = folder / "agents/openai.yaml"
    if interface.exists():
        try:
            data = yaml.safe_load(interface.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                errors.append("agents/openai.yaml 必须为 YAML 映射")
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            errors.append("agents/openai.yaml 无效: {}".format(exc))
    for error in errors:
        print("FAIL {}: {}".format(label, error))
    if not errors:
        print("PASS {}: 文件与 YAML 元数据有效 ({})".format(label, folder))
    return not errors


def installation_candidates(platform, home=None, environ=None):
    home = Path.home() if home is None else Path(home)
    environ = os.environ if environ is None else environ
    if platform == "codex":
        codex_home = Path(environ.get("CODEX_HOME") or home / ".codex").expanduser()
        roots = [codex_home / "skills", home / ".agents/skills"]
    elif platform == "antigravity":
        roots = [home / ".gemini/config/skills"]
    elif platform == "antigravity-cli":
        roots = [home / ".gemini/antigravity-cli/skills"]
    elif platform == "gemini-cli":
        roots = [home / ".gemini/skills", home / ".agents/skills"]
    else:
        raise ValueError("Unknown platform: {}".format(platform))
    return list(dict.fromkeys(root / SKILL_NAME for root in roots))


def find_codex_cli(explicit=None):
    if explicit:
        candidate = shutil.which(explicit)
        if candidate:
            return candidate
        raise VerificationError("找不到可执行文件: {}".format(explicit))
    candidate = shutil.which("codex")
    if candidate:
        return candidate
    bundled = Path("/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex")
    if bundled.is_file() and os.access(str(bundled), os.X_OK):
        return str(bundled)
    raise VerificationError("未找到 Codex CLI；请加入 PATH 或使用 --codex-cli 指定")


def verify_codex_runtime(executable, cwd, skill_files, timeout=10.0):
    """Read skills/list with a deadline and always reap the child process."""
    expected = {str(Path(path).resolve()) for path in skill_files}
    messages = queue.Queue()
    deadline = time.monotonic() + timeout
    proc = subprocess.Popen(
        [str(executable), "app-server", "--stdio"],
        cwd=str(cwd), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True, encoding="utf-8", bufsize=1,
    )

    def read_stdout():
        try:
            for line in proc.stdout:
                messages.put(line)
        except (OSError, UnicodeError) as exc:
            messages.put(exc)
        finally:
            messages.put(None)

    reader = threading.Thread(target=read_stdout, daemon=True)
    reader.start()

    def send(message):
        if time.monotonic() >= deadline:
            raise VerificationError("Codex 运行时检查超时")
        proc.stdin.write(json.dumps(message) + "\n")
        proc.stdin.flush()

    def receive(request_id):
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise VerificationError("Codex 运行时检查超时")
            try:
                raw = messages.get(timeout=remaining)
            except queue.Empty:
                raise VerificationError("Codex 运行时检查超时")
            if raw is None:
                raise VerificationError("Codex app-server 在返回结果前结束")
            if isinstance(raw, Exception):
                raise VerificationError("读取 Codex 响应失败: {}".format(raw))
            try:
                message = json.loads(raw)
            except (ValueError, TypeError):
                raise VerificationError("Codex app-server 返回了无效 JSON")
            if not isinstance(message, dict):
                raise VerificationError("Codex app-server 响应必须为对象")
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise VerificationError("Codex 请求失败: {}".format(message["error"]))
            result = message.get("result")
            if not isinstance(result, dict):
                raise VerificationError("Codex 响应缺少有效 result")
            return result

    try:
        send({"id": 1, "method": "initialize", "params": {
            "clientInfo": {"name": "skill-verifier", "version": "1.0"}}})
        receive(1)
        send({"method": "initialized"})
        send({"id": 2, "method": "skills/list", "params": {
            "cwds": [str(Path(cwd).resolve())], "forceReload": True}})
        result = receive(2)
        entries = result.get("data")
        if not isinstance(entries, list):
            raise VerificationError("skills/list 未返回有效 data 列表")
        for entry in entries:
            if not isinstance(entry, dict):
                raise VerificationError("skills/list data 项必须为对象")
            skills = entry.get("skills", [])
            if not isinstance(skills, list):
                raise VerificationError("skills/list skills 必须为列表")
            for skill in skills:
                if not isinstance(skill, dict):
                    continue
                path = skill.get("path")
                if (skill.get("name") == SKILL_NAME and skill.get("enabled") is True
                        and isinstance(path, str) and str(Path(path).resolve()) in expected):
                    return path
        raise VerificationError("Codex 未识别并启用所检查路径的 skill；同名其他路径不算通过")
    except (OSError, UnicodeError) as exc:
        raise VerificationError("Codex 运行时通信失败: {}".format(exc))
    finally:
        if proc.poll() is None:
            proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=1)
        reader.join(timeout=1)
        for stream in (proc.stdin, proc.stdout):
            try:
                stream.close()
            except OSError:
                pass


def positive_timeout(value):
    try:
        result = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("timeout 必须为正有限秒数")
    if not math.isfinite(result) or result <= 0:
        raise argparse.ArgumentTypeError("timeout 必须为正有限秒数")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="待校验的 skill 目录，默认当前仓库")
    parser.add_argument("--platform", choices=PLATFORMS, help="额外检查所选平台的安装文件")
    parser.add_argument("--runtime", action="store_true", help="检查 Codex 是否实际识别并启用安装文件")
    parser.add_argument("--codex-cli", help="Codex 可执行文件路径或命令名")
    parser.add_argument("--timeout", type=positive_timeout, default=10.0, help="运行时检查总超时秒数，默认 10")
    args = parser.parse_args(argv)
    if args.runtime and args.platform != "codex":
        parser.error("--runtime 需要 --platform codex；其他平台请在宿主中核验运行时")
    if args.codex_cli and not args.runtime:
        parser.error("--codex-cli 需要同时使用 --runtime")
    if yaml is None:
        print("ERROR 缺少 PyYAML；请运行 python3 -m pip install -r requirements.txt", file=sys.stderr)
        return 2
    args.path = args.path.expanduser().resolve()
    if not verify_skill_folder(args.path, "当前 skill"):
        return 1
    if args.platform:
        candidates = installation_candidates(args.platform)
        installed = [path for path in candidates if path.exists()]
        if not installed:
            print("FAIL 未找到 {} 安装文件；检查路径: {}".format(
                args.platform, ", ".join(str(path) for path in candidates)))
            return 1
        valid = [verify_skill_folder(path, args.platform) for path in installed]
        if not all(valid):
            return 1
        if args.runtime:
            try:
                executable = find_codex_cli(args.codex_cli)
                path = verify_codex_runtime(executable, args.path,
                                            [p / "SKILL.md" for p in installed], args.timeout)
            except (VerificationError, OSError) as exc:
                print("FAIL {}".format(exc))
                return 1
            print("PASS Codex 运行时已识别且启用: {}".format(path))
        else:
            print("INFO 仅检查安装文件；尚未验证宿主运行时发现或启用状态")
    else:
        print("INFO 仅检查本地 skill 文件；未检查平台安装或运行时")
    print("PASS 本次明确请求的检查均通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
