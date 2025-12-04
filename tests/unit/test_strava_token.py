"""
Tests para el módulo strava_token_1 (legacy).

NOTA: Este es un módulo legacy que será reemplazado.
Los tests usan mocks para evitar llamadas reales a la API de Strava.
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import Mock
from py_strava.strava.strava_token_1 import (
    refreshToken,
    getTokenFromFile,
    openTokenFile,
    saveTokenFile,
)


class TestStravaToken:
    """Tests legacy refactorizados con mocks."""

    def setup_method(self):
        """Setup para cada test."""
        self.STRAVA_TOKEN_JSON = "json/test/strava_tokens.json"
        self.access_token = "f4e2939500ffa174654f91a9177e05b87d217938"
        self.expires_at = 1613511684
        self.expires_in = 21600
        self.refresh_token = "e518c071c6bed349dbfb9b46e1e75efab02e4ff1"
        self.strava_tokens_json = {
            "token_type": "Bearer",
            "access_token": "f4e2939500ffa174654f91a9177e05b87d217938",
            "expires_at": 1613511684,
            "expires_in": 21600,
            "refresh_token": "e518c071c6bed349dbfb9b46e1e75efab02e4ff1",
        }

    def test_get_token_from_file(self):
        """Verificar que getTokenFromFile lee el archivo correctamente."""
        result = getTokenFromFile(self.STRAVA_TOKEN_JSON)
        assert result == self.strava_tokens_json

    def test_no_refresh_token_with_mock(self, mocker, tmp_path):
        """Verificar refresh_token cuando el token está expirado (usa mock)."""
        # Crear archivo temporal de tokens
        temp_token_file = tmp_path / "strava_tokens.json"
        with open(temp_token_file, "w") as f:
            json.dump(self.strava_tokens_json, f)

        # Mock de time.time para simular que el token está expirado
        mocker.patch("time.time", return_value=self.expires_at + 1000)

        # Mock de requests.post para simular respuesta de Strava API
        mock_response = Mock()
        mock_response.json.return_value = {
            **self.strava_tokens_json,
            "access_token": "new_token",
            "refresh_token": self.refresh_token,
        }
        mocker.patch("py_strava.strava.strava_token_1.requests.post", return_value=mock_response)

        # Ejecutar con archivo temporal
        strava_tokens = refreshToken(getTokenFromFile(str(temp_token_file)), str(temp_token_file))

        # Verificar que el refresh_token se mantuvo
        assert strava_tokens["refresh_token"] == self.refresh_token

    def test_refresh_token_with_mock(self, mocker, tmp_path):
        """Verificar que refreshToken retorna access_token actualizado (usa mock)."""
        # Crear archivo temporal de tokens
        temp_token_file = tmp_path / "strava_tokens.json"
        with open(temp_token_file, "w") as f:
            json.dump(self.strava_tokens_json, f)

        # Mock de time.time para simular que el token está expirado
        mocker.patch("time.time", return_value=self.expires_at + 1000)

        # Mock de requests.post para simular respuesta de Strava API
        mock_response = Mock()
        mock_response.json.return_value = {
            **self.strava_tokens_json,
            "access_token": self.access_token,
        }
        mocker.patch("py_strava.strava.strava_token_1.requests.post", return_value=mock_response)

        # Ejecutar con archivo temporal
        strava_tokens = refreshToken(getTokenFromFile(str(temp_token_file)), str(temp_token_file))

        # Verificar que el access_token es el esperado
        assert strava_tokens["access_token"] == self.access_token


class TestStravaTokenAdvanced:
    """Tests adicionales con cobertura extendida."""

    @pytest.fixture
    def token_file_path(self, tmp_path):
        """Crea un archivo temporal de tokens para tests."""
        token_file = tmp_path / "strava_tokens.json"
        return str(token_file)

    @pytest.fixture
    def valid_token_data(self):
        """Retorna datos de token válido (no expirado)."""
        return {
            "token_type": "Bearer",
            "access_token": "valid_access_token_123",
            "expires_at": int(time.time()) + 3600,  # Expira en 1 hora
            "expires_in": 3600,
            "refresh_token": "valid_refresh_token_456",
        }

    @pytest.fixture
    def expired_token_data(self):
        """Retorna datos de token expirado."""
        return {
            "token_type": "Bearer",
            "access_token": "expired_access_token",
            "expires_at": int(time.time()) - 3600,  # Expiró hace 1 hora
            "expires_in": 21600,
            "refresh_token": "old_refresh_token",
        }

    @pytest.fixture
    def refreshed_token_response(self):
        """Retorna respuesta mock de API al refrescar token."""
        return {
            "token_type": "Bearer",
            "access_token": "new_access_token_789",
            "expires_at": int(time.time()) + 7200,
            "expires_in": 7200,
            "refresh_token": "new_refresh_token_abc",
        }

    def test_save_token_file(self, token_file_path, valid_token_data):
        """Verificar que saveTokenFile escribe correctamente el archivo JSON."""
        # Guardar tokens
        saveTokenFile(valid_token_data, token_file_path)

        # Verificar que se guardó correctamente
        assert Path(token_file_path).exists()

        with open(token_file_path) as f:
            saved_data = json.load(f)

        assert saved_data == valid_token_data

    def test_refresh_token_when_expired(
        self, token_file_path, expired_token_data, refreshed_token_response, mocker
    ):
        """Verificar que refreshToken actualiza el token cuando está expirado."""
        # Mock de requests.post para simular respuesta de Strava API
        mock_response = Mock()
        mock_response.json.return_value = refreshed_token_response

        mock_post = mocker.patch("py_strava.strava.strava_token_1.requests.post")
        mock_post.return_value = mock_response

        # Guardar token expirado
        with open(token_file_path, "w") as f:
            json.dump(expired_token_data, f)

        # Ejecutar refresh
        result = refreshToken(expired_token_data, token_file_path)

        # Verificar que se hizo la llamada a la API
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["url"] == "https://www.strava.com/oauth/token"
        assert call_kwargs["data"]["grant_type"] == "refresh_token"
        assert call_kwargs["data"]["refresh_token"] == expired_token_data["refresh_token"]

        # Verificar que se retorna el nuevo token
        assert result == refreshed_token_response
        assert result["access_token"] == "new_access_token_789"

        # Verificar que se guardó el nuevo token en el archivo
        with open(token_file_path) as f:
            saved_data = json.load(f)
        assert saved_data == refreshed_token_response

    def test_refresh_token_when_not_expired(self, token_file_path, valid_token_data, mocker):
        """Verificar que refreshToken NO actualiza el token cuando aún es válido."""
        # Mock de requests.post (no debería llamarse)
        mock_post = mocker.patch("py_strava.strava.strava_token_1.requests.post")

        # Ejecutar refresh con token válido
        result = refreshToken(valid_token_data, token_file_path)

        # Verificar que NO se hizo llamada a la API
        mock_post.assert_not_called()

        # Verificar que se retorna el mismo token
        assert result == valid_token_data
        assert result["access_token"] == "valid_access_token_123"

    def test_open_token_file_prints_content(self, token_file_path, valid_token_data, capsys):
        """Verificar que openTokenFile imprime el contenido del archivo."""
        # Guardar datos
        with open(token_file_path, "w") as f:
            json.dump(valid_token_data, f)

        # Ejecutar función que imprime
        openTokenFile(token_file_path)

        # Capturar output
        captured = capsys.readouterr()

        # Verificar que se imprimió el diccionario
        assert "valid_access_token_123" in captured.out

    def test_get_token_from_nonexistent_file_raises_error(self):
        """Verificar que getTokenFromFile lanza error si el archivo no existe."""
        with pytest.raises(FileNotFoundError):
            getTokenFromFile("/path/that/does/not/exist.json")
