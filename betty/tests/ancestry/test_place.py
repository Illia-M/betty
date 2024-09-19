from __future__ import annotations

from typing import Sequence, Mapping, Any, TYPE_CHECKING

from geopy import Point
from typing_extensions import override

from betty.ancestry import Event, Enclosure
from betty.ancestry.event_type.event_types import Birth
from betty.ancestry.link import Link
from betty.ancestry.name import Name
from betty.ancestry.place import Place
from betty.ancestry.place_type.place_types import Unknown as UnknownPlaceType
from betty.date import Date
from betty.locale import UNDETERMINED_LOCALE
from betty.test_utils.ancestry.place_type import DummyPlaceType
from betty.test_utils.json.linked_data import assert_dumps_linked_data
from betty.test_utils.model import EntityTestBase

if TYPE_CHECKING:
    from betty.model import Entity


class TestPlace(EntityTestBase):
    @override
    def get_sut_class(self) -> type[Place]:
        return Place

    @override
    async def get_sut_instances(self) -> Sequence[Entity]:
        return [
            Place(),
            Place(names=[Name("My First Place")]),
        ]

    def test_place_type_default(self) -> None:
        sut = Place()
        assert isinstance(sut.place_type, UnknownPlaceType)

    def test___init___with_place_type(self) -> None:
        place_type = DummyPlaceType()
        sut = Place(place_type=place_type)
        assert sut.place_type is place_type

    def test_place_type(self) -> None:
        place_type = DummyPlaceType()
        sut = Place()
        sut.place_type = place_type
        assert sut.place_type is place_type

    async def test_events(self) -> None:
        sut = Place(
            id="P1",
            names=[Name("The Place")],
        )
        event = Event(
            id="1",
            event_type=Birth(),
        )
        sut.events.add(event)
        assert event in sut.events
        assert sut == event.place
        sut.events.remove(event)
        assert list(sut.events) == []
        assert event.place is None

    async def test_enclosed_by(self) -> None:
        sut = Place(
            id="P1",
            names=[Name("The Place")],
        )
        assert list(sut.enclosed_by) == []
        enclosing_place = Place(
            id="P2",
            names=[Name("The Other Place")],
        )
        enclosure = Enclosure(encloses=sut, enclosed_by=enclosing_place)
        assert enclosure in sut.enclosed_by
        assert sut == enclosure.encloses
        sut.enclosed_by.remove(enclosure)
        assert list(sut.enclosed_by) == []
        assert enclosure.encloses is None

    async def test_encloses(self) -> None:
        sut = Place(
            id="P1",
            names=[Name("The Place")],
        )
        assert list(sut.encloses) == []
        enclosed_place = Place(
            id="P2",
            names=[Name("The Other Place")],
        )
        enclosure = Enclosure(encloses=enclosed_place, enclosed_by=sut)
        assert enclosure in sut.encloses
        assert sut == enclosure.enclosed_by
        sut.encloses.remove(enclosure)
        assert list(sut.encloses) == []
        assert enclosure.enclosed_by is None

    async def test_walk_encloses_without_encloses(self) -> None:
        sut = Place(
            id="P1",
            names=[Name("The Place")],
        )
        assert list(sut.walk_encloses) == []

    async def test_walk_encloses_with_encloses(self) -> None:
        sut = Place(
            id="P1",
            names=[Name("The Place")],
        )
        encloses_place = Place(
            id="P2",
            names=[Name("The Other Place")],
        )
        encloses = Enclosure(encloses_place, sut)
        encloses_encloses_place = Place(
            id="P2",
            names=[Name("The Other Other Place")],
        )
        encloses_encloses = Enclosure(encloses_encloses_place, encloses_place)
        assert list(sut.walk_encloses) == [encloses, encloses_encloses]

    async def test_id(self) -> None:
        place_id = "C1"
        sut = Place(
            id=place_id,
            names=[Name("one")],
        )
        assert sut.id == place_id

    async def test_links(self) -> None:
        sut = Place(
            id="P1",
            names=[Name("The Place")],
        )
        assert list(sut.links) == []

    async def test_names(self) -> None:
        name = Name("The Place")
        sut = Place(
            id="P1",
            names=[name],
        )
        assert list(sut.names) == [name]

    async def test_coordinates(self) -> None:
        name = Name("The Place")
        sut = Place(
            id="P1",
            names=[name],
        )
        coordinates = Point()
        sut.coordinates = coordinates
        assert sut.coordinates == coordinates

    async def test_dump_linked_data_should_dump_minimal(self) -> None:
        place_id = "the_place"
        place = Place(id=place_id)
        expected: Mapping[str, Any] = {
            "@context": {
                "names": "https://schema.org/name",
                "enclosedBy": "https://schema.org/containedInPlace",
                "encloses": "https://schema.org/containsPlace",
                "events": "https://schema.org/event",
            },
            "@id": "https://example.com/place/the_place/index.json",
            "@type": "https://schema.org/Place",
            "id": place_id,
            "names": [],
            "enclosedBy": [],
            "encloses": [],
            "events": [],
            "notes": [],
            "links": [
                {
                    "url": "/place/the_place/index.json",
                    "relationship": "canonical",
                    "mediaType": "application/ld+json",
                    "locale": "und",
                },
                {
                    "url": "/place/the_place/index.html",
                    "relationship": "alternate",
                    "mediaType": "text/html",
                    "locale": "en-US",
                },
            ],
            "private": False,
        }
        actual = await assert_dumps_linked_data(place)
        assert actual == expected

    async def test_dump_linked_data_should_dump_full(self) -> None:
        place_id = "the_place"
        name = "The Place"
        locale = "nl-NL"
        latitude = 12.345
        longitude = -54.321
        coordinates = Point(latitude, longitude)
        link = Link("https://example.com/the-place")
        link.label = "The Place Online"
        place = Place(
            id=place_id,
            names=[Name({locale: name}, date=Date(1970, 1, 1))],
            events=[
                Event(
                    id="E1",
                    event_type=Birth(),
                )
            ],
            links=[link],
        )
        place.coordinates = coordinates
        Enclosure(encloses=place, enclosed_by=Place(id="the_enclosing_place"))
        Enclosure(encloses=Place(id="the_enclosed_place"), enclosed_by=place)
        expected: Mapping[str, Any] = {
            "@context": {
                "names": "https://schema.org/name",
                "enclosedBy": "https://schema.org/containedInPlace",
                "encloses": "https://schema.org/containsPlace",
                "events": "https://schema.org/event",
                "coordinates": "https://schema.org/geo",
            },
            "@id": "https://example.com/place/the_place/index.json",
            "@type": "https://schema.org/Place",
            "id": place_id,
            "names": [
                {"translations": {"nl-NL": name}},
            ],
            "events": [
                "/event/E1/index.json",
            ],
            "notes": [],
            "links": [
                {
                    "url": "https://example.com/the-place",
                    "label": {
                        "translations": {UNDETERMINED_LOCALE: "The Place Online"}
                    },
                    "locale": "und",
                },
                {
                    "url": "/place/the_place/index.json",
                    "relationship": "canonical",
                    "mediaType": "application/ld+json",
                    "locale": "und",
                },
                {
                    "url": "/place/the_place/index.html",
                    "relationship": "alternate",
                    "mediaType": "text/html",
                    "locale": "en-US",
                },
            ],
            "coordinates": {
                "@context": {
                    "latitude": "https://schema.org/latitude",
                    "longitude": "https://schema.org/longitude",
                },
                "@type": "https://schema.org/GeoCoordinates",
                "latitude": latitude,
                "longitude": longitude,
            },
            "encloses": [
                "/place/the_enclosed_place/index.json",
            ],
            "enclosedBy": [
                "/place/the_enclosing_place/index.json",
            ],
            "private": False,
        }
        actual = await assert_dumps_linked_data(place)
        assert actual == expected