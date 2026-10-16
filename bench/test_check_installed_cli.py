"""Focused checks for installed-wheel distribution identity validation."""
import zipfile

import pytest

from check_installed_cli import distribution_identity


METADATA = "Metadata-Version: 2.1\nName: dxa-research-toolkit\nVersion: 1.2.3\n\n"
ENTRY_POINTS = (
    "[console_scripts]\n"
    "dxa = dxa:main\n"
    "dxadyn = dxadyn:main\n"
    "dxaprove = dxaprove:main\n"
)


def make_wheel(path, *, metadata=METADATA, entry_points=ENTRY_POINTS,
               extra_metadata=()):
    with zipfile.ZipFile(path, "w") as wheel:
        wheel.writestr("dxa_research_toolkit-1.2.3.dist-info/METADATA", metadata)
        wheel.writestr("dxa_research_toolkit-1.2.3.dist-info/entry_points.txt",
                       entry_points)
        for index, value in enumerate(extra_metadata):
            wheel.writestr(
                f"other-{index}.dist-info/METADATA",
                value,
            )
    return path


def test_distribution_identity_accepts_expected_metadata(tmp_path):
    wheel = make_wheel(tmp_path / "valid.whl")

    assert distribution_identity(wheel) == {
        "name": "dxa-research-toolkit",
        "version": "1.2.3",
    }


def test_distribution_identity_rejects_wrong_name(tmp_path):
    wheel = make_wheel(
        tmp_path / "wrong-name.whl",
        metadata=METADATA.replace("dxa-research-toolkit", "unrelated-toolkit"),
    )

    with pytest.raises(AssertionError, match="unexpected wheel distribution name"):
        distribution_identity(wheel)


@pytest.mark.parametrize(
    "entry_points",
    [
        ENTRY_POINTS.replace("dxaprove = dxaprove:main\n", ""),
        ENTRY_POINTS.replace("dxadyn = dxadyn:main", "dxadyn = other:main"),
    ],
    ids=["missing-script", "wrong-script-target"],
)
def test_distribution_identity_rejects_invalid_console_script_mapping(
    tmp_path, entry_points
):
    wheel = make_wheel(tmp_path / "invalid-entry-points.whl",
                       entry_points=entry_points)

    with pytest.raises(AssertionError, match="console-script metadata mismatch"):
        distribution_identity(wheel)


def test_distribution_identity_rejects_duplicate_dist_info_metadata(tmp_path):
    wheel = make_wheel(tmp_path / "duplicate-metadata.whl",
                       extra_metadata=(METADATA,))

    with pytest.raises(AssertionError, match="exactly one dist-info METADATA"):
        distribution_identity(wheel)
