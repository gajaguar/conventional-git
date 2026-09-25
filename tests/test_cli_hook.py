from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

_MANAGED_BY: Final[str] = "# managed-by: conventional-git"
_HOOK_NAMES: Final[tuple[str, ...]] = ("commit-msg", "pre-commit", "pre-push")
_EXECUTABLE_MODE: Final[int] = 0o755


# A global core.hooksPath would redirect the installer away from the scratch repo.
def _isolated_env() -> dict[str, str]:
    return {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def _run_cli(*arguments: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "conventional_git.cli.app", *arguments],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=_isolated_env(),
    )


def _init_repository(path: Path, branch: str | None = None) -> None:
    init = ["git", "init", *(["-b", branch] if branch else []), str(path)]
    subprocess.run(init, capture_output=True, check=True, env=_isolated_env())


def _commit(repository: Path, message: str) -> None:
    subprocess.run(
        [  # ruff: ignore[start-process-with-partial-path]
            "git",
            "-C",
            str(repository),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "--allow-empty",
            "-m",
            message,
        ],
        capture_output=True,
        check=True,
        env=_isolated_env(),
    )


# The generated hook calls the conventional-git entry point, so the
# interpreter's bin directory must come first on PATH.
def _hook_env() -> dict[str, str]:
    path = f"{Path(sys.executable).parent}{os.pathsep}{os.environ.get('PATH', os.defpath)}"
    return {**_isolated_env(), "PATH": path}


def _run_pre_commit(repository: Path) -> subprocess.CompletedProcess[str]:
    hook = repository / ".git" / "hooks" / "pre-commit"
    return subprocess.run(
        [str(hook)],
        cwd=repository,
        capture_output=True,
        text=True,
        check=False,
        env=_hook_env(),
    )


def test_install_writes_executable_marked_hooks(tmp_path: Path) -> None:
    # Arrange
    repository = tmp_path / "repository"
    _init_repository(repository)
    # Act
    completed = _run_cli("hook", "install", "--target", str(repository), cwd=repository)
    # Assert
    assert completed.returncode == 0
    for name in _HOOK_NAMES:
        hook = repository / ".git" / "hooks" / name
        assert hook.exists()
        assert _MANAGED_BY in hook.read_text(encoding="utf-8")
        assert stat.S_IMODE(hook.stat().st_mode) == _EXECUTABLE_MODE


def test_install_writes_common_hooks_for_linked_worktree(tmp_path: Path) -> None:
    # Arrange
    repository = tmp_path / "repository"
    worktree = tmp_path / "worktree"
    _init_repository(repository)
    (repository / "README.md").write_text("repository\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repository), "add", "README.md"], check=True, env=_isolated_env())  # ruff: ignore[start-process-with-partial-path]
    _commit(repository, "feat: initialize")
    subprocess.run(
        ["git", "-C", str(repository), "worktree", "add", str(worktree), "-b", "feat/worktree"],  # ruff: ignore[start-process-with-partial-path]
        check=True,
        env=_isolated_env(),
    )
    # Act
    completed = _run_cli("hook", "install", cwd=worktree)
    # Assert
    assert completed.returncode == 0
    for name in _HOOK_NAMES:
        hook = repository / ".git" / "hooks" / name
        assert hook.exists()
        assert _MANAGED_BY in hook.read_text(encoding="utf-8")


def test_install_uses_configured_hooks_path(tmp_path: Path) -> None:
    # Arrange
    repository = tmp_path / "repository"
    _init_repository(repository)
    subprocess.run(
        ["git", "-C", str(repository), "config", "core.hooksPath", ".husky"],  # ruff: ignore[start-process-with-partial-path]
        check=True,
        env=_isolated_env(),
    )
    # Act
    completed = _run_cli("hook", "install", cwd=repository)
    # Assert
    assert completed.returncode == 0
    assert (repository / ".husky" / "commit-msg").exists()
    assert not (repository / ".git" / "hooks" / "commit-msg").exists()
    assert "outside" in completed.stdout


def test_install_rejects_non_repository(tmp_path: Path) -> None:
    # Arrange
    directory = tmp_path / "not-a-repository"
    directory.mkdir()
    # Act
    completed = _run_cli("hook", "install", cwd=directory)
    # Assert
    assert completed.returncode == 1
    assert completed.stderr.strip() == f"Not a git repository: {directory}"


def test_install_refuses_existing_hook_without_force(tmp_path: Path) -> None:
    # Arrange
    repository = tmp_path / "repository"
    _init_repository(repository)
    hook = repository / ".git" / "hooks" / "commit-msg"
    hook.write_text("foreign hook\n", encoding="utf-8")
    # Act
    completed = _run_cli("hook", "install", "--target", str(repository), cwd=repository)
    # Assert
    assert completed.returncode == 1
    assert "Refusing to overwrite existing hook" in completed.stderr
    assert hook.read_text(encoding="utf-8") == "foreign hook\n"


def test_install_force_overwrites_existing_hook(tmp_path: Path) -> None:
    # Arrange
    repository = tmp_path / "repository"
    _init_repository(repository)
    hook = repository / ".git" / "hooks" / "commit-msg"
    hook.write_text("foreign hook\n", encoding="utf-8")
    # Act
    completed = _run_cli("hook", "install", "--target", str(repository), "--force", cwd=repository)
    # Assert
    assert completed.returncode == 0
    assert _MANAGED_BY in hook.read_text(encoding="utf-8")


def test_uninstall_removes_marked_hooks_and_keeps_foreign_hook(tmp_path: Path) -> None:
    # Arrange
    repository = tmp_path / "repository"
    _init_repository(repository)
    installed = _run_cli("hook", "install", cwd=repository)
    assert installed.returncode == 0
    foreign_hook = repository / ".git" / "hooks" / "pre-commit"
    foreign_hook.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    # Act
    completed = _run_cli("hook", "uninstall", cwd=repository)
    # Assert
    assert completed.returncode == 0
    assert not (repository / ".git" / "hooks" / "commit-msg").exists()
    assert foreign_hook.read_text(encoding="utf-8") == "#!/usr/bin/env bash\nexit 0\n"
    assert not (repository / ".git" / "hooks" / "pre-push").exists()
    assert "not installed by conventional-git" in completed.stdout


def test_pre_commit_accepts_valid_unborn_branch(tmp_path: Path) -> None:
    # Arrange
    repository = tmp_path / "repository"
    _init_repository(repository, branch="feat/native")
    installed = _run_cli("hook", "install", cwd=repository)
    assert installed.returncode == 0
    # Act
    completed = _run_pre_commit(repository)
    # Assert
    assert completed.returncode == 0


def test_pre_commit_rejects_invalid_unborn_branch(tmp_path: Path) -> None:
    # Arrange
    repository = tmp_path / "repository"
    _init_repository(repository, branch="Bad_Branch")
    installed = _run_cli("hook", "install", cwd=repository)
    assert installed.returncode == 0
    # Act
    completed = _run_pre_commit(repository)
    # Assert
    assert completed.returncode != 0
    assert "branch.format" in completed.stderr


def test_pre_commit_skips_detached_head(tmp_path: Path) -> None:
    # Arrange
    repository = tmp_path / "repository"
    _init_repository(repository, branch="feat/native")
    _commit(repository, "feat: initialize")
    subprocess.run(
        ["git", "-C", str(repository), "checkout", "--detach"],  # ruff: ignore[start-process-with-partial-path]
        capture_output=True,
        check=True,
        env=_isolated_env(),
    )
    installed = _run_cli("hook", "install", cwd=repository)
    assert installed.returncode == 0
    # Act
    completed = _run_pre_commit(repository)
    # Assert
    assert completed.returncode == 0
