import pytest
from venice_sdk.account import APIKeysAPI
from venice_sdk.errors import APIKeyError, VeniceAPIError


def test_api_keys_create_wraps_venice_errors(mocker):
    client = mocker.Mock()
    client.post.side_effect = VeniceAPIError("boom", status_code=500)
    api = APIKeysAPI(client)

    with pytest.raises(APIKeyError) as excinfo:
        api.create("test-key")

    assert isinstance(excinfo.value.__cause__, VeniceAPIError)


def test_api_keys_create_raises_for_partial_payloads(mocker):
    client = mocker.Mock()
    client.post.return_value.json.return_value = {"data": {}}
    api = APIKeysAPI(client)

    with pytest.raises(APIKeyError):
        api.create("test-key")


def test_api_keys_delete_wraps_venice_errors(mocker):
    client = mocker.Mock()
    client.delete.side_effect = VeniceAPIError("boom", status_code=500)
    api = APIKeysAPI(client)

    with pytest.raises(APIKeyError):
        api.delete("key-123")
