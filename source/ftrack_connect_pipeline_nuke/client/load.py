from ftrack_connect_pipeline.client.load import QtPipelineLoaderWidget
from ftrack_connect_pipeline_nuke.constants import HOST, UI


class QtPipelineNukeLoaderWidget(QtPipelineLoaderWidget):
    '''Dockable nuke load widget'''
    def __init__(self, event_manager, parent=None):
        super(QtPipelineNukeLoaderWidget, self).__init__(event_manager=event_manager, parent=parent)
        self.setWindowTitle('nuke Pipeline Loader{}'.format(hostid))
