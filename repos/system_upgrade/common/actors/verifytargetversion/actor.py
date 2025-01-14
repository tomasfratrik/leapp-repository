from leapp.actors import Actor
from leapp.libraries.actor import verifytargetversion
from leapp.models import Report
from leapp.tags import FactsPhaseTag, IPUWorkflowTag


class VerifyTargetVersion(Actor):
    """
    Verify if the target system version is supported by the upgrade process.

    Invoke inhibitor if the target system is not supported.
    Allow unsupported target if `LEAPP_UNSUPPORTED=1` is set.
    """

    name = 'verify_target_version'
    consumes = ()
    produces = (Report,)
    tags = (FactsPhaseTag, IPUWorkflowTag)

    def process(self):
        verifytargetversion.process()
