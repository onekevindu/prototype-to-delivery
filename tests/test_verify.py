"""Regression checks for metadata validation, exit codes and runtime probing."""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/verify.py"
SPEC = importlib.util.spec_from_file_location("skill_verify", SCRIPT)
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


def create_skill(folder, frontmatter=None):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "references").mkdir(exist_ok=True)
    for name in ("design-outline.md", "completion-check.md"):
        (folder / "references" / name).write_text("# Reference\n", encoding="utf-8")
    body = frontmatter or "name: prototype-to-delivery\ndescription: Valid test skill"
    (folder / "SKILL.md").write_text("---\n" + body + "\n---\n# Test\n", encoding="utf-8")
    return folder


class MetadataAndCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = create_skill(self.root / "source")

    def run_main(self, *arguments):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = verify.main(["--path", str(self.skill)] + list(arguments))
        return result, output.getvalue()

    def test_rejects_missing_wrong_type_and_malformed_description(self):
        for field in ("", "description: null", "description: false", "description: 123",
                      "description: []", "description: ''", "description: '   '",
                      "description: [unterminated"):
            with self.subTest(field=field):
                content = "---\nname: prototype-to-delivery\n" + field + "\n---\n"
                with self.assertRaises(verify.VerificationError):
                    verify.parse_frontmatter(content)

    def test_accepts_real_yaml_multiline_and_quoted_values(self):
        result = verify.parse_frontmatter(
            "---\nname: 'prototype-to-delivery'\ndescription: >-\n  First line:\n  second line\n---\n")
        self.assertEqual(result["description"], "First line: second line")

    def test_rejects_wrong_name_non_mapping_and_missing_delimiters(self):
        for content in ("# No frontmatter", "---\nname: prototype-to-delivery",
                        "---\n- item\n---\n", "---\nname: another\ndescription: Fine\n---\n"):
            with self.subTest(content=content), self.assertRaises(verify.VerificationError):
                verify.parse_frontmatter(content)

    def test_missing_required_reference_fails(self):
        (self.skill / "references/design-outline.md").unlink()
        result, output = self.run_main()
        self.assertEqual(result, 1)
        self.assertIn("缺少必要文件", output)

    def test_invalid_optional_ui_yaml_fails(self):
        (self.skill / "agents").mkdir()
        (self.skill / "agents/openai.yaml").write_text("interface: [broken", encoding="utf-8")
        result, output = self.run_main()
        self.assertEqual(result, 1)
        self.assertIn("agents/openai.yaml 无效", output)

    def test_default_does_not_probe_installations_or_launch_processes(self):
        with patch.object(verify, "installation_candidates") as locations, \
                patch.object(verify.subprocess, "Popen") as process:
            result, output = self.run_main()
        self.assertEqual(result, 0)
        locations.assert_not_called()
        process.assert_not_called()
        self.assertIn("未检查平台安装或运行时", output)

    def test_missing_selected_installation_returns_failure(self):
        with patch.object(verify, "installation_candidates", return_value=[self.root / "missing"]):
            result, output = self.run_main("--platform", "gemini-cli")
        self.assertEqual(result, 1)
        self.assertIn("未找到", output)

    def test_installation_only_does_not_claim_runtime_success(self):
        with patch.object(verify, "installation_candidates", return_value=[self.skill]):
            result, output = self.run_main("--platform", "antigravity")
        self.assertEqual(result, 0)
        self.assertIn("尚未验证宿主运行时", output)

    def test_runtime_failure_propagates_to_exit_code(self):
        with patch.object(verify, "installation_candidates", return_value=[self.skill]), \
                patch.object(verify, "find_codex_cli", return_value="codex"), \
                patch.object(verify, "verify_codex_runtime", side_effect=verify.VerificationError("not found")):
            result, output = self.run_main("--platform", "codex", "--runtime")
        self.assertEqual(result, 1)
        self.assertIn("FAIL not found", output)
        self.assertNotIn("明确请求的检查均通过", output)

    def test_missing_dependency_is_actionable_configuration_error(self):
        with patch.object(verify, "yaml", None):
            result, output = self.run_main()
        self.assertEqual(result, 2)
        self.assertIn("pip install PyYAML", output)

    def test_bad_runtime_combinations_and_timeouts_are_usage_errors(self):
        cases = [("--runtime",), ("--platform", "gemini-cli", "--runtime"),
                 ("--codex-cli", "codex"), ("--timeout", "0"), ("--timeout", "-1"),
                 ("--timeout", "nan"), ("--timeout", "inf"), ("--timeout", "text")]
        for arguments in cases:
            with self.subTest(arguments=arguments), self.assertRaises(SystemExit) as raised:
                self.run_main(*arguments)
            self.assertEqual(raised.exception.code, 2)

    def test_cli_process_uses_nonzero_exit_code_for_failed_validation(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--path", str(self.root / "missing")],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("FAIL", result.stdout)

    def test_platform_locations_are_distinct_and_respect_codex_home(self):
        base = self.root
        name = "prototype-to-delivery"
        self.assertEqual(verify.installation_candidates("antigravity", base, {}),
                         [base / ".gemini/config/skills" / name])
        self.assertEqual(verify.installation_candidates("antigravity-cli", base, {}),
                         [base / ".gemini/antigravity-cli/skills" / name])
        self.assertEqual(verify.installation_candidates("gemini-cli", base, {}),
                         [base / ".gemini/skills" / name, base / ".agents/skills" / name])
        self.assertEqual(verify.installation_candidates("codex", base, {}),
                         [base / ".codex/skills" / name, base / ".agents/skills" / name])
        self.assertEqual(verify.installation_candidates("codex", base, {"CODEX_HOME": str(base / "custom")}),
                         [base / "custom/skills" / name, base / ".agents/skills" / name])


FAKE_SERVER = '''import json, signal, sys, time
mode = MODE
path = PATH
if mode == "stubborn":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
def send(value):
    print(json.dumps(value), flush=True)
for line in sys.stdin:
    message = json.loads(line)
    if message.get("method") == "initialize":
        if mode == "eof":
            break
        send({"method": "server/notice", "params": {}})
        send({"id": 99, "result": {"unrelated": True}})
        send({"id": 1, "result": {}})
    elif message.get("method") == "skills/list":
        if mode in ("timeout", "stubborn"):
            time.sleep(30)
        elif mode == "wrong-id":
            send({"id": 77, "result": {"data": []}})
            time.sleep(30)
        elif mode == "malformed":
            print("not JSON", flush=True)
        elif mode == "rpc-error":
            send({"id": 2, "error": {"code": -1, "message": "Unavailable"}})
        else:
            send({"method": "server/notice", "params": {}})
            skill = {"name": "prototype-to-delivery", "enabled": mode != "disabled", "path": path}
            if mode == "wrong-path":
                skill["path"] = path + ".elsewhere"
            skills = [] if mode == "not-found" else [skill]
            send({"id": 2, "result": {"data": [{"skills": skills}]}})
'''


class RuntimeProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill_file = create_skill(self.root / "installed") / "SKILL.md"

    def probe(self, mode, timeout=2.0):
        server = self.root / "fake_server.py"
        source = FAKE_SERVER.replace("MODE", repr(mode)).replace("PATH", repr(str(self.skill_file)))
        server.write_text(source, encoding="utf-8")
        real_popen = subprocess.Popen
        children = []

        def start_fake(command, **kwargs):
            child = real_popen([sys.executable, str(server)], **kwargs)
            children.append(child)
            return child

        try:
            with patch.object(verify.subprocess, "Popen", side_effect=start_fake):
                return verify.verify_codex_runtime("fake-codex", self.root, [self.skill_file], timeout)
        finally:
            self.assertEqual(len(children), 1)
            for child in children:
                self.assertIsNotNone(child.poll(), "Child process was not reaped")
                self.assertTrue(child.stdin.closed)
                self.assertTrue(child.stdout.closed)

    def test_enabled_expected_path_survives_notifications_and_unrelated_ids(self):
        self.assertEqual(self.probe("enabled"), str(self.skill_file))

    def test_disabled_missing_and_other_path_are_not_success(self):
        for mode in ("disabled", "not-found", "wrong-path"):
            with self.subTest(mode=mode), self.assertRaises(verify.VerificationError):
                self.probe(mode)

    def test_rpc_errors_malformed_json_and_eof_fail_and_cleanup(self):
        for mode in ("rpc-error", "malformed", "eof"):
            with self.subTest(mode=mode), self.assertRaises(verify.VerificationError):
                self.probe(mode)

    def test_timeout_and_wrong_id_are_bounded_and_cleanup(self):
        for mode in ("timeout", "wrong-id"):
            started = time.monotonic()
            with self.subTest(mode=mode), self.assertRaisesRegex(verify.VerificationError, "超时"):
                self.probe(mode, timeout=0.2)
            self.assertLess(time.monotonic() - started, 3)

    @unittest.skipIf(os.name == "nt", "SIGTERM ignore is a POSIX fixture")
    def test_uncooperative_process_is_killed_and_reaped(self):
        started = time.monotonic()
        with self.assertRaisesRegex(verify.VerificationError, "超时"):
            self.probe("stubborn", timeout=0.5)
        self.assertLess(time.monotonic() - started, 4)


if __name__ == "__main__":
    unittest.main()
