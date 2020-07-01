# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import nuke

from ftrack_connect_pipeline_nuke import plugin


class AbcNukeImportPlugin(plugin.LoaderImporterNukePlugin):
    plugin_name = 'abc_nuke_import'

    def run(self, context=None, data=None, options=None):
        results = {}
        paths_to_import = data
        for component_path in paths_to_import:
            self.logger.debug('Importing path {}'.format(component_path))
            import_result = nuke.createNode(
                'ReadGeo2', 'file {}'.format(component_path)
            )
            results[component_path] = import_result.name()

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = AbcNukeImportPlugin(api_object)
    plugin.register()