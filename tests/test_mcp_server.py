from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

from conventional_git import generation
from conventional_git.generation.heuristic import HeuristicProvider
from conventional_git.generation.protocol import ProviderError
from conventional_git.mcp import server

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path
    from typing import Final

    import pytest


_FAILURE_MESSAGE: Final[str] = "jev provider failed: connection refused"


class _FailingProvider:
    name = "jev"

    @staticmethod
    def suggest(
        diff: str,
        *,
        changed_paths: tuple[str, ...] = (),
        types: Mapping[str, str] | None = None,
    ) -> None:
        del diff, changed_paths, types
        raise ProviderError(_FAILURE_MESSAGE)


def test_suggest_commit_message_falls_back_to_heuristic_on_a_provider_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.setattr(generation, "enable_optional_providers", lambda: None)
    monkeypatch.setattr(generation, "available_providers", lambda: ("jev", "heuristic"))
    providers = {"jev": _FailingProvider(), "heuristic": HeuristicProvider()}
    monkeypatch.setattr(generation, "get_provider", providers.get)
    diff = "diff --git a/src/foo.py b/src/foo.py\n--- a/src/foo.py\n+++ b/src/foo.py\n@@ -1 +1 @@\n-a\n+b\n"
    expected_suggestion = HeuristicProvider().suggest(diff, changed_paths=("src/foo.py",))
    # Act
    result = server.suggest_commit_message(diff, changed_paths=["src/foo.py"])
    # Assert
    assert result == {
        "provider": "heuristic",
        "suggestion": asdict(expected_suggestion) if expected_suggestion else None,
        "warning": _FAILURE_MESSAGE,
    }


def _write_commit_type_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    overrides_csv = tmp_path / "commit-types.csv"
    overrides_csv.write_text("type,when_to_use\nspike,Throwaway exploration\n", encoding="utf-8")
    (tmp_path / ".conventional-git.toml").write_text(
        f'[commit]\ntype_overrides = ["{overrides_csv.name}"]\n', encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)


def test_validate_commit_message_honors_the_config_type_overrides(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange
    _write_commit_type_override(tmp_path, monkeypatch)
    # Act
    result = server.validate_commit_message("spike: try a new approach")
    # Assert
    assert result == {"valid": True, "violations": []}


def test_describe_convention_honors_the_config_type_overrides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    _write_commit_type_override(tmp_path, monkeypatch)
    # Act
    result = server.describe_convention()
    # Assert
    expected_types = sorted({*server.commit_vocab.default_types(), "spike"})
    assert result == {
        "commit": {
            "types": expected_types,
            "title_max_length": server.commit_grammar.title_max_length(),
            "body_line_max": server.commit_rules.body_line_max(),
            "message_max_bytes": server.commit_rules.message_max_bytes(),
        },
        "branch": {
            "types": sorted(server.branch_vocab.default_types()),
            "trunks": sorted(server.branch_vocab.default_trunks()),
            "description_max_length": server.branch_grammar.description_max_length(),
        },
    }


def test_validate_branch_name_honors_the_config_type_overrides(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange
    overrides_csv = tmp_path / "branch-types.csv"
    overrides_csv.write_text("type,when_to_use\nspike,Throwaway exploration branch\n", encoding="utf-8")
    (tmp_path / ".conventional-git.toml").write_text(
        f'[branch]\ntype_overrides = ["{overrides_csv.name}"]\n', encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    # Act
    result = server.validate_branch_name("spike/try-a-new-approach")
    # Assert
    assert result == {"valid": True, "violations": []}
