import os

from leapp import reporting
from leapp.cli.commands import command_utils
from leapp.exceptions import StopActorExecution
from leapp.libraries.stdlib import api

FMT_LIST_SEPARATOR = '\n    - '


def process():
    flavour = os.environ.get('LEAPP_UPGRADE_PATH_FLAVOUR')
    target_version = os.environ.get('LEAPP_UPGRADE_PATH_TARGET_RELEASE')
    supported_target_versions = command_utils.get_supported_target_versions(flavour)

    unsupported = target_version not in supported_target_versions and os.environ.get('LEAPP_UNSUPPORTED') != '1'

    if unsupported:
        hint = (
                'Upgrade to a supported version\n'
                'Supported target versions for your source version are: {sep}{ver}\n'
                'Alternatively, if you want to upgrade to an unsupported version, '
                'set the `LEAPP_UNSUPPORTED=1` environment variable.'
                .format(sep=FMT_LIST_SEPARATOR, ver=FMT_LIST_SEPARATOR.join(supported_target_versions))
        )

        reporting.create_report([
            reporting.Title('Target version is not supported'),
            reporting.Summary(
                'You are trying to upgrade to an unsupported target\n'
                'Those are the targets without EUS (Extended Update Support)'
            ),
            reporting.Groups([reporting.Groups.INHIBITOR]),
            reporting.Severity(reporting.Severity.HIGH),
            reporting.Remediation(hint=hint),
            reporting.ExternalLink(
                url='https://access.redhat.com/articles/4263361',
                title='Learn more about supported in-place upgrade paths'
            )
        ])
        raise StopActorExecution()
    api.current_logger().info('Target version is supported')
