from ftrack_connect_pipeline.client.publish import QtPipelinePublishWidget
from ftrack_connect_pipeline_nuke.constants import HOST, UI


class QtPipelineNukePublisherWidget(QtPipelinePublishWidget):
    '''Dockable nuke load widget'''
    def __init__(self, event_manager, parent=None):
        super(QtPipelineNukePublisherWidget, self).__init__(event_manager=event_manager, parent=parent)
        self.setWindowTitle('nuke Pipeline Publisher {}'.format(event_manager.hostid))
