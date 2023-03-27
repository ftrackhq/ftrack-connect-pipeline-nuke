# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack
import os
from ftrack_connect_pipeline import utils as core_utils

import nuke

from Qt import QtWidgets

import ftrack_api

from ftrack_connect_pipeline_qt.plugin.widget import BaseOptionsWidget
from ftrack_connect_pipeline_qt.ui.utility.widget import dialog
from ftrack_connect_pipeline_qt.ui.utility.widget import radio_button_group, browse_widget
from ftrack_connect_pipeline_nuke import plugin


class NukeSequencePublisherCollectorOptionsWidget(BaseOptionsWidget):
    '''Nuke image sequence collector widget plugin'''

    # Run fetch nodes function on widget initialization
    auto_fetch_on_init = True

    @property
    def image_sequence_path(self):
        '''Return the media path from options'''
        result = self.options.get('image_sequence_path')
        if result:
            result = result.strip()
            if len(result) == 0:
                result = None
        return result

    @image_sequence_path.setter
    def image_sequence_path(self, image_sequence_path):
        '''Store *image_sequence_path* in options and update widgets'''
        if image_sequence_path:
            self.set_option_result(image_sequence_path, 'image_sequence_path')
        else:
            image_sequence_path = '<please choose a image sequence>'
            self.set_option_result(None, 'image_sequence_path')

        # Update UI
        self._image_sequence_path_le.setText(image_sequence_path)
        self._image_sequence_path_le.setToolTip(image_sequence_path)

    @property
    def node_names(self):
        '''Return the list node names'''
        return self._node_names

    @node_names.setter
    def node_names(self, node_names):
        '''Store *node_names* in options and update widgets'''
        self._node_names = node_names
        if self.node_names:
            self._nodes_cb.setDisabled(False)
        else:
            self._nodes_cb.setDisabled(True)

        self._nodes_cb.clear()
        for (index, node_name) in enumerate(self.node_names):
            self._nodes_cb.addItem(node_name)
            if node_name == self._node_name:
                self._nodes_cb.setCurrentIndex(index)

    @property
    def write_node_names(self):
        '''Return the list renderable write node names'''
        return self._write_node_names

    @write_node_names.setter
    def write_node_names(self, node_names):
        '''Store list of renderable write node *node_names* and update widgets'''
        self._write_node_names = node_names
        if self.write_node_names:
            self._write_nodes_cb.setDisabled(False)
        else:
            self._write_nodes_cb.setDisabled(True)

        self._write_nodes_cb.clear()
        for (index, node_name) in enumerate(self.write_node_names):
            self._write_nodes_cb.addItem(node_name)
            if node_name == self._node_name:
                self._write_nodes_cb.setCurrentIndex(index)

        self._render_warning.setVisible(False)
        if len(self.write_node_names) == 0:
            self._render_warning.setVisible(True)
            self._render_warning.setText(
                '<html><i style="color:red">No image sequence write node selected!</i></html>'
            )

        # Extract a path from the write node
        node_name = self._node_name
        if not node_name and len(self.write_node_names) > 0:
            node_name = self.write_node_names[0]

        if node_name:
            node = nuke.toNode(node_name)
            node_file_path = node.knob('file').value()
            if node.knob('use_limit').value():
                first = int(node.knob('first').value())
                last = int(node.knob('last').value())
            else:
                first = int(nuke.root()["first_frame"].getValue())
                last = int(nuke.root()["last_frame"].getValue())
            full_path = '{} [{}-{}]'.format(node_file_path, first, last)
            self.image_sequence_path = full_path

    def __init__(
        self,
        parent=None,
        session=None,
        data=None,
        name=None,
        description=None,
        options=None,
        context_id=None,
        asset_type_name=None,
    ):
        self._node_names = []
        self._write_node_names = []
        self._node_name = options.get('node_name')
        super(NukeSequencePublisherCollectorOptionsWidget, self).__init__(
            parent=parent,
            session=session,
            data=data,
            name=name,
            description=description,
            options=options,
            context_id=context_id,
            asset_type_name=asset_type_name,
        )

    def build(self):
        '''Build the collector widget'''
        super(NukeSequencePublisherCollectorOptionsWidget, self).build()

        self.rbg = radio_button_group.RadioButtonGroup()
        self._nodes_cb = QtWidgets.QComboBox()
        self.rbg.add_button('render_create_write', 'Create write node at selected node:', self._nodes_cb)
        self._write_nodes_cb = QtWidgets.QComboBox()
        self.rbg.add_button('render_selected', 'Render selected node:', self._write_nodes_cb)
        self._browse_widget = browse_widget.BrowseWidget()
        self.rbg.add_button('pickup', 'Pick up rendered image sequence:', self.browse_widget)

        # Use supplied value from definition if available
        if self.options.get('image_sequence_path'):
            self.image_sequence_path = self.options['image_sequence_path']

        if 'mode' not in self.options:
            self.set_option_result(
                'render_create_write', 'mode'
            )  # Set default mode

        self.report_input()

    def post_build(self):
        super(NukeSequencePublisherCollectorOptionsWidget, self).post_build()

        self._nodes_cb.currentTextChanged.connect(self._on_node_selected)
        self._write_nodes_cb.currentTextChanged.connect(self._on_node_selected)

        self.rbg.option_changed.connect(self.set_mode)

        self._browse_image_sequence_path_btn.clicked.connect(
            self._show_image_sequence_dialog
        )

        self.rbg.set_default(self.options['mode'].lower())

    def set_mode(self, mode_name, widget, inner_widget):
        self.set_option_result(mode_name, 'mode')
        if inner_widget in [self._nodes_cb, self._write_nodes_cb]:
            self._on_node_selected(inner_widget.currentText())
        self.report_input()

    def _on_node_selected(self, node_name):
        '''Callback when node is selected in either on of the combo boxes.'''
        if not node_name:
            if 'node_name' in self.options:
                del self.options['node_name']
            return
        self.set_option_result(node_name, 'node_name')

    def on_fetch_callback(self, result):
        '''This function is called by the _set_internal_run_result function of
        the BaseOptionsWidget'''
        self.node_names = [
            node_name for (node_name, unused_is_write_node) in result
        ]
        # Evaluate which nodes writes an image sequence
        write_nodes = []
        for (node_name, is_compatible_write_node) in result:
            if is_compatible_write_node:
                write_nodes.append(node_name)
        self.write_node_names = write_nodes

    def _show_image_sequence_dialog(self):
        '''Shows the file dialog for image sequences'''
        start_dir = None
        if self.image_sequence_path:
            start_dir = os.path.dirname(self._image_sequence_path_le.text())
        (
            file_path,
            unused_selected_filter,
        ) = QtWidgets.QFileDialog.getOpenFileName(
            caption='Choose image sequence',
            dir=start_dir,
            filter='Images (*.cin *.dng *.dpx *.dtex *.gif *.bmp *.float *.pcx '
            '*.png *.psd *.tga *.jpeg *.jpg *.exr *.dds *.hdr *.hdri *.cgi '
            '*.tif *.tiff *.tga *.targa *.yuv);;All files (*)',
        )

        if not file_path:
            return

        file_path = os.path.normpath(file_path)

        image_sequence_path = core_utils.find_image_sequence(file_path)

        if not image_sequence_path:
            dialog.ModalDialog(
                None,
                title='Locate image sequence',
                message='An image sequence on the form "prefix.NNNN.ext" were not '
                'found at {}!'.format(file_path),
            )

        self.image_sequence_path = image_sequence_path
        self.report_input()

    def report_input(self):
        '''(Override) Amount of collected objects has changed, notify parent(s)'''
        status = False
        if self._render_create_write_rb.isChecked():
            if self._nodes_cb.isEnabled() and self._nodes_cb.count() > 0:
                message = '1 script node selected'
                status = True
            else:
                message = 'No script node selected!'
        elif self._render_selected_rb.isChecked():
            if (
                self._write_nodes_cb.isEnabled()
                and self._write_nodes_cb.count() > 0
            ):
                message = '1 write node selected'
                status = True
            else:
                message = 'No write node selected!'
        else:
            if self.image_sequence_path:
                message = '1 image sequence selected'
                status = True
            else:
                message = 'No image sequence selected'

        self.inputChanged.emit(
            {
                'status': status,
                'message': message,
            }
        )


class NukeSequencePublisherCollectorPluginWidget(
    plugin.NukePublisherCollectorPluginWidget
):
    plugin_name = 'nuke_sequence_publisher_collector'
    widget = NukeSequencePublisherCollectorOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = NukeSequencePublisherCollectorPluginWidget(api_object)
    plugin.register()
