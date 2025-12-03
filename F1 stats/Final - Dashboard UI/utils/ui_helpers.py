"""
Common UI building helpers used across modules.
"""

from typing import Optional

from PyQt6 import QtCore, QtWidgets


def build_toolbar_toggle(toolbar: QtWidgets.QToolBar, label_off: str, label_on: str) -> QtWidgets.QCheckBox:
    """
    Create a toggle switch style checkbox and add it to a toolbar.
    """
    toggle = QtWidgets.QCheckBox(label_off)
    toggle.setTristate(False)
    toggle.setChecked(False)
    toolbar.addWidget(toggle)
    toolbar.addSeparator()
    toolbar.addWidget(QtWidgets.QLabel("Mode switch"))

    def update_label(state: int) -> None:
        toggle.setText(label_on if state == QtCore.Qt.CheckState.Checked.value else label_off)

    toggle.stateChanged.connect(update_label)
    return toggle


def labeled_value(label: str, value: str) -> QtWidgets.QWidget:
    """Create a stacked label/value pair."""
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(QtWidgets.QLabel(label))
    value_lbl = QtWidgets.QLabel(value)
    value_lbl.setObjectName("valueLabel")
    layout.addWidget(value_lbl)
    return widget


def set_tab_visibility(tab_widget: QtWidgets.QTabWidget, tab: QtWidgets.QWidget, visible: bool) -> None:
    """Toggle tab visibility by index."""
    index = tab_widget.indexOf(tab)
    if index != -1:
        tab_widget.setTabVisible(index, visible)


def add_export_buttons(container: QtWidgets.QWidget, handlers: dict) -> QtWidgets.QHBoxLayout:
    """
    Attach export buttons to a container. Handlers map label -> callable.
    """
    layout = QtWidgets.QHBoxLayout()
    for label, fn in handlers.items():
        btn = QtWidgets.QPushButton(label)
        btn.clicked.connect(fn)
        layout.addWidget(btn)
    container.layout().addLayout(layout)
    return layout
