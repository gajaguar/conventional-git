from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

_SAMPLE_DIFF = (
    "diff --git a/src/conventional_git/cli/create.py b/src/conventional_git/cli/create.py\n"
    "--- a/src/conventional_git/cli/create.py\n"
    "+++ b/src/conventional_git/cli/create.py\n"
    "@@ -1 +1,2 @@\n"
    "+# comment\n"
)


def _env_without_llm_credentials() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("TYPESAFE_API_KEY", None)
    env.pop("OPENROUTER_API_KEY", None)
    return env


def test_app_help_exits_zero() -> None:
    # Arrange
    # Act
    completed = subprocess.run(
        [sys.executable, "-m", "conventional_git.cli.app", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    # Assert
    assert completed.returncode == 0
    assert "conventional-git" in completed.stdout


def test_check_commit_accepts_valid_message() -> None:
    # Arrange
    # Act
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "conventional_git.cli.app",
            "check",
            "commit",
            "--message",
            "feat(auth): add login",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # Assert
    assert completed.returncode == 0
    assert "ok" in completed.stdout


def test_check_commit_rejects_bad_type() -> None:
    # Arrange
    # Act
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "conventional_git.cli.app",
            "check",
            "commit",
            "--message",
            "banana: add login",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # Assert
    assert completed.returncode == 1
    assert "commit.type" in completed.stderr


def test_check_commit_rejects_attribution_trailer() -> None:
    # Arrange
    # Act
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "conventional_git.cli.app",
            "check",
            "commit",
            "--message",
            "feat: add login\n\n- bullet one\nCo-Authored-By: Claude <noreply@anthropic.com>",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # Assert
    assert completed.returncode == 1
    assert "commit.attribution" in completed.stderr


def test_check_branch_accepts_valid_name() -> None:
    # Arrange
    # Act
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "conventional_git.cli.app",
            "check",
            "branch",
            "--name",
            "feat/add-login",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # Assert
    assert completed.returncode == 0
    assert "ok" in completed.stdout


def test_check_branch_rejects_uppercase() -> None:
    # Arrange
    # Act
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "conventional_git.cli.app",
            "check",
            "branch",
            "--name",
            "BadName",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # Assert
    assert completed.returncode == 1
    assert "branch.format" in completed.stderr


def test_check_branch_accepts_main_trunk() -> None:
    # Arrange
    # Act
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "conventional_git.cli.app",
            "check",
            "branch",
            "--name",
            "main",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # Assert
    assert completed.returncode == 0
    assert "ok" in completed.stdout


def test_check_branch_accepts_extra_trunk_via_csv(tmp_path: Path) -> None:
    # Arrange
    trunks_csv = tmp_path / "branch-trunks.csv"
    trunks_csv.write_text("name,when_to_use\npython,Permanent language layer branch\n", encoding="utf-8")
    # Act
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "conventional_git.cli.app",
            "check",
            "branch",
            "--name",
            "python",
            "--trunks-csv",
            str(trunks_csv),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # Assert
    assert completed.returncode == 0
    assert "ok" in completed.stdout


def test_create_branch_outputs_normalized_name() -> None:
    # Arrange
    # Act
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "conventional_git.cli.app",
            "create",
            "branch",
            "--type",
            "feature",
            "--description",
            "Add OAuth Login",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # Assert
    assert completed.returncode == 0
    assert completed.stdout.strip() == "feature/add-oauth-login"


def test_create_suggest_falls_back_to_heuristic_without_credentials(tmp_path: Path) -> None:
    # Arrange
    diff_file = tmp_path / "sample.diff"
    diff_file.write_text(_SAMPLE_DIFF, encoding="utf-8")
    # Act
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "conventional_git.cli.app",
            "create",
            "suggest",
            "--diff-file",
            str(diff_file),
        ],
        capture_output=True,
        text=True,
        check=False,
        env=_env_without_llm_credentials(),
    )
    # Assert
    assert completed.returncode == 0
    assert "Falling back to the heuristic provider" in completed.stderr
    assert "type: chore" in completed.stdout


def test_create_suggest_with_explicit_jev_provider_fails_without_credentials(tmp_path: Path) -> None:
    # Arrange
    diff_file = tmp_path / "sample.diff"
    diff_file.write_text(_SAMPLE_DIFF, encoding="utf-8")
    # Act
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "conventional_git.cli.app",
            "create",
            "suggest",
            "--diff-file",
            str(diff_file),
            "--provider",
            "jev",
        ],
        capture_output=True,
        text=True,
        check=False,
        env=_env_without_llm_credentials(),
    )
    # Assert
    assert completed.returncode == 1
    assert "No TypeSafe or OpenRouter API key found" in completed.stderr


def test_auth_status_reports_no_credentials_when_unset() -> None:
    # Arrange
    # Act
    completed = subprocess.run(
        [sys.executable, "-m", "conventional_git.cli.app", "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
        env=_env_without_llm_credentials(),
    )
    # Assert
    assert completed.returncode == 0
    assert "No credentials found" in completed.stdout


def test_help_payload_is_json_shape() -> None:
    # Arrange
    # Act
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json; from conventional_git.mcp.server import describe_convention;"
                " print(json.dumps(describe_convention()))"
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # Assert
    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert "commit" in payload
    assert "branch" in payload
    assert "feat" in payload["commit"]["types"]
