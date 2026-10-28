#!/usr/bin/env python3
"""Deploy a local, validated skill package; never fetch or change host settings."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid

import verify


STATE = ".installation.json"
PAYLOAD = ("SKILL.md", "references/design-outline.md", "references/completion-check.md",
           "agents/openai.yaml", "LICENSE", "VERSION")


class InstallError(Exception):
    pass


def version_tuple(value):
    if not isinstance(value, str) or not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value):
        raise InstallError("VERSION 必须是 MAJOR.MINOR.PATCH，例如 1.0.0")
    return tuple(map(int, value.split(".")))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder).as_posix()
        if path.is_symlink():
            raise InstallError("安装文件中含符号链接，需要人工处理: " + relative)
        if path.is_file() and relative != STATE and path.name != ".DS_Store":
            result[relative] = digest(path)
    return result


def package(source):
    if not verify.verify_skill_folder(source, "安装源"):
        raise InstallError("安装源校验失败")
    files = {}
    for relative in PAYLOAD:
        path = source / relative
        if not path.is_file() or path.is_symlink() or source not in path.resolve().parents:
            raise InstallError("安装源缺少文件或包含外部链接: " + relative)
        files[relative] = digest(path)
    version = (source / "VERSION").read_text(encoding="utf-8").strip()
    version_tuple(version)
    return {"schema": 1, "name": verify.SKILL_NAME, "version": version, "files": files}


def installed_state(dest):
    try:
        state = json.loads((dest / STATE).read_text(encoding="utf-8"))
        if not isinstance(state, dict) or state.get("schema") != 1 or state.get("name") != verify.SKILL_NAME:
            raise ValueError("不匹配的安装记录")
        version_tuple(state.get("version"))
        files = state.get("files")
        if not isinstance(files, dict) or not files or not all(
                isinstance(k, str) and isinstance(v, str) and re.fullmatch(r"[a-f0-9]{64}", v)
                for k, v in files.items()):
            raise ValueError("无效的文件摘要")
        if (dest / "VERSION").read_text(encoding="utf-8").strip() != state["version"]:
            raise ValueError("版本记录与 VERSION 不一致")
        return state
    except (OSError, ValueError, InstallError) as exc:
        raise InstallError("旧安装、损坏或未受管理的目录；请用 reinstall 备份后重新安装 ({})".format(exc))


def destination(platform, explicit):
    if explicit:
        dest = explicit.expanduser().absolute()
    else:
        candidates = verify.installation_candidates(platform)
        existing = [p for p in candidates if p.exists() or p.is_symlink()]
        if len(existing) > 1:
            raise InstallError("发现多个安装位置，请用 --dest 明确选择，并检查宿主是否重复发现: "
                               + ", ".join(map(str, existing)))
        # Reuse an existing legacy install; new Codex installations follow current docs.
        if existing:
            dest = existing[0]
        elif platform == "codex" and not os.environ.get("CODEX_HOME"):
            dest = candidates[-1]
        else:
            dest = candidates[0]
    if dest.name != verify.SKILL_NAME:
        raise InstallError("--dest 必须指向名为 prototype-to-delivery 的完整安装目录")
    if dest.is_symlink():
        raise InstallError("目标是符号链接；请在链接源更新，或先人工迁移为普通安装目录")
    return dest.resolve()


@contextmanager
def lock_destination(dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    lock = dest.parent / ("." + verify.SKILL_NAME + ".install.lock")
    try:
        lock.mkdir()
    except FileExistsError:
        raise InstallError("另一安装操作可能正在执行；若上次进程异常退出，确认其已结束后移除锁: " + str(lock))
    try:
        yield
    finally:
        lock.rmdir()


def deploy(source, dest, action):
    if source == dest or source in dest.parents or dest in source.parents:
        raise InstallError("源码目录与安装目录必须分开，且不能互相包含")
    state = package(source)
    with lock_destination(dest):
        exists = dest.exists()
        if exists and not dest.is_dir():
            raise InstallError("目标存在但不是目录")
        if action == "update" and not exists:
            raise InstallError("尚未安装，请先使用 install")
        if exists and action != "reinstall":
            current = installed_state(dest)
            if inventory(dest) != current["files"]:
                raise InstallError("安装目录有本地修改；update 不会覆盖。请保留修改，或用 reinstall 备份后替换")
            if current == state:
                print("PASS 已安装相同版本和内容，无需重复操作: " + state["version"])
                return None
            if action == "install":
                raise InstallError("已安装不同内容，请使用 update 或 reinstall")
            if version_tuple(state["version"]) <= version_tuple(current["version"]):
                raise InstallError("update 只接受更高版本；同版本修复或回退请显式使用 reinstall")
        if exists and action == "reinstall" and not ((dest / "SKILL.md").is_file() or (dest / STATE).is_file()):
            raise InstallError("目标不像 Skill 安装，拒绝替换无关目录")

        # Stage on the same filesystem. The old installation is untouched until staging succeeds.
        with tempfile.TemporaryDirectory(prefix=".ptd-install-", dir=str(dest.parent)) as temporary:
            staged = Path(temporary) / verify.SKILL_NAME
            staged.mkdir()
            for relative in PAYLOAD:
                target = staged / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source / relative, target)
            if inventory(staged) != state["files"]:
                raise InstallError("安装源在复制期间改变，未修改旧安装；请重试")
            (staged / STATE).write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            backup = None
            if exists:
                # Outside the skills discovery directory, so backups are not duplicate skills.
                backups = dest.parent.parent / "skill-backups" / verify.SKILL_NAME
                backups.mkdir(parents=True, exist_ok=True)
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                backup = backups / (stamp + "-" + uuid.uuid4().hex[:8])
                dest.rename(backup)
            try:
                staged.rename(dest)
            except BaseException:
                if backup is not None:
                    backup.rename(dest)
                raise
            print("PASS {} {}: {}".format(action, state["version"], dest))
            if backup is not None:
                print("INFO 旧安装完整备份: " + str(backup))
            print("INFO 文件已部署；请在宿主中刷新并核对实际发现状态")
            return backup


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "update", "reinstall", "status"))
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="本地源码目录；固定版本请先检出相应 Git 标签")
    location = parser.add_mutually_exclusive_group(required=True)
    location.add_argument("--platform", choices=verify.PLATFORMS)
    location.add_argument("--dest", type=Path, help="完整安装目录，末级为 prototype-to-delivery")
    args = parser.parse_args(argv)
    if args.action != "status" and verify.yaml is None:
        print("ERROR 缺少 PyYAML；请运行 python3 -m pip install -r requirements.txt", file=sys.stderr)
        return 2
    try:
        dest = destination(args.platform, args.dest)
        if args.action == "status":
            if not dest.is_dir():
                raise InstallError("未找到安装: " + str(dest))
            state = installed_state(dest)
            print("INFO 已安装版本 {}: {}".format(state["version"], dest))
            if inventory(dest) != state["files"]:
                raise InstallError("安装文件存在本地修改或缺失")
            print("PASS 安装文件与记录一致；未检查宿主运行时")
        else:
            deploy(args.source.expanduser().resolve(), dest, args.action)
        return 0
    except (InstallError, OSError, UnicodeError) as exc:
        print("FAIL {}".format(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
