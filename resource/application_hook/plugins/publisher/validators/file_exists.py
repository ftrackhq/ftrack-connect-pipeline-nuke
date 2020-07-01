# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api
import os

from ftrack_connect_pipeline_nuke import plugin

class FileExistsValidatorPlugin(plugin.PublisherValidatorNukePlugin):
    plugin_name = 'file_exists'

    def run(self, context=None, data=None, options=None):
        scene_path = data[0]
        if os.path.exists(scene_path):
            return True
        else:
            self.logger.debug("Nuke Scene file does not exists")
        return False


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = FileExistsValidatorPlugin(api_object)
    plugin.register()
