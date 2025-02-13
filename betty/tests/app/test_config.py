from typing import TYPE_CHECKING

from betty.app.config import AppConfiguration

if TYPE_CHECKING:
    from betty.serde.dump import Dump, DumpMapping


class TestAppConfiguration:
    def test___init___minimal_locale(self) -> None:
        sut = AppConfiguration()
        assert sut.locale is None

    def test___init___with_locale(self) -> None:
        locale = "nl-NL"
        sut = AppConfiguration(locale=locale)
        assert sut.locale == locale

    def test_locale(self) -> None:
        sut = AppConfiguration()
        locale = "nl-NL"
        sut.locale = locale
        assert sut.locale == locale

    def test_load_minimal(self) -> None:
        sut = AppConfiguration()
        dump: DumpMapping[Dump] = {}
        sut.load(dump)

    def test_load_with_locale(self) -> None:
        locale = "nl-NL"
        sut = AppConfiguration()
        dump: DumpMapping[Dump] = {"locale": locale}
        sut.load(dump)
        assert sut.locale == locale

    def test_dump_minimal(self) -> None:
        sut = AppConfiguration()
        actual = sut.dump()
        assert actual == {"locale": None}

    def test_dump_with_locale(self) -> None:
        locale = "nl-NL"
        sut = AppConfiguration(locale=locale)
        actual = sut.dump()
        assert actual == {"locale": locale}
