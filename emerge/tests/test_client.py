def test_client_create():
    from emerge.core.client import Client

    client = Client("0.0.0.0", "6558")

    assert client is not None
