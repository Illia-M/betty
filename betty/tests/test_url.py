from typing import Any

from parameterized import parameterized

from betty.model import Entity
from betty.model.ancestry import Person, Place, File, Source, Death, PlaceName, Event, Citation
from betty.config import Configuration, LocaleConfiguration
from betty.tests import TestCase
from betty.url import LocalizedPathUrlGenerator, _EntityUrlGenerator, AppUrlGenerator


class LocalizedPathUrlGeneratorTest(TestCase):
    @parameterized.expand([
        ('', '/'),
        ('/index.html', '/index.html'),
        ('/example', 'example'),
        ('/example', '/example'),
        ('/example', 'example/'),
        ('/example', '/example/'),
        ('/example/index.html', 'example/index.html'),
        ('/example/index.html', '/example/index.html'),
    ])
    def test_generate(self, expected: str, resource: str):
        configuration = Configuration('/tmp', 'https://example.com')
        sut = LocalizedPathUrlGenerator(configuration)
        self.assertEquals(expected, sut.generate(resource, 'text/html'))

    @parameterized.expand([
        ('', 'index.html'),
        ('', '/index.html'),
        ('/example', 'example/index.html'),
        ('/example', '/example/index.html'),
    ])
    def test_generate_with_clean_urls(self, expected: str, resource: str):
        configuration = Configuration('/tmp', 'https://example.com')
        configuration.clean_urls = True
        sut = LocalizedPathUrlGenerator(configuration)
        self.assertEquals(expected, sut.generate(resource, 'text/html'))

    @parameterized.expand([
        ('https://example.com', '/'),
        ('https://example.com/example', 'example'),
    ])
    def test_generate_absolute(self, expected: str, resource: str):
        configuration = Configuration('/tmp', 'https://example.com')
        sut = LocalizedPathUrlGenerator(configuration)
        self.assertEquals(expected, sut.generate(
            resource, 'text/html', absolute=True))

    def test_generate_with_invalid_value(self):
        configuration = Configuration('/tmp', 'https://example.com')
        sut = LocalizedPathUrlGenerator(configuration)
        with self.assertRaises(ValueError):
            sut.generate(9, 'text/html')

    def test_generate_multilingual(self):
        configuration = Configuration('/tmp', 'https://example.com')
        configuration.locales.replace([
            LocaleConfiguration('nl'),
            LocaleConfiguration('en'),
        ])
        sut = LocalizedPathUrlGenerator(configuration)
        self.assertEquals('/nl/index.html',
                          sut.generate('/index.html', 'text/html'))
        self.assertEquals(
            '/en/index.html', sut.generate('/index.html', 'text/html', locale='en'))


class EntityUrlGeneratorTest(TestCase):
    class UrlyEntity(Entity):
        pass

    def test_generate(self):
        configuration = Configuration('/tmp', 'https://example.com')
        sut = _EntityUrlGenerator(configuration, self.UrlyEntity, 'prefix/%s/index.%s')
        self.assertEquals('/prefix/I1/index.html', sut.generate(self.UrlyEntity('I1'), 'text/html'))

    def test_generate_with_invalid_value(self):
        configuration = Configuration('/tmp', 'https://example.com')
        sut = _EntityUrlGenerator(configuration, self.UrlyEntity, 'prefix/%s/index.html')
        with self.assertRaises(ValueError):
            sut.generate(9, 'text/html')


class AppUrlGeneratorTest(TestCase):
    @parameterized.expand([
        ('/index.html', '/index.html'),
        ('/person/P1/index.html', Person('P1')),
        ('/event/E1/index.html', Event('E1', Death())),
        ('/place/P1/index.html', Place('P1', [PlaceName('Place 1')])),
        ('/file/F1/index.html', File('F1', '/tmp')),
        ('/source/S1/index.html', Source('S1', 'Source 1')),
        ('/citation/C1/index.html', Citation('C1', Source('Source 1'))),
    ])
    def test_generate(self, expected: str, resource: Any):
        configuration = Configuration('/tmp', 'https://example.com')
        sut = AppUrlGenerator(configuration)
        self.assertEquals(expected, sut.generate(resource, 'text/html'))

    def test_generate_with_invalid_value(self):
        configuration = Configuration('/tmp', 'https://example.com')
        sut = AppUrlGenerator(configuration)
        with self.assertRaises(ValueError):
            sut.generate(9, 'text/html')
