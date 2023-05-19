def test_client_create():
    from emerge.core.client import Z0RPCClient as Client

    client = Client("0.0.0.0", "5558")

    assert client is not None
