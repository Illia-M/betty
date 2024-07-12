from betty.locale.localizer import DEFAULT_LOCALIZER
from betty.locale.localizable import plain
from betty.assertion.error import AssertionFailed, AssertionFailedGroup
from betty.tests.assertion import assert_error


class TestAssertionFailed:
    async def test_localizewithout_contexts(self) -> None:
        sut = AssertionFailed(plain("Something went wrong!"))
        assert sut.localize(DEFAULT_LOCALIZER) == "Something went wrong!"

    async def test_localize_with_contexts(self) -> None:
        sut = AssertionFailed(plain("Something went wrong!"))
        sut = sut.with_context(plain("Somewhere, at some point..."))
        sut = sut.with_context(plain("Somewhere else, too..."))
        assert (
            sut.localize(DEFAULT_LOCALIZER)
            == "Something went wrong!\n- Somewhere, at some point...\n- Somewhere else, too..."
        )

    async def test_with_context(self) -> None:
        sut = AssertionFailed(plain("Something went wrong!"))
        sut_with_context = sut.with_context(plain("Somewhere, at some point..."))
        assert sut != sut_with_context
        assert [
            context.localize(DEFAULT_LOCALIZER) for context in sut_with_context.contexts
        ] == ["Somewhere, at some point..."]


class TestAssertionFailedGroup:
    async def test_localize_without_errors(self) -> None:
        sut = AssertionFailedGroup()
        assert sut.localize(DEFAULT_LOCALIZER) == ""

    async def test_localize_with_one_error(self) -> None:
        sut = AssertionFailedGroup()
        sut.append(AssertionFailed(plain("Something went wrong!")))
        assert sut.localize(DEFAULT_LOCALIZER) == "Something went wrong!"

    async def test_localize_with_multiple_errors(self) -> None:
        sut = AssertionFailedGroup()
        sut.append(AssertionFailed(plain("Something went wrong!")))
        sut.append(AssertionFailed(plain("Something else went wrong, too!")))
        assert (
            sut.localize(DEFAULT_LOCALIZER)
            == "Something went wrong!\n\nSomething else went wrong, too!"
        )

    async def test_localize_with_predefined_contexts(self) -> None:
        sut = AssertionFailedGroup()
        sut = sut.with_context(plain("Somewhere, at some point..."))
        sut = sut.with_context(plain("Somewhere else, too..."))
        error_1 = AssertionFailed(plain("Something went wrong!"))
        error_2 = AssertionFailed(plain("Something else went wrong, too!"))
        sut.append(error_1)
        sut.append(error_2)
        assert not len(error_1.contexts)
        assert not len(error_2.contexts)
        assert (
            sut.localize(DEFAULT_LOCALIZER)
            == "Something went wrong!\n- Somewhere, at some point...\n- Somewhere else, too...\n\nSomething else went wrong, too!\n- Somewhere, at some point...\n- Somewhere else, too..."
        )

    async def test_localize_with_postdefined_contexts(self) -> None:
        sut = AssertionFailedGroup()
        error_1 = AssertionFailed(plain("Something went wrong!"))
        error_2 = AssertionFailed(plain("Something else went wrong, too!"))
        sut.append(error_1)
        sut.append(error_2)
        sut = sut.with_context(plain("Somewhere, at some point..."))
        sut = sut.with_context(plain("Somewhere else, too..."))
        assert not len(error_1.contexts)
        assert not len(error_2.contexts)
        assert (
            sut.localize(DEFAULT_LOCALIZER)
            == "Something went wrong!\n- Somewhere, at some point...\n- Somewhere else, too...\n\nSomething else went wrong, too!\n- Somewhere, at some point...\n- Somewhere else, too..."
        )

    async def test_with_context(self) -> None:
        sut = AssertionFailedGroup()
        sut_with_context = sut.with_context(plain("Somewhere, at some point..."))
        assert sut is not sut_with_context
        assert [
            context.localize(DEFAULT_LOCALIZER) for context in sut_with_context.contexts
        ] == ["Somewhere, at some point..."]

    async def test_catch_without_contexts(self) -> None:
        sut = AssertionFailedGroup()
        error = AssertionFailed(plain("Help!"))
        with sut.catch() as errors:
            raise error
        assert_error(errors, error=error)  # type: ignore[unreachable]
        assert_error(sut, error=error)

    async def test_catch_with_contexts(self) -> None:
        sut = AssertionFailedGroup()
        error = AssertionFailed(plain("Help!"))
        with sut.catch(plain("Somewhere")) as errors:
            raise error
        assert_error(errors, error=error.with_context(plain("Somewhere")))  # type: ignore[unreachable]
        assert_error(sut, error=error.with_context(plain("Somewhere")))