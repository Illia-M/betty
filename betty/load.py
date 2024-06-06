"""
Provide the Ancestry loading API.
"""

import logging
from xml.etree.ElementTree import Element

from html5lib import parse

from betty.app import App
from betty.asyncio import gather
from betty.fetch import Fetcher, FetchError
from betty.media_type import MediaType, InvalidMediaType
from betty.model.ancestry import Link, HasLinks
from betty.warnings import deprecated


@deprecated(
    "This function is deprecated as of Betty 0.3.2, and will be removed in Betty 0.4.x. Instead, use `logging.getLogger()`."
)
def getLogger() -> logging.Logger:
    """
    Get the ancestry loading logger.
    """
    return logging.getLogger(__name__)


class Loader:
    """
    Load (part of) the project's ancestry.

    Extensions may subclass this to add data to the ancestry, if they choose to do so.
    """

    async def load(self) -> None:
        """
        Load ancestry data.
        """
        raise NotImplementedError(repr(self))


class PostLoader:
    """
    Act on the project's ancestry having been loaded.
    """

    async def post_load(self) -> None:
        """
        Act on the ancestry having been loaded.

        This method is called immediately after :py:meth:`betty.load.Loader.load`.
        """
        raise NotImplementedError(repr(self))


async def load(app: App) -> None:
    """
    Load an ancestry.
    """
    await app.dispatcher.dispatch(Loader)()
    await app.dispatcher.dispatch(PostLoader)()
    await _fetch_link_titles(app)


async def _fetch_link_titles(app: App) -> None:
    await gather(
        *(
            _fetch_link_title(app.fetcher, link)
            for entity in app.project.ancestry
            if isinstance(entity, HasLinks)
            for link in entity.links
        )
    )


async def _fetch_link_title(fetcher: Fetcher, link: Link) -> None:
    if link.label is not None:
        return
    try:
        response = await fetcher.fetch(link.url)
    except FetchError as error:
        logging.getLogger(__name__).warning(str(error))
        return
    try:
        content_type = MediaType(response.headers["Content-Type"])
    except InvalidMediaType:
        return

    if (content_type.type, content_type.subtype, content_type.suffix) not in (
        ("text", "html", None),
        ("application", "xhtml", "+xml"),
    ):
        return

    document = parse(response.text)
    title = _extract_html_title(document)
    if title is not None:
        link.label = title
    if link.description is None:
        description = _extract_html_meta_description(document)
        if description is not None:
            link.description = description


def _extract_html_title(document: Element) -> str | None:
    head = document.find(
        "ns:head",
        namespaces={
            "ns": "http://www.w3.org/1999/xhtml",
        },
    )
    if head is None:
        return None
    title = head.find(
        "ns:title",
        namespaces={
            "ns": "http://www.w3.org/1999/xhtml",
        },
    )
    if title is None:
        return None
    return title.text


def _extract_html_meta_description(document: Element) -> str | None:
    head = document.find(
        "ns:head",
        namespaces={
            "ns": "http://www.w3.org/1999/xhtml",
        },
    )
    if head is None:
        return None
    metas = head.findall(
        "ns:meta",
        namespaces={
            "ns": "http://www.w3.org/1999/xhtml",
        },
    )
    for attr_name, attr_value in (
        ("name", "description"),
        ("property", "og:description"),
    ):
        for meta in metas:
            if meta.get(attr_name, None) == attr_value:
                return meta.get("content", None)
    return None
