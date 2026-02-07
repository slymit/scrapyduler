import pytest
from scrapyd.app import application
from scrapyd.config import Config

from scrapyduler.launcher import Launcher


@pytest.fixture
def config(request):
    config = Config()
    if request.param:
        section = request.node.callspec.id
        config.cp.add_section(section)
        for key, value in request.param:
            config.cp.set(section, key, value)
    return config


@pytest.fixture
def app(config, mocker):
    app = application(config)
    app.root = mocker.MagicMock()
    return app


@pytest.fixture
def launcher(app, config):
    return Launcher(config, app)
