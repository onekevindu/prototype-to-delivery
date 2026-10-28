"""Run the shell installer with a PATH that contains no Python, Node or package manager."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/install.sh"
PAYLOAD = ("SKILL.md", "references/design-outline.md", "references/completion-check.md",
           "agents/openai.yaml", "LICENSE", "VERSION")
COMMANDS = ("basename", "dirname", "cat", "find", "cksum", "sort", "cmp", "mkdir",
            "mktemp", "cp", "mv", "rm", "rmdir", "date")


@unittest.skipUnless(Path("/bin/bash").is_file(), "macOS/Linux shell installer")
class ShellInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ptd-shell-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "source with spaces"
        self.dest = self.root / "host with spaces/skills/prototype-to-delivery"
        for relative in PAYLOAD:
            target = self.source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        self.set_version("1.0.0")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for command in COMMANDS:
            executable = shutil.which(command)
            self.assertIsNotNone(executable, command)
            (self.bin / command).symlink_to(executable)
        self.env = dict(os.environ, PATH=str(self.bin))

    def set_version(self, version):
        (self.source / "VERSION").write_text(version + "\n", encoding="utf-8")

    def run_install(self, action, success=True, *extra):
        result = subprocess.run(["/bin/bash", str(SCRIPT), action, "--source", str(self.source),
                                 "--dest", str(self.dest)] + list(extra), env=self.env,
                                capture_output=True, text=True, timeout=10)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def backups(self):
        return list((self.dest.parent.parent / "skill-backups/prototype-to-delivery").glob("*"))

    def snapshot(self, folder):
        return {str(p.relative_to(folder)): p.read_bytes() for p in folder.rglob("*") if p.is_file()}

    def test_install_status_and_idempotency_with_no_python_on_path(self):
        for command in ("python", "python3", "pip", "pip3", "node", "npm"):
            self.assertIsNone(shutil.which(command, path=self.env["PATH"]))
        self.run_install("install")
        self.run_install("status")
        before = self.snapshot(self.dest)
        result = self.run_install("install")
        self.assertIn("Already installed", result.stdout)
        self.assertEqual(self.snapshot(self.dest), before)
        self.assertEqual(self.backups(), [])
        self.assertEqual(set(before), set(PAYLOAD) | {".installation.cksum"})

    def test_update_creates_complete_backup_outside_skills_directory(self):
        self.run_install("install")
        before = self.snapshot(self.dest)
        self.set_version("1.0.1")
        self.run_install("update")
        self.assertEqual((self.dest / "VERSION").read_text(), "1.0.1\n")
        self.assertEqual(len(self.backups()), 1)
        self.assertEqual(self.snapshot(self.backups()[0]), before)
        self.assertNotIn(self.dest.parent, self.backups()[0].parents)
        self.run_install("status")

    def test_local_edits_additions_and_deletions_block_update(self):
        self.run_install("install")
        self.set_version("1.0.1")
        for change in ("edit", "delete", "add"):
            with self.subTest(change=change):
                if change == "edit":
                    (self.dest / "SKILL.md").write_text("Local custom content", encoding="utf-8")
                elif change == "delete":
                    (self.dest / "SKILL.md").unlink()
                else:
                    (self.dest / "local.txt").write_text("keep", encoding="utf-8")
                before = self.snapshot(self.dest)
                self.run_install("update", False)
                self.run_install("status", False)
                self.assertEqual(self.snapshot(self.dest), before)
                self.assertEqual(self.backups(), [])

    def test_reinstall_migrates_python_and_manual_installations_with_backup(self):
        self.dest.mkdir(parents=True)
        (self.dest / "SKILL.md").write_text("User edits", encoding="utf-8")
        (self.dest / ".installation.json").write_text('{"schema": 1}', encoding="utf-8")
        (self.dest / ".git").mkdir()
        (self.dest / ".git/HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
        before = self.snapshot(self.dest)
        self.run_install("update", False)
        self.run_install("reinstall")
        self.assertEqual(self.snapshot(self.backups()[0]), before)
        self.assertFalse((self.dest / ".installation.json").exists())
        self.run_install("status")

    def test_reinstall_repairs_deleted_file_and_keeps_modified_content_in_backup(self):
        self.run_install("install")
        (self.dest / "SKILL.md").unlink()
        (self.dest / "local.txt").write_text("keep", encoding="utf-8")
        before = self.snapshot(self.dest)
        self.run_install("reinstall")
        self.assertTrue((self.dest / "SKILL.md").is_file())
        self.assertEqual(self.snapshot(self.backups()[0]), before)

    def test_downgrade_requires_reinstall(self):
        self.set_version("1.1.0")
        self.run_install("install")
        self.set_version("1.0.1")
        self.run_install("update", False)
        self.run_install("reinstall")
        self.assertEqual((self.dest / "VERSION").read_text(), "1.0.1\n")

    def test_same_version_changed_content_is_not_silently_updated(self):
        self.run_install("install")
        with (self.source / "SKILL.md").open("a") as stream:
            stream.write("\nUpdated content\n")
        self.run_install("install", False)
        self.run_install("update", False)
        self.assertEqual(self.backups(), [])

    def test_incomplete_source_and_unrelated_destination_are_preserved(self):
        self.dest.mkdir(parents=True)
        (self.dest / "important.txt").write_text("keep", encoding="utf-8")
        self.run_install("reinstall", False)
        self.assertEqual((self.dest / "important.txt").read_text(), "keep")
        (self.source / "references/design-outline.md").unlink()
        self.run_install("reinstall", False)
        self.assertEqual(self.backups(), [])

    def test_lock_and_symlink_destinations_block_mutation(self):
        self.dest.parent.mkdir(parents=True)
        lock = self.dest.parent / ".prototype-to-delivery.install.lock"
        lock.mkdir()
        self.run_install("install", False)
        self.assertTrue(lock.exists())
        lock.rmdir()
        self.dest.symlink_to(self.source, target_is_directory=True)
        self.run_install("reinstall", False)
        self.assertTrue(self.dest.is_symlink())

    def fake_command(self, name, body):
        path = self.bin / name
        path.unlink()
        path.write_text("#!/bin/bash\n" + body, encoding="utf-8")
        path.chmod(0o755)

    def test_copy_failure_leaves_current_installation_untouched(self):
        self.run_install("install")
        before = self.snapshot(self.dest)
        self.fake_command("cp", "exit 23\n")
        self.run_install("reinstall", False)
        self.assertEqual(self.snapshot(self.dest), before)
        self.assertEqual(self.backups(), [])

    def test_failed_switch_restores_previous_installation(self):
        self.run_install("install")
        before = self.snapshot(self.dest)
        self.fake_command("mv", 'case "$1" in */new) exit 24 ;; esac\nexec /bin/mv "$@"\n')
        self.run_install("reinstall", False)
        self.assertEqual(self.snapshot(self.dest), before)
        self.assertEqual(self.backups(), [])
        self.run_install("status")

    def test_status_does_not_require_source_or_write_installation(self):
        self.run_install("install")
        before = self.snapshot(self.dest)
        shutil.rmtree(self.source)
        self.run_install("status")
        self.assertEqual(self.snapshot(self.dest), before)

    def test_invalid_version_or_overlapping_source_is_rejected(self):
        for version in ("v1.0.0", "01.0.0", "1.0", "1.0.0; echo unsafe"):
            self.set_version(version)
            self.run_install("install", False)
            self.assertFalse(self.dest.exists())
        self.set_version("1.0.0")
        result = subprocess.run(["/bin/bash", str(SCRIPT), "reinstall", "--source", str(self.source),
                                 "--dest", str(self.source / "prototype-to-delivery")],
                                capture_output=True, text=True, env=self.env, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.source / "prototype-to-delivery").exists())


if __name__ == "__main__":
    unittest.main()
