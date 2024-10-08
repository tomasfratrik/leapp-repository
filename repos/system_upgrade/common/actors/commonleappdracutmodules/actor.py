from leapp.actors import Actor
from leapp.libraries.actor import modscan
from leapp.tags import InterimPreparationPhaseTag, IPUWorkflowTag
from leapp.utils.deprecation import suppress_deprecation

from leapp.models import (  # isort:skip
    LiveModeConfig,
    RequiredUpgradeInitramPackages,  # deprecated
    UpgradeDracutModule,  # deprecated
    TargetUserSpaceUpgradeTasks,
    UpgradeInitramfsTasks
)


@suppress_deprecation(RequiredUpgradeInitramPackages, UpgradeDracutModule)
class CommonLeappDracutModules(Actor):
    """
    Influences the generation of the initram disk

    The initram disk generation is influenced by specifying necessary dracut modules and packages that are
    required to be installed in the target userspace so required fields can be included.
    Modules to be added are specified via the UpgradeDracutModule message.
    Packages to install on the target userspace are specified by the RequiredUpgradeInitramPackages message.
    """

    name = 'common_leapp_dracut_modules'
    consumes = (LiveModeConfig,)
    produces = (
        RequiredUpgradeInitramPackages,  # deprecated
        TargetUserSpaceUpgradeTasks,
        UpgradeDracutModule,  # deprecated
        UpgradeInitramfsTasks,
    )
    tags = (IPUWorkflowTag, InterimPreparationPhaseTag)

    def process(self):
        modscan.process()
