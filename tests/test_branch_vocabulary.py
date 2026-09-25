from __future__ import annotations

from typing import TYPE_CHECKING

from conventional_git.branch import vocabulary
from conventional_git.config import Config

if TYPE_CHECKING:
    from pathlib import Path


def test_resolve_policy_uses_defaults_when_config_has_no_overrides() -> None:
    # Arrange
    config = Config(
        extra_attribution_patterns=(),
        commit_type_overrides=(),
        branch_type_overrides=(),
        branch_trunk_overrides=(),
    )
    # Act
    policy = vocabulary.resolve_policy(config)
    # Assert
    assert policy.types == vocabulary.default_types()
    assert policy.trunks == vocabulary.default_trunks()


def test_resolve_policy_honors_branch_type_overrides_from_config(tmp_path: Path) -> None:
    # Arrange
    overrides_csv = tmp_path / "branch-types.csv"
    overrides_csv.write_text("type,when_to_use\nspike,Throwaway exploration branch\n", encoding="utf-8")
    config = Config(
        extra_attribution_patterns=(),
        commit_type_overrides=(),
        branch_type_overrides=(overrides_csv,),
        branch_trunk_overrides=(),
    )
    # Act
    policy = vocabulary.resolve_policy(config)
    # Assert
    assert "spike" in policy.types
    assert policy.types >= vocabulary.default_types()


def test_resolve_policy_layers_extra_csvs_on_top_of_config_overrides(tmp_path: Path) -> None:
    # Arrange
    config_types_csv = tmp_path / "config-types.csv"
    config_types_csv.write_text("type,when_to_use\nfromconfig,From config\n", encoding="utf-8")
    extra_types_csv = tmp_path / "flag-types.csv"
    extra_types_csv.write_text("type,when_to_use\nfromflag,From --types-csv\n", encoding="utf-8")
    extra_trunks_csv = tmp_path / "flag-trunks.csv"
    extra_trunks_csv.write_text("name,when_to_use\npython,Permanent language layer branch\n", encoding="utf-8")
    config = Config(
        extra_attribution_patterns=(),
        commit_type_overrides=(),
        branch_type_overrides=(config_types_csv,),
        branch_trunk_overrides=(),
    )
    # Act
    policy = vocabulary.resolve_policy(config, extra_types_csv=extra_types_csv, extra_trunks_csv=extra_trunks_csv)
    # Assert
    assert "fromconfig" in policy.types
    assert "fromflag" in policy.types
    assert "python" in policy.trunks
