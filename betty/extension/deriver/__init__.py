"""
Expand an ancestry by deriving additional data from existing data.
"""

from __future__ import annotations

from logging import getLogger
from typing import final

from typing_extensions import override

from betty.deriver import Deriver as DeriverApi
from betty.extension.privatizer import Privatizer
from betty.load import PostLoadAncestryEvent
from betty.locale.localizable import _, Localizable
from betty.model import event_type
from betty.model.event_type import DerivableEventType
from betty.project.extension import Extension
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from betty.event_dispatcher import EventHandlerRegistry
    from betty.plugin import PluginId


async def _derive_ancestry(event: PostLoadAncestryEvent) -> None:
    logger = getLogger(__name__)
    logger.info(event.project.app.localizer._("Deriving..."))

    deriver = DeriverApi(
        event.project.ancestry,
        event.project.configuration.lifetime_threshold,
        set(await event_type.EVENT_TYPE_REPOSITORY.select(DerivableEventType)),
        localizer=event.project.app.localizer,
    )
    await deriver.derive()


@final
class Deriver(Extension):
    """
    Expand an ancestry by deriving additional data from existing data.
    """

    @override
    @classmethod
    def plugin_id(cls) -> PluginId:
        return "deriver"

    @override
    def register_event_handlers(self, registry: EventHandlerRegistry) -> None:
        registry.add_handler(PostLoadAncestryEvent, _derive_ancestry)

    @override
    @classmethod
    def comes_before(cls) -> set[PluginId]:
        return {Privatizer.plugin_id()}

    @override
    @classmethod
    def plugin_label(cls) -> Localizable:
        return _("Deriver")

    @override
    @classmethod
    def plugin_description(cls) -> Localizable:
        return _(
            "Create events such as births and deaths by deriving their details from existing information."
        )
