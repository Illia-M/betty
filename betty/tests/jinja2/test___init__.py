from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import aiofiles
from aiofiles.tempfile import TemporaryDirectory

from betty.jinja2 import Jinja2Renderer, _Citer, Jinja2Provider, EntityContexts
from betty.model.ancestry import (
    Citation,
    HasFileReferences,
)
from betty.project import Project
from betty.test_utils.assets.templates import TemplateTestBase
from betty.test_utils.model import DummyEntity

if TYPE_CHECKING:
    from betty.app import App


class TestJinja2Provider:
    async def test_globals(self) -> None:
        sut = Jinja2Provider()
        assert isinstance(sut.globals, dict)

    async def test_filters(self) -> None:
        sut = Jinja2Provider()
        assert isinstance(sut.filters, dict)

    async def test_tests(self) -> None:
        sut = Jinja2Provider()
        assert isinstance(sut.tests, dict)

    async def test_new_context_vars(self) -> None:
        sut = Jinja2Provider()
        assert isinstance(sut.new_context_vars(), dict)


class TestJinja2Renderer:
    async def test_render_file(self, new_temporary_app: App) -> None:
        async with Project.new_temporary(new_temporary_app) as project, project:
            sut = Jinja2Renderer(project.jinja2_environment, project.configuration)
            template = "{% if true %}true{% endif %}"
            expected_output = "true"
            async with TemporaryDirectory() as working_directory_path_str:
                working_directory_path = Path(working_directory_path_str)
                template_file_path = working_directory_path / "betty.txt.j2"
                async with aiofiles.open(template_file_path, "w") as f:
                    await f.write(template)
                await sut.render_file(template_file_path)
                async with aiofiles.open(working_directory_path / "betty.txt") as f:
                    assert expected_output == (await f.read()).strip()
                assert not template_file_path.exists()

    async def test_file_extensions(self, new_temporary_app: App) -> None:
        async with Project.new_temporary(new_temporary_app) as project, project:
            sut = Jinja2Renderer(project.jinja2_environment, project.configuration)
            sut.file_extensions  # noqa B018


class DummyHasFileReferencesEntity(HasFileReferences, DummyEntity):
    pass


class TestGlobalCiter(TemplateTestBase):
    async def test_cite(self) -> None:
        citation1 = Citation()
        citation2 = Citation()
        sut = _Citer()
        assert sut.cite(citation1) == 1
        assert sut.cite(citation2) == 2
        assert sut.cite(citation1) == 1

    async def test_iter(self) -> None:
        citation1 = Citation()
        citation2 = Citation()
        sut = _Citer()
        sut.cite(citation1)
        sut.cite(citation2)
        sut.cite(citation1)
        assert [(1, citation1), (2, citation2)] == list(sut)

    async def test_len(self) -> None:
        citation1 = Citation()
        citation2 = Citation()
        sut = _Citer()
        sut.cite(citation1)
        sut.cite(citation2)
        sut.cite(citation1)
        assert len(sut) == 2


class EntityContextsTestEntityA(DummyEntity):
    pass


class EntityContextsTestEntityB(DummyEntity):
    pass


class TestEntityContexts:
    async def test___getitem__(self) -> None:
        sut = EntityContexts()
        assert sut[EntityContextsTestEntityA] is None

    async def test___getitem___with___init__(self) -> None:
        a = EntityContextsTestEntityA()
        sut = EntityContexts(a)
        assert sut[EntityContextsTestEntityA] is a

    async def test___call__(self) -> None:
        a = EntityContextsTestEntityA()
        contexts = EntityContexts()
        sut = contexts(a)
        assert sut[EntityContextsTestEntityA] is a

    async def test___call___with___init__(self) -> None:
        a = EntityContextsTestEntityA()
        b = EntityContextsTestEntityA()
        contexts = EntityContexts(a)
        sut = contexts(b)
        assert sut[EntityContextsTestEntityA] is b