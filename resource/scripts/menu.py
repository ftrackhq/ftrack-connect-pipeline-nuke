# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import logging

from ftrack_connect_pipeline_nuke import usage, host as nuke_host
from ftrack_connect_pipeline import event, host, utils
from ftrack_connect_pipeline import session
from ftrack_connect_pipeline_nuke import constants
from ftrack_connect_pipeline_nuke.menu import build_menu_widgets
from ftrack_connect_pipeline_nuke.constants import UI, HOST
import ftrack_connect_pipeline_nuke

import sys
import traceback

logger = logging.getLogger('ftrack_connect_pipeline_nuke.scripts.menu')


def initialise():
    # TODO : later we need to bring back here all the nuke initialiations from ftrack-connect-nuke
    # such as frame start / end etc....
    event_manager = event.EventManager(
        session=session.get_shared_session(),
        remote=utils.remote_event_mode(),
        ui=UI,
        host=HOST
    )

    host.initialise(event_manager)

    usage.send_event(
        'USED-FTRACK-CONNECT-PIPELINE-NUKE'
    )

    # Enable loader and publisher only if is set to run local (default)
    ftrack_menu = nuke_host.get_ftrack_menu()

    if not event_manager.remote:
        try:
            build_menu_widgets(ftrack_menu, event_manager)
        except:
            traceback.print_exc(file=sys.stdout)

    else:
        nuke_host.notify_connected_client(
            event_manager.session,
            event_manager.hostid)





initialise()
