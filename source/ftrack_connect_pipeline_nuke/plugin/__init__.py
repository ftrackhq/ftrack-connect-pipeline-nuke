# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import sys
import re
import glob
import os
import traceback
from ftrack_connect_pipeline import plugin
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline_nuke import constants as nuke_constants
from ftrack_connect_pipeline.utils import MainThreadWorker

import nuke


class _BaseNuke(plugin._Base):
    host = nuke_constants.HOST

    def _run(self, event):
        super_fn = super(_BaseNuke, self)._run
        mThreadWorker = MainThreadWorker()
        result = mThreadWorker.execute_in_main_thread(super_fn, event)
        return result


class BaseNukePlugin(plugin.BasePlugin, _BaseNuke):
    type = 'plugin'

    def get_sequence_fist_last_frame(self, path):
        try:
            if '%V' in path:
                path = path.replace('%V', 'left')
            hashMatch = re.search('#+', path)
            if hashMatch:
                path = path[:hashMatch.start(0)] + '*' + path[hashMatch.end(0):]

            nukeFormatMatch = re.search('%\d+d', path)
            if nukeFormatMatch:
                path = (
                    path[:nukeFormatMatch.start(0)] + '*' +
                    path[nukeFormatMatch.end(0):]
                )

            fileExtension = os.path.splitext(path)[1].replace('.', '\.')
            files = sorted(glob.glob(path))
            regexp = '(\d+)' + fileExtension + ''
            first = int(re.findall(regexp, files[0])[0])
            last = int(re.findall(regexp, files[-1])[0])
        except:
            traceback.print_exc(file=sys.stdout)
            first = 1
            last = 1
        return first, last

    def sequence_exists(self, filepath):
        seq = re.compile('(\w+).+(\%\d+d).(\w+)')
        self.logger.info('searching for {}'.format(filepath))

        frames = glob.glob(filepath)
        nfiles = len(frames)
        self.logger.info('Sequence frames {}'.format(nfiles))
        first, last = self.get_sequence_fist_last_frame(filepath)
        total_frames = (last - first) + 1
        self.logger.info('Sequence lenght {}'.format(total_frames))
        if nfiles != total_frames:
            return False

        return True


class BaseNukeWidget(plugin.BaseWidget,_BaseNuke):
    type = 'widget'
    ui = nuke_constants.UI


class ContextNukePlugin(BaseNukePlugin, plugin.ContextPlugin):
    plugin_type = constants.CONTEXT


class ContextNukeWidget(BaseNukeWidget, plugin.ContextWidget):
    plugin_type = constants.CONTEXT


from ftrack_connect_pipeline_nuke.plugin.load import *
from ftrack_connect_pipeline_nuke.plugin.publish import *