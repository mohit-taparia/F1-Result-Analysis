from f1_pipeline.config import ApiSettings
from f1_pipeline.ingestion.client import JolpicaClient


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, pages):
        self.pages = iter(pages)
        self.headers = {}
        self.calls = []

    def mount(self, *_args, **_kwargs):
        return None

    def get(self, url, params, timeout):
        self.calls.append((url, params, timeout))
        return FakeResponse(next(self.pages))


def test_client_sets_required_user_agent():
    session = FakeSession([])
    JolpicaClient(session=session)
    assert session.headers["User-Agent"].startswith("F1ModernDataPlatform/")


def test_iter_pages_uses_limit_and_offset():
    pages = [
        {"MRData": {"total": "3", "limit": "2"}},
        {"MRData": {"total": "3", "limit": "2"}},
    ]
    session = FakeSession(pages)
    client = JolpicaClient(ApiSettings(page_size=2), session=session)

    assert len(list(client.iter_pages("2025/results/"))) == 2
    assert session.calls[0][1] == {"limit": 2, "offset": 0}
    assert session.calls[1][1] == {"limit": 2, "offset": 2}
