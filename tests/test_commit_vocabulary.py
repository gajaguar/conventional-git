from __future__ import annotations

from typing import TYPE_CHECKING

from conventional_git.commit import vocabulary
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
    assert policy.extra_attribution_patterns == ()


def test_resolve_policy_merges_config_overrides(tmp_path: Path) -> None:
    # Arrange
    overrides_csv = tmp_path / "commit-types.csv"
    overrides_csv.write_text("type,when_to_use\nspike,Throwaway exploration\n", encoding="utf-8")
    config = Config(
        extra_attribution_patterns=("Signed-off-by",),
        commit_type_overrides=(overrides_csv,),
        branch_type_overrides=(),
        branch_trunk_overrides=(),
    )
    # Act
    policy = vocabulary.resolve_policy(config)
    # Assert
    assert "spike" in policy.types
    assert policy.types >= vocabulary.default_types()
    assert policy.extra_attribution_patterns == ("Signed-off-by",)


def test_resolve_policy_layers_extra_types_csv_on_top_of_config_overrides(tmp_path: Path) -> None:
    # Arrange
    config_csv = tmp_path / "from-config.csv"
    config_csv.write_text("type,when_to_use\nfromconfig,From config\n", encoding="utf-8")
    extra_csv = tmp_path / "from-flag.csv"
    extra_csv.write_text("type,when_to_use\nfromflag,From --types-csv\n", encoding="utf-8")
    config = Config(
        extra_attribution_patterns=(),
        commit_type_overrides=(config_csv,),
        branch_type_overrides=(),
        branch_trunk_overrides=(),
    )
    # Act
    policy = vocabulary.resolve_policy(config, extra_types_csv=extra_csv)
    # Assert
    assert "fromconfig" in policy.types
    assert "fromflag" in policy.types
