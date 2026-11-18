import pytest
import requests
from unittest.mock import patch, Mock

from sigpac_tools import http


class TestSharedSession:
    def test_module_level_session_exists(self):
        assert isinstance(http._session, requests.Session)

    @patch("sigpac_tools.http._session")
    def test_get_uses_shared_session(self, mock_session):
        mock_response = Mock()
        mock_session.get.return_value = mock_response

        result = http.get("https://example.com/test")

        mock_session.get.assert_called_once_with("https://example.com/test")
        assert result is mock_response


if __name__ == "__main__":
    pytest.main()
