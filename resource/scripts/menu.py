# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import os
import logging
import ftrack_connect_pipeline_nuke
from ftrack_connect_pipeline_nuke import usage, host as nuke_host
from ftrack_connect_pipeline_qt import event
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline_nuke.menu import build_menu_widgets

import ftrack_api
import nuke


logger = logging.getLogger('ftrack_connect_pipeline_nuke.scripts.userSetup')

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


def initialise():
    # TODO : later we need to bring back here all the nuke initialiations
    #  from ftrack-connect-nuke such as frame start / end etc....

    logger.info('Setting up the menu')
    session = ftrack_api.Session(auto_connect_event_hub=False)

    event_manager = event.QEventManager(
        session=session, mode=constants.LOCAL_EVENT_MODE
    )
    nuke_host.NukeHost(event_manager)

    usage.send_event(
        'USED-FTRACK-CONNECT-PIPELINE-NUKE'
    )

    ftrack_menu = get_ftrack_menu()

    build_menu_widgets(ftrack_menu, event_manager)


initialise()
