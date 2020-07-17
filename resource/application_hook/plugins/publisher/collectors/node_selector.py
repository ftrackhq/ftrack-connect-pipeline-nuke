# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import nuke

from ftrack_connect_pipeline_nuke import plugin


class NodeSelectorNukePlugin(plugin.PublisherCollectorNukePlugin):
    plugin_name = 'node_selector'

    def run(self, context=None, data=None, options=None):

        node_name = options['node_name']
        return [node_name]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = NodeSelectorNukePlugin(api_object)
    plugin.register()
