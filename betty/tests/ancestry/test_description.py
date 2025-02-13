from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, cast

import pytest

from betty.locale.localizer import DEFAULT_LOCALIZER
from betty.test_utils.ancestry.description import DummyHasDescription
from betty.test_utils.json.linked_data import assert_dumps_linked_data

if TYPE_CHECKING:
    from betty.serde.dump import DumpMapping, Dump
    from betty.ancestry.link import HasLinks


class TestHasDescription:
    async def test___init___with_description(self) -> None:
        description = "Hello, world!"
        sut = DummyHasDescription(description=description)
        assert sut.description.localize(DEFAULT_LOCALIZER) == description

    async def test_description(self) -> None:
        sut = DummyHasDescription()
        assert not sut.description

    @pytest.mark.parametrize(
        ("expected", "sut"),
        [
            (
                {
                    "@context": {"description": "https://schema.org/description"},
                    "description": cast(Mapping[str, str], {}),
                },
                DummyHasDescription(),
            ),
            (
                {
                    "@context": {"description": "https://schema.org/description"},
                    "description": {"und": "Hello, world!"},
                },
                DummyHasDescription(description="Hello, world!"),
            ),
        ],
    )
    async def test_dump_linked_data(
        self, expected: DumpMapping[Dump], sut: HasLinks
    ) -> None:
        assert await assert_dumps_linked_data(sut) == expected
