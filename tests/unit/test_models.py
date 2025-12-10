import pytest
from venice_sdk.models import ModelsAPI
from venice_sdk.errors import VeniceAPIError


def test_models_api_validate_handles_venice_errors(mocker):
    api = ModelsAPI(client=mocker.Mock())
    mocker.patch.object(api, "get", side_effect=VeniceAPIError("boom", status_code=404))

    assert api.validate("llama") is False


def test_models_api_validate_propagates_unexpected_errors(mocker):
    api = ModelsAPI(client=mocker.Mock())
    mocker.patch.object(api, "get", side_effect=RuntimeError("explode"))

    with pytest.raises(RuntimeError):
        api.validate("llama")
