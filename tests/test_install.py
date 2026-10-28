"""Exercise actual file replacement, backups and failure recovery in temporary homes."""

import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import install


class InstallLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "source"
        for relative in install.PAYLOAD:
            target = self.source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        self.dest = self.root / "host/skills/prototype-to-delivery"

    def run_install(self, action, *extra):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = install.main([action, "--source", str(self.source), "--dest", str(self.dest)] + list(extra))
        return code, output.getvalue()

    def set_version(self, version):
        (self.source / "VERSION").write_text(version + "\n", encoding="utf-8")

    def backups(self):
        return list((self.dest.parent.parent / "skill-backups/prototype-to-delivery").glob("*"))

    def install_first(self):
        code, output = self.run_install("install")
        self.assertEqual(code, 0, output)

    def test_first_install_copies_only_payload_and_repeated_install_is_noop(self):
        (self.source / "private.txt").write_text("Do not deploy", encoding="utf-8")
        self.install_first()
        self.assertEqual(set(install.inventory(self.dest)), set(install.PAYLOAD))
        before = (self.dest / install.STATE).stat().st_mtime_ns
        code, output = self.run_install("install")
        self.assertEqual(code, 0, output)
        self.assertIn("无需重复操作", output)
        self.assertEqual((self.dest / install.STATE).stat().st_mtime_ns, before)
        self.assertEqual(self.backups(), [])

    def test_upgrade_retains_full_backup_outside_discovery_root(self):
        self.install_first()
        original = install.inventory(self.dest)
        self.set_version("1.1.0")
        code, output = self.run_install("update")
        self.assertEqual(code, 0, output)
        self.assertEqual((self.dest / "VERSION").read_text().strip(), "1.1.0")
        self.assertEqual(len(self.backups()), 1)
        self.assertEqual(install.inventory(self.backups()[0]), original)
        self.assertNotIn(self.dest.parent, self.backups()[0].parents)
        self.assertEqual(self.run_install("status")[0], 0)

    def test_modified_missing_or_added_files_block_update_without_mutation(self):
        self.install_first()
        self.set_version("1.1.0")
        for change in ("edit", "delete", "add"):
            with self.subTest(change=change):
                if change == "edit":
                    (self.dest / "SKILL.md").write_text("Local customisation", encoding="utf-8")
                elif change == "delete":
                    (self.dest / "SKILL.md").unlink()
                else:
                    (self.dest / "custom.md").write_text("local", encoding="utf-8")
                before = install.inventory(self.dest)
                self.assertEqual(self.run_install("update")[0], 1)
                self.assertEqual(install.inventory(self.dest), before)
                self.assertEqual(self.backups(), [])

    def test_reinstall_preserves_manual_and_git_install_and_repairs_deleted_files(self):
        self.dest.mkdir(parents=True)
        (self.dest / "SKILL.md").write_text("Old custom skill", encoding="utf-8")
        (self.dest / ".git").mkdir()
        (self.dest / ".git/HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
        self.assertEqual(self.run_install("update")[0], 1)
        code, output = self.run_install("reinstall")
        self.assertEqual(code, 0, output)
        self.assertEqual((self.backups()[0] / "SKILL.md").read_text(), "Old custom skill")
        self.assertTrue((self.backups()[0] / ".git/HEAD").is_file())
        self.assertFalse((self.dest / ".git").exists())
        (self.dest / "SKILL.md").unlink()
        self.assertEqual(self.run_install("reinstall")[0], 0)
        self.assertTrue((self.dest / "SKILL.md").is_file())

    def test_update_rejects_downgrade_but_reinstall_can_roll_back(self):
        self.set_version("1.1.0")
        self.install_first()
        self.set_version("1.0.0")
        self.assertEqual(self.run_install("update")[0], 1)
        self.assertEqual(self.backups(), [])
        self.assertEqual(self.run_install("reinstall")[0], 0)
        self.assertEqual((self.dest / "VERSION").read_text().strip(), "1.0.0")

    def test_different_content_requires_update_and_a_higher_version(self):
        self.install_first()
        with (self.source / "SKILL.md").open("a") as stream:
            stream.write("\nChanged instructions\n")
        self.assertEqual(self.run_install("install")[0], 1)
        self.assertEqual(self.run_install("update")[0], 1)
        self.set_version("1.0.1")
        self.assertEqual(self.run_install("update")[0], 0)

    def test_bad_source_leaves_existing_install_untouched(self):
        self.install_first()
        before = install.inventory(self.dest)
        (self.source / "SKILL.md").write_text("Broken YAML", encoding="utf-8")
        self.assertEqual(self.run_install("reinstall")[0], 1)
        self.assertEqual(install.inventory(self.dest), before)
        self.assertEqual(self.backups(), [])

    def test_failed_copy_does_not_move_old_install(self):
        self.install_first()
        before = install.inventory(self.dest)
        with patch.object(install.shutil, "copy2", side_effect=OSError("disk full")):
            self.assertEqual(self.run_install("reinstall")[0], 1)
        self.assertEqual(install.inventory(self.dest), before)
        self.assertEqual(self.backups(), [])

    def test_failed_switch_restores_previous_install(self):
        self.install_first()
        before = install.inventory(self.dest)
        real_rename = Path.rename

        def fail_staged(source, target):
            if source.parent.name.startswith(".ptd-install-"):
                raise OSError("simulated replacement failure")
            return real_rename(source, target)

        with patch.object(Path, "rename", fail_staged):
            code, output = self.run_install("reinstall")
        self.assertEqual(code, 1, output)
        self.assertEqual(install.inventory(self.dest), before)
        self.assertEqual(self.run_install("status")[0], 0)
        self.assertEqual(self.backups(), [])

    def test_status_detects_tampering_and_corrupt_installation_record(self):
        self.install_first()
        (self.dest / "custom.txt").write_text("local", encoding="utf-8")
        self.assertEqual(self.run_install("status")[0], 1)
        for invalid in ("[]", "{", json.dumps({"schema": 1, "name": install.verify.SKILL_NAME,
                                               "version": "1.0.0", "files": {}})):
            (self.dest / install.STATE).write_text(invalid, encoding="utf-8")
            self.assertEqual(self.run_install("update")[0], 1)

    def test_existing_lock_stops_concurrent_install(self):
        self.dest.parent.mkdir(parents=True)
        lock = self.dest.parent / ".prototype-to-delivery.install.lock"
        lock.mkdir()
        self.assertEqual(self.run_install("install")[0], 1)
        self.assertTrue(lock.is_dir())
        self.assertFalse(self.dest.exists())

    def test_overlapping_source_and_destination_are_rejected(self):
        with self.assertRaises(install.InstallError):
            install.deploy(self.source, self.source, "reinstall")
        with self.assertRaises(install.InstallError):
            install.deploy(self.source, self.source / install.verify.SKILL_NAME, "install")

    def test_symbolic_link_install_is_not_replaced_or_followed(self):
        self.dest.parent.mkdir(parents=True)
        self.dest.symlink_to(self.source, target_is_directory=True)
        self.assertEqual(self.run_install("reinstall")[0], 1)
        self.assertTrue(self.dest.is_symlink())
        self.assertTrue((self.source / "SKILL.md").is_file())

    def test_platform_reuses_old_install_and_rejects_ambiguous_duplicates(self):
        legacy = self.root / ".codex/skills/prototype-to-delivery"
        modern = self.root / ".agents/skills/prototype-to-delivery"
        with patch.object(install.verify, "installation_candidates", return_value=[legacy, modern]), \
                patch.dict(os.environ, {"CODEX_HOME": ""}):
            self.assertEqual(install.destination("codex", None), modern)
            legacy.mkdir(parents=True)
            self.assertEqual(install.destination("codex", None), legacy)
            modern.mkdir(parents=True)
            with self.assertRaises(install.InstallError):
                install.destination("codex", None)

    def test_missing_install_update_fails_and_unrelated_folder_is_preserved(self):
        self.assertEqual(self.run_install("update")[0], 1)
        self.dest.mkdir(parents=True)
        (self.dest / "important.txt").write_text("keep", encoding="utf-8")
        self.assertEqual(self.run_install("reinstall")[0], 1)
        self.assertEqual((self.dest / "important.txt").read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
