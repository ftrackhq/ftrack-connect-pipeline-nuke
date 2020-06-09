# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import logging
from ftrack_connect_pipeline_qt import constants as qt_constants
from ftrack_connect_pipeline_nuke import constants as nuke_constants
from ftrack_connect_pipeline.host import Host


logger = logging.getLogger(
    __name__
)


class NukeHost(Host):
    host = [qt_constants.HOST, nuke_constants.HOST]