from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_marketplace.py"
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"


class MarketplaceValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        shutil.copytree(ROOT / "heliox", self.repo / "heliox")
        shutil.copytree(ROOT / "skill-creator", self.repo / "skill-creator")
        for relative in (
            Path(".claude-plugin/marketplace.json"),
            Path(".agents/plugins/marketplace.json"),
        ):
            destination = self.repo / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        self._git("init", "--initial-branch=main")
        self._git("config", "user.name", "Marketplace Test")
        self._git("config", "user.email", "marketplace-test@example.com")
        self._git("config", "commit.gpgSign", "false")
        self._git("add", ".")
        self._git("commit", "-m", "initial marketplace")
        self.base_sha = self._git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def _set_version(self, version: str) -> None:
        for relative in (
            Path("heliox/.claude-plugin/plugin.json"),
            Path("heliox/.codex-plugin/plugin.json"),
        ):
            path = self.repo / relative
            document = json.loads(path.read_text(encoding="utf-8"))
            document["version"] = version
            path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        for relative in (
            Path(".claude-plugin/marketplace.json"),
            Path(".agents/plugins/marketplace.json"),
        ):
            path = self.repo / relative
            document = json.loads(path.read_text(encoding="utf-8"))
            entry = next(
                plugin for plugin in document["plugins"] if plugin["name"] == "heliox"
            )
            entry["version"] = version
            path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def _change_payload(self, marker: str) -> None:
        skill = self.repo / "heliox" / "skills" / "apps" / "SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8") + f"\n{marker}\n", encoding="utf-8"
        )

    def _commit_publish(self, version: str, marker: str = "Published change") -> None:
        self._set_version(version)
        self._change_payload(marker)
        self._git("add", ".")
        self._git("commit", "-m", f"publish {version}")

    def _run(
        self,
        *,
        base_ref: str | None = None,
        head_ref: str = "feature",
        head_repository: str = "heliohq/marketplace",
        event_name: str = "pull_request_target",
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                str(VALIDATOR),
                "--root",
                str(self.repo),
                "--base-ref",
                base_ref or self.base_sha,
                "--head-ref",
                head_ref,
                "--repository",
                "heliohq/marketplace",
                "--head-repository",
                head_repository,
                "--event-name",
                event_name,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_strictly_newer_same_repository_publish_passes(self) -> None:
        self._commit_publish("0.2.14")

        result = self._run(head_ref="heliox-publish-v0.2.14")

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_payload_change_without_version_increase_fails(self) -> None:
        self._change_payload("Unversioned change")
        self._git("add", ".")
        self._git("commit", "-m", "unversioned payload")

        result = self._run()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("strictly increase", result.stderr)

    def test_live_main_overrides_stale_event_base(self) -> None:
        self._git("switch", "--create", "heliox-publish-v0.2.14")
        self._commit_publish("0.2.14", "Older publication")
        self._git("branch", "stale-event-base", self.base_sha)
        self._git("switch", "main")
        self._commit_publish("0.2.15", "Newer publication")
        self._git("switch", "heliox-publish-v0.2.14")

        result = self._run(base_ref="main", head_ref="heliox-publish-v0.2.14")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("strictly increase", result.stderr)

    def test_publish_preserves_non_heliox_catalog_content(self) -> None:
        self._commit_publish("0.2.14")
        catalog_path = self.repo / ".claude-plugin" / "marketplace.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["plugins"] = [
            plugin for plugin in catalog["plugins"] if plugin["name"] != "skill-creator"
        ]
        catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "delete unrelated plugin")

        result = self._run(head_ref="heliox-publish-v0.2.14")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("may only replace", result.stderr)

    def test_publish_branch_rejects_extra_files_and_forks(self) -> None:
        self._commit_publish("0.2.14")
        (self.repo / "README.md").write_text("unrelated\n", encoding="utf-8")
        self._git("add", "README.md")
        self._git("commit", "-m", "unrelated file")

        extra = self._run(head_ref="heliox-publish-v0.2.14")
        fork = self._run(
            head_ref="heliox-publish-v0.2.14",
            head_repository="attacker/marketplace",
        )

        self.assertNotEqual(extra.returncode, 0)
        self.assertIn("outside its payload", extra.stderr)
        self.assertNotEqual(fork.returncode, 0)
        self.assertIn("same-repository", fork.stderr)

    def test_heliox_change_cannot_opt_out_with_feature_branch(self) -> None:
        self._commit_publish("0.2.14")

        same_repository = self._run(head_ref="feature")
        fork = self._run(head_ref="feature", head_repository="attacker/marketplace")

        self.assertNotEqual(same_repository.returncode, 0)
        self.assertIn("publish branch must be named", same_repository.stderr)
        self.assertNotEqual(fork.returncode, 0)
        self.assertIn("same-repository", fork.stderr)

    def test_non_heliox_catalog_update_does_not_require_heliox_bump(self) -> None:
        path = self.repo / ".claude-plugin" / "marketplace.json"
        catalog = json.loads(path.read_text(encoding="utf-8"))
        skill_creator = next(
            plugin for plugin in catalog["plugins"] if plugin["name"] == "skill-creator"
        )
        skill_creator["version"] = "0.1.1"
        path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "publish skill creator")

        result = self._run(head_ref="skill-creator-publish-v0.1.1")

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_artifact_and_apps_skills_are_required(self) -> None:
        shutil.rmtree(self.repo / "heliox" / "skills" / "artifact")

        result = self._run()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("preserve the artifact skill", result.stderr)

    def test_every_skill_directory_requires_complete_runtime_metadata(self) -> None:
        (self.repo / "heliox" / "skills" / "missing-skill").mkdir()

        missing = self._run()

        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("missing SKILL.md", missing.stderr)

        shutil.rmtree(self.repo / "heliox" / "skills" / "missing-skill")
        skill = self.repo / "heliox" / "skills" / "apps" / "SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8").replace(
                "user-invocable: false", "user-invocable: true", 1
            ),
            encoding="utf-8",
        )

        metadata = self._run()

        self.assertNotEqual(metadata.returncode, 0)
        self.assertIn("user-invocable: false", metadata.stderr)

    def test_codex_manifest_must_expose_loadable_skill_directory(self) -> None:
        path = self.repo / "heliox" / ".codex-plugin" / "plugin.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["skills"] = "./not-skills/"
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        result = self._run()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be ./skills/", result.stderr)

    def test_payload_rejects_non_regular_git_modes(self) -> None:
        link = self.repo / "heliox" / "skills" / "apps" / "linked-instructions"
        link.symlink_to("../artifact/SKILL.md")
        self._git("add", str(link.relative_to(self.repo)))
        self._git("commit", "-m", "add payload symlink")

        result = self._run()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("regular files only", result.stderr)

    def test_workflow_executes_live_main_control_against_exact_candidate(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("ref: refs/heads/main", workflow)
        self.assertIn("pull_request_target:", workflow)
        self.assertNotIn("\n  pull_request:\n", workflow)
        self.assertIn("path: control", workflow)
        self.assertIn("path: candidate", workflow)
        self.assertIn("refs/remotes/upstream/main", workflow)
        self.assertIn("control/scripts/validate_marketplace.py", workflow)
        self.assertIn("github.event.pull_request.number || github.ref", workflow)
        self.assertNotIn("github.event.pull_request.base.sha", workflow)


if __name__ == "__main__":
    unittest.main()
