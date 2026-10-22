"""Общие настройки тестов: путь к модулям проекта, маркер html и фикстуры Flask."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import app as app_module  # noqa: E402  (импорт после настройки sys.path)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "html: тест рендерит настоящие шаблоны templates/*.html "
        "(без шаблонов можно пропустить: -m 'not html')",
    )


@pytest.fixture
def client(monkeypatch):
    """Тестовый клиент Flask; рабочая папка — корень репозитория (там лежат *_sort.py)."""
    monkeypatch.chdir(REPO_ROOT)
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def rendered(monkeypatch):
    """Подменяет render_template в app.py: записывает (имя шаблона, контекст) вместо рендера.

    Так логику страниц можно проверять независимо от HTML-шаблонов.
    """
    calls = []

    def fake_render_template(template_name, **context):
        calls.append((template_name, context))
        return f"rendered {template_name}"

    monkeypatch.setattr(app_module, "render_template", fake_render_template)
    return calls
