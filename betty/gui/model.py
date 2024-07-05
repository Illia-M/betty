"""
Provide entity management widgets for the Graphical User Interface.
"""

from __future__ import annotations

from typing import Callable, cast, Iterator, TYPE_CHECKING

from PyQt6.QtWidgets import (
    QFormLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from typing_extensions import override

from betty.gui.locale import LocalizedObject
from betty.model import UserFacingEntity, Entity
from betty.project import EntityReference, EntityReferenceSequence, Project

if TYPE_CHECKING:
    from betty.locale import Localizable


class EntityReferenceCollector(LocalizedObject, QWidget):
    """
    A form widget that allows users to configure an entity reference.
    """

    def __init__(
        self,
        project: Project,
        entity_reference: EntityReference[UserFacingEntity & Entity],
        label_builder: Callable[[], str] | None = None,
        caption_builder: Callable[[], str] | None = None,
    ):
        super().__init__(project.app)
        self._entity_reference = entity_reference
        self._label_builder = label_builder
        self._caption_builder = caption_builder

        self._layout = QFormLayout()
        self.setLayout(self._layout)

        if self._entity_reference.entity_type_is_constrained:
            self._entity_type_label = QLabel()
        else:

            def _update_entity_type() -> None:
                self._entity_reference.entity_type = self._entity_type.currentData()

            self._entity_type = QComboBox()
            self._entity_type.currentIndexChanged.connect(_update_entity_type)
            entity_types = enumerate(
                sorted(
                    cast(
                        Iterator[type["UserFacingEntity & Entity"]],
                        filter(
                            lambda entity_type: issubclass(
                                entity_type, UserFacingEntity
                            ),
                            project.entity_types,
                        ),
                    ),
                    key=lambda entity_type: entity_type.entity_type_label().localize(
                        self._app.localizer
                    ),
                )
            )
            for i, entity_type in entity_types:
                self._entity_type.addItem(
                    entity_type.entity_type_label().localize(self._app.localizer),
                    entity_type,
                )
                if entity_type == self._entity_reference.entity_type:
                    self._entity_type.setCurrentIndex(i)
            self._entity_type_label = QLabel()
            self._layout.addRow(self._entity_type_label, self._entity_type)

        def _update_entity_id() -> None:
            self._entity_reference.entity_id = self._entity_id.text()

        self._entity_id = QLineEdit()
        self._entity_id.textChanged.connect(_update_entity_id)
        self._entity_id_label = QLabel()
        self._layout.addRow(self._entity_id_label, self._entity_id)

        self._set_translatables()

    @override
    def _set_translatables(self) -> None:
        super()._set_translatables()
        if self._entity_reference.entity_type:
            self._entity_id_label.setText(
                self._app.localizer._("{entity_type_label} ID").format(
                    entity_type_label=self._entity_reference.entity_type.entity_type_label().localize(
                        self._app.localizer
                    ),
                )
            )
        else:
            self._entity_id_label.setText(self._app.localizer._("Entity ID"))


class EntityReferenceSequenceCollector(LocalizedObject, QWidget):
    """
    A form widget that allows users to configure a sequence of entity references.
    """

    def __init__(
        self,
        project: Project,
        entity_references: EntityReferenceSequence[UserFacingEntity & Entity],
        label_text: Localizable | None = None,
        caption_text: Localizable | None = None,
    ):
        super().__init__(project.app)
        self._project = project
        self._entity_references = entity_references
        self._label_text = label_text
        self._caption_text = caption_text
        self._entity_reference_collectors: list[EntityReferenceCollector] = [
            EntityReferenceCollector(project, entity_reference)
            for entity_reference in entity_references
        ]

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        if label_text:
            self._label = QLabel()
            self._layout.addWidget(self._label)

        self._entity_reference_collectors_widget = QWidget()
        self._entity_reference_collectors_layout = QVBoxLayout()
        self._entity_reference_collectors_widget.setLayout(
            self._entity_reference_collectors_layout
        )
        self._layout.addWidget(self._entity_reference_collectors_widget)

        self._entity_reference_collection_widgets: list[QWidget] = []
        self._entity_reference_remove_buttons: list[QPushButton] = []

        if caption_text:
            self._caption = QLabel()
            self._layout.addWidget(self._caption)

        self._add_entity_reference_button = QPushButton()
        self._add_entity_reference_button.released.connect(self._add_entity_reference)
        self._layout.addWidget(self._add_entity_reference_button)

        self._build_entity_references_collection()

        self._set_translatables()

    def _add_entity_reference(self) -> None:
        entity_reference = EntityReference["UserFacingEntity & Entity"]()
        self._entity_references.append(entity_reference)
        self._build_entity_reference_collection(
            len(self._entity_references) - 1, entity_reference
        )
        self._set_translatables()

    def _remove_entity_reference(self, i: int) -> None:
        del self._entity_references[i]
        del self._entity_reference_collectors[i]
        del self._entity_reference_remove_buttons[i]
        self._entity_reference_collectors_layout.removeWidget(
            self._entity_reference_collection_widgets[i]
        )
        del self._entity_reference_collection_widgets[i]

    def _build_entity_references_collection(self) -> None:
        for i, entity_reference in enumerate(self._entity_references):
            self._build_entity_reference_collection(i, entity_reference)

    def _build_entity_reference_collection(
        self,
        i: int,
        entity_reference: EntityReference[UserFacingEntity & Entity],
    ) -> None:
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        self._entity_reference_collection_widgets.insert(i, widget)
        self._entity_reference_collectors_layout.insertWidget(i, widget)

        entity_reference_collector = EntityReferenceCollector(
            self._project, entity_reference
        )
        self._entity_reference_collectors.append(entity_reference_collector)
        layout.addWidget(entity_reference_collector)

        entity_reference_remove_button = QPushButton()
        self._entity_reference_remove_buttons.insert(i, entity_reference_remove_button)
        entity_reference_remove_button.released.connect(
            lambda: self._remove_entity_reference(i)
        )
        layout.addWidget(entity_reference_remove_button)

    @override
    def _set_translatables(self) -> None:
        super()._set_translatables()
        if self._label_text:
            self._label.setText(self._label_text.localize(self._app.localizer))
        if self._caption_text:
            self._caption.setText(self._caption_text.localize(self._app.localizer))
        self._add_entity_reference_button.setText(
            self._app.localizer._("Add an entity")
        )
        for entity_reference_remove_button in self._entity_reference_remove_buttons:
            entity_reference_remove_button.setText(self._app.localizer._("Remove"))
