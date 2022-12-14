# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import logging
import sys
import re
import os
import glob
import traceback
import threading
from functools import wraps

from Qt import QtWidgets

import nuke
import nukescripts

from ftrack_connect_pipeline.utils import (
    get_save_path,
)
from ftrack_connect_pipeline_nuke.constants import asset as asset_const

logger = logging.getLogger(__name__)


def get_main_window():
    return QtWidgets.QApplication.activeWindow()


def run_in_main_thread(f):
    '''Make sure a function runs in the main Nuke thread.'''

    @wraps(f)
    def decorated(*args, **kwargs):
        if threading.currentThread().name != 'MainThread':
            return nuke.executeInMainThreadWithResult(
                f, args=args, kwargs=kwargs
            )
        else:
            return f(*args, **kwargs)

    return decorated


def get_sequence_fist_last_frame(path):
    '''
    Returns first and last frame from the given *path*
    '''
    try:
        if '%V' in path:
            path = path.replace('%V', 'left')
        has_match = re.search('#+', path)
        if has_match:
            path = path[: has_match.start(0)] + '*' + path[has_match.end(0) :]

        nuke_format_match = re.search('%\d+d', path)
        if nuke_format_match:
            path = (
                path[: nuke_format_match.start(0)]
                + '*'
                + path[nuke_format_match.end(0) :]
            )

        file_extension = os.path.splitext(path)[1].replace('.', '\.')
        files = sorted(glob.glob(path))
        regexp = '(\d+){} '.format(file_extension)
        first = int(re.findall(regexp, files[0])[0])
        last = int(re.findall(regexp, files[-1])[0])
    except:
        traceback.print_exc(file=sys.stdout)
        first = 1
        last = 1
    return first, last


def sequence_exists(file_path):
    seq = re.compile('(\w+).+(\%\d+d).(\w+)')
    logger.debug('searching for {}'.format(file_path))

    frames = glob.glob(file_path)
    n_files = len(frames)
    logger.debug('Sequence frames {}'.format(n_files))
    first, last = get_sequence_fist_last_frame(file_path)
    total_frames = (last - first) + 1
    logger.debug('Sequence lenght {}'.format(total_frames))
    if n_files != total_frames:
        return False

    return True


def get_unique_scene_name(current_name):
    '''
    Returns a unique name from the given *current_name*

    *current_name*: string name of an object.
    '''
    res = nuke.toNode(str(current_name))
    if res:
        i = 0
        while res:
            unique_name = current_name + str(i)
            res = nuke.toNode(str(current_name))
            i = i + 1
        return unique_name
    else:
        return current_name


def get_nodes_with_ftrack_tab():
    '''
    Returns all the nuke dcc_objects that contain an ftrack tab.
    '''
    dependencies = []
    for node in nuke.allNodes():
        if asset_const.FTRACK_PLUGIN_TYPE in node.knobs().keys():
            dependencies.append(node)
    return dependencies


def reference_script(path, options=None):
    '''
    Create LiveGroup from the givem *path*
    '''
    node = nuke.createNode(
        'LiveGroup', 'published true file {}'.format(path), inpanel=False
    )
    return node


def open_script(path, options=None):
    '''
    Open nuke scene from the given *path*
    '''
    result = nuke.scriptOpen(path)
    return result


def import_script(path, options=None):
    '''
    Import the scene from the given *path*
    '''
    return nuke.nodePaste(path)


def get_current_scene_objects():
    return set(nuke.allNodes())


def get_all_write_nodes():
    write_nodes = []
    for node in nuke.allNodes('Write'):
        write_nodes.append(node)
    return write_nodes


def cleanSelection():
    for node in nuke.selectedNodes():
        node['selected'].setValue(False)


def init_nuke(context_id=None, session=None):
    '''
    Initialise timeline in Nuke based on shot/asset build settings.

    :param session:
    :param from_context: If True, the timeline data should be fetched from current context instead of environment variables.
    :return:
    '''
    fstart = fend = fps = None
    if context_id:
        context = session.query(
            'Context where id={}'.format(context_id)
        ).first()
        if context is None:
            logger.error(
                'Cannot initialize Nuke timeline - no such context: {}'.format(
                    context_id
                )
            )
            return
        shot = None
        if context.entity_type == 'Shot':
            shot = context
        elif context.entity_type == 'Task':
            parent = context['parent']
            if parent.entity_type == 'Shot':
                shot = parent
        if not shot:
            logger.warning(
                'Cannot initialize Nuke timeline - no shot related to context: {}'.format(
                    context_id
                )
            )
            return
        elif (
            not 'fstart' in shot['custom_attributes']
            or not 'fend' in shot['custom_attributes']
        ):
            logger.warning(
                'Cannot initialize Nuke timeline - no fstart or fend shot custom attributes available'.format()
            )
            return
        if 'fstart' in shot['custom_attributes']:
            fstart = int(shot['custom_attributes']['fstart'])
        if 'fend' in shot['custom_attributes']:
            fend = int(shot['custom_attributes']['fend'])
        if 'fps' in shot['custom_attributes']:
            fps = float(shot['custom_attributes']['fps'])
    else:
        # Set default values from environments.
        if 'FS' in os.environ and len(os.environ['FS'] or '') > 0:
            fstart = os.environ.get('FS', 0)
        if 'FE' in os.environ and len(os.environ['FE'] or '') > 0:
            fend = os.environ.get('FE', 100)
        if 'FPS' in os.environ:
            fps = float(os.environ['FPS'])

    if fstart is not None and fend is not None:
        nuke.root().knob("lock_range").setValue(False)
        logger.info('Setting start frame : {}'.format(fstart))
        nuke.knob('root.first_frame', str(fstart))
        logger.info('Setting end frame : {}'.format(fend))
        nuke.knob('root.last_frame', str(fend))
        nuke.root().knob("lock_range").setValue(True)
    if fps is not None:
        logger.info('Setting FPS : {}'.format(fps))
        nuke.root().knob("fps").setValue(fps)


def save(context_id, session, temp=True):
    '''Save script locally, with the next version number based on latest version
    in ftrack.'''

    save_path, message = get_save_path(
        context_id, session, extension='.nk', temp=temp
    )

    if save_path is None:
        return (False, message)

    nuke.scriptSaveAs(save_path, overwrite=1)
    message = 'Saved Nuke script @ "{}"'.format(save_path)
    result = save_path

    return result, message
