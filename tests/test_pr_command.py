from __future__ import annotations

import json
from pathlib import Path

from conventional_git.cli import pr_command


def test_payload_cwd_returns_the_cwd_string() -> None:
    # Arrange
    raw = json.dumps({"cwd": "/work", "tool_input": {"command": "x"}})
    # Act
    cwd = pr_command.payload_cwd(raw)
    # Assert
    assert cwd == "/work"


def test_payload_cwd_is_none_for_plain_text_or_non_string() -> None:
    # Arrange
    non_string = json.dumps({"cwd": 3})
    # Act
    results = (pr_command.payload_cwd("gh pr create"), pr_command.payload_cwd(non_string))
    # Assert
    assert results == (None, None)


def test_pr_workdir_takes_the_last_cd_before_the_pr_command() -> None:
    # Arrange
    command = "cd a && cd b && gh pr create --body x"
    # Act
    workdir = pr_command.pr_workdir(command, Path("/base"))
    # Assert
    assert workdir == Path("/base/a/b")


def test_pr_workdir_ignores_a_cd_after_the_pr_command_and_in_non_pr_commands() -> None:
    # Arrange
    after = "gh pr create --body x && cd /elsewhere"
    plain = "cd /elsewhere && git status"
    # Act
    results = (pr_command.pr_workdir(after, Path("/base")), pr_command.pr_workdir(plain, Path("/base")))
    # Assert
    assert results == (Path("/base"), Path("/base"))


def test_find_config_stops_after_the_repository_root(tmp_path: Path) -> None:
    # Arrange
    (tmp_path / ".conventional-git.toml").write_text("", encoding="utf-8")
    (tmp_path / "repo" / ".git").mkdir(parents=True)
    (tmp_path / "repo" / "sub").mkdir()
    # Act
    found = pr_command.find_config(tmp_path / "repo" / "sub")
    # Assert
    assert found is None
