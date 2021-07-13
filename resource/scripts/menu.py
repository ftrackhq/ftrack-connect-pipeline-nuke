# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import os
import logging
import ftrack_connect_pipeline_nuke
from ftrack_connect_pipeline_nuke import host as nuke_host
from ftrack_connect_pipeline_qt import event
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline_nuke.menu import build_menu_widgets

import ftrack_api
import nuke

from ftrack_connect_pipeline.configure_logging import configure_logging

configure_logging(
    'ftrack_connect_pipeline_nuke',
    extra_modules=['ftrack_connect_pipeline', 'ftrack_connect_pipeline_qt']
)

logger = logging.getLogger('ftrack_connect_pipeline_nuke')

created_dialogs = dict()

def get_ftrack_menu(menu_name = 'ftrack', submenu_name = 'pipeline'):
    '''Get the current ftrack menu, create it if does not exists.'''

    nuke_menu = nuke.menu("Nuke")
    ftrack_menu = nuke_menu.findItem(menu_name)
    if not ftrack_menu:
        ftrack_menu = nuke_menu.addMenu(menu_name)
    ftrack_sub_menu = ftrack_menu.findItem(submenu_name)
    if not ftrack_sub_menu:
        ftrack_sub_menu = ftrack_menu.addMenu(submenu_name)

    return ftrack_sub_menu

def script_init():
    # Setup script with fps and frame range from ftrack

    nuke.removeOnUserCreate(script_init)

    fps = str(os.getenv('FPS'))

    if not fps is None and 0 < len(fps):

        fps_float = float(fps)

        nuke.tprint('Setting current fps to: {0}'.format(fps_float))
        nuke.root().knob("fps").setValue(fps_float)
    else:
        nuke.tprint('No fps supplied!')

    # Set animation timeline

    start = os.getenv('FS')
    end = os.getenv('FE')

    if not start is None and 0 < len(start) and not end is None and 0 < len(end):
        start_int = int(float(start))
        end_int = int(float(end))

        nuke.tprint('Setting script timeline to {0}-{1}'.format(
            start_int, end_int))
        nuke.root().knob("lock_range").setValue(False)
        nuke.root().knob("first_frame").setValue(start_int)
        nuke.root().knob("last_frame").setValue(end_int)
        nuke.root().knob("lock_range").setValue(True)
    else:
        nuke.tprint('No timeline start and/or end supplied!')

def initialise():

    logger.debug('Setting up the menu')
    session = ftrack_api.Session(auto_connect_event_hub=False)

    event_manager = event.QEventManager(
        session=session, mode=constants.LOCAL_EVENT_MODE
    )
    nuke_host.NukeHost(event_manager)

    ftrack_menu = get_ftrack_menu()

    build_menu_widgets(ftrack_menu, event_manager)

    nuke.addOnUserCreate(script_init)

initialise()
