import pytest

from leapp import reporting
from leapp.cli.commands import command_utils
from leapp.exceptions import StopActorExecution
from leapp.libraries.actor import verifytargetversion
from leapp.libraries.common.testutils import create_report_mocked, logger_mocked
from leapp.libraries.stdlib import api

upgrade_paths = {
        "7.9": ["8.10"],
        "8.10": ["9.4", "9.5", "9.6"],
        "9.6": ["10.0"],
        "7": ["8.10"],
        "8": ["9.4", "9.5", "9.6"],
        "9": ["10.0"]
}


def _get_supported_target_versions(source_version):
    return upgrade_paths.get(source_version, [])


@pytest.fixture
def setup_monkeypatch(monkeypatch):
    """Fixture to set up common monkeypatches."""

    def _setup(source_version, target_version, leapp_unsupported="0"):
        monkeypatch.setenv('LEAPP_UPGRADE_PATH_FLAVOUR', 'default')
        monkeypatch.setenv('LEAPP_UPGRADE_PATH_TARGET_RELEASE', target_version)
        monkeypatch.setenv('LEAPP_UNSUPPORTED', leapp_unsupported)
        monkeypatch.setattr(command_utils, 'get_supported_target_versions',
                            lambda flavour: _get_supported_target_versions(source_version))
        monkeypatch.setattr(reporting, 'create_report', create_report_mocked())
        monkeypatch.setattr(api, 'current_logger', logger_mocked())
    return _setup


@pytest.mark.parametrize("source_version, target_version, leapp_unsupported", [
    # LEAPP_UNSUPPORTED=0
    ("7.9", "9.0", "0"),
    ("8.10", "9.0", "0"),
    ("9.6", "10.1", "0"),
    ("7", "9.0", "0"),
    ("8", "9.0", "0"),
    ("9", "10.1", "0"),
    # LEAPP_UNSUPPORTED=1
    ("7.9", "9.0", "1"),
    ("8.10", "9.0", "1"),
    ("9.6", "10.1", "1"),
    ("7", "9.0", "1"),
    ("8", "9.0", "1"),
    ("9", "10.1", "1"),
])
def test_unsuppoted_paths(setup_monkeypatch, source_version, target_version, leapp_unsupported):
    setup_monkeypatch(source_version, target_version, leapp_unsupported)

    if leapp_unsupported == "1":
        verifytargetversion.process()
        assert reporting.create_report.called == 0
        assert api.current_logger.infomsg == ['Target version is supported']
    else:
        with pytest.raises(StopActorExecution):
            verifytargetversion.process()
        assert reporting.create_report.called == 1
        assert 'Target version is not supported' in reporting.create_report.report_fields['title']
        assert 'You are trying to upgrade ' in reporting.create_report.report_fields['summary']
        assert 'inhibitor' in reporting.create_report.report_fields['groups']


@pytest.mark.parametrize("source_version, target_version", [
    ("7.9", "8.10"),
    ("8.10", "9.4"),
    ("8.10", "9.5"),
    ("8.10", "9.6"),
    ("9.6", "10.0"),
    ("7", "8.10"),
    ("8", "9.4"),
    ("8", "9.5"),
    ("8", "9.6"),
    ("9", "10.0"),
])
def test_supported_paths(setup_monkeypatch, source_version, target_version):
    setup_monkeypatch(source_version, target_version, leapp_unsupported="0")

    verifytargetversion.process()
    assert reporting.create_report.called == 0
    assert api.current_logger.infomsg == ['Target version is supported']
