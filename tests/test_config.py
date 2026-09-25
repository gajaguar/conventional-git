from __future__ import annotations

from typing import TYPE_CHECKING

from conventional_git.config import Config

if TYPE_CHECKING:
    from pathlib import Path


def test_load_returns_defaults_when_no_file_exists(tmp_path: Path) -> None:
    # Arrange
    missing = tmp_path / ".conventional-git.toml"
    # Act
    config = Config.load(missing)
    # Assert
    assert config == Config(
        extra_attribution_patterns=(),
        commit_type_overrides=(),
        branch_type_overrides=(),
        branch_trunk_overrides=(),
    )


def test_load_resolves_relative_override_paths_against_the_config_directory(tmp_path: Path) -> None:
    # Arrange
    config_path = tmp_path / "subdir" / ".conventional-git.toml"
    config_path.parent.mkdir()
    config_path.write_text(
        '[commit]\ntype_overrides = ["commit-types.csv"]\n'
        '[branch]\ntype_overrides = ["branch-types.csv"]\ntrunk_overrides = ["branch-trunks.csv"]\n',
        encoding="utf-8",
    )
    # Act
    config = Config.load(config_path)
    # Assert
    assert config.commit_type_overrides == (config_path.parent / "commit-types.csv",)
    assert config.branch_type_overrides == (config_path.parent / "branch-types.csv",)
    assert config.branch_trunk_overrides == (config_path.parent / "branch-trunks.csv",)


def test_load_keeps_absolute_override_paths_unchanged(tmp_path: Path) -> None:
    # Arrange
    absolute_csv = tmp_path / "elsewhere" / "commit-types.csv"
    config_path = tmp_path / ".conventional-git.toml"
    config_path.write_text(f'[commit]\ntype_overrides = ["{absolute_csv.as_posix()}"]\n', encoding="utf-8")
    # Act
    config = Config.load(config_path)
    # Assert
    assert config.commit_type_overrides == (absolute_csv,)


def test_load_reads_attribution_patterns(tmp_path: Path) -> None:
    # Arrange
    config_path = tmp_path / ".conventional-git.toml"
    config_path.write_text('[commit]\nattribution_patterns = ["Signed-off-by"]\n', encoding="utf-8")
    # Act
    config = Config.load(config_path)
    # Assert
    assert config.extra_attribution_patterns == ("Signed-off-by",)
