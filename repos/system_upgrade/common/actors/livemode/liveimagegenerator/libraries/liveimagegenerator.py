import os
import os.path
import shutil

from leapp.exceptions import StopActorExecutionError
from leapp.libraries.common import mounting
from leapp.libraries.stdlib import api, CalledProcessError, run
from leapp.models import LiveModeArtifacts, LiveModeConfig, TargetUserSpaceInfo


def lighten_target_userpace(context):
    """
    Remove unneeded files from the target userspace.
    """

    userspace_trees_to_prune = ['artifacts', 'boot']

    for tree_to_prune in userspace_trees_to_prune:
        tree_full_path = os.path.join(context.base_dir, tree_to_prune)
        try:
            shutil.rmtree(tree_full_path)
        except OSError as error:
            api.current_logger().warning('Failed to remove /%s directory from the live image. Full error: %s',
                                         tree_to_prune, error)


def build_squashfs(livemode_config, userspace_info):
    """
    Generate the live rootfs image based on the target userspace

    :param livemode LiveModeConfig: Livemode configuration message
    :param userspace_info TargetUserspaceInfo: Information about how target userspace is set up
    """
    target_userspace_fullpath = userspace_info.path
    squashfs_fullpath = livemode_config.squashfs_fullpath

    api.current_logger().info('Building the squashfs image %s from target userspace located at %s',
                              squashfs_fullpath, target_userspace_fullpath)

    try:
        if os.path.exists(squashfs_fullpath):
            os.unlink(squashfs_fullpath)
    except OSError as error:
        api.current_logger().warning('Failed to remove already existing %s. Full error: %s',
                                     squashfs_fullpath, error)

    try:
        run(['mksquashfs', target_userspace_fullpath, squashfs_fullpath])
    except CalledProcessError as error:
        raise StopActorExecutionError(
           'Cannot pack the target userspace into a squash image. ',
           details={'details': 'The following error occurred while building the squashfs image: {0}.'.format(error)}
        )

    return squashfs_fullpath


def generate_live_image_if_enabled():
    """
    Main function to generate the additional artifacts needed to run in live mode.
    """

    livemode_config = next(api.consume(LiveModeConfig), None)
    if not livemode_config or not livemode_config.is_enabled:
        return

    userspace_info = next(api.consume(TargetUserSpaceInfo), None)

    with mounting.NspawnActions(base_dir=userspace_info.path) as context:
        lighten_target_userpace(context)
        squashfs_path = build_squashfs(livemode_config, userspace_info)
        api.produce(LiveModeArtifacts(squashfs_path=squashfs_path))