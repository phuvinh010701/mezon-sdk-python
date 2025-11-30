"""
Copyright 2022 The Mezon Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import jwt
import time
from typing import Optional, Dict, Any

from .models import ApiSession


class Session:
    def __init__(self, api_session: ApiSession):
        """
        Initialize a Session from an API session response.

        Args:
            api_session: Dictionary containing token, refresh_token, and user_id
        """
        self.token: str = api_session.token
        self.refresh_token: str = api_session.refresh_token
        self.user_id: Optional[str] = api_session.user_id
        self.api_url: Optional[str] = api_session.api_url
        self.id_token: Optional[str] = api_session.id_token
        self.created_at: int = int(time.time())

        self.update(self.token, self.refresh_token)

    def is_expired(self, currenttime: int) -> bool:
        """
        Check if the session has expired.

        Args:
            currenttime: Current UNIX timestamp in seconds

        Returns:
            True if expired, False otherwise
        """
        if self.expires_at is None:
            return True
        return (self.expires_at - currenttime) < 0

    def is_refresh_expired(self, currenttime: int) -> bool:
        """
        Check if the refresh token has expired.

        Args:
            currenttime: Current UNIX timestamp in seconds

        Returns:
            True if expired, False otherwise
        """
        if self.refresh_expires_at is None:
            return True
        return (self.refresh_expires_at - currenttime) < 0

    def update(self, token: str, refresh_token: Optional[str] = None) -> None:
        """
        Update the session with new tokens.

        Args:
            token: The JWT token
            refresh_token: The refresh JWT token (optional)

        Raises:
            ValueError: If JWT tokens are invalid
        """
        payload = jwt.decode(
            token, options={"verify_signature": False, "verify_exp": False}
        )
        self.expires_at = int(payload["exp"])
        self.token = token
        self.vars = payload.get("vrs", {})

        if refresh_token:
            r_payload = jwt.decode(
                refresh_token, options={"verify_signature": False, "verify_exp": False}
            )
            self.refresh_expires_at = int(r_payload["exp"])
            self.refresh_token = refresh_token

    @classmethod
    def restore(cls, session: Dict[str, Any]) -> "Session":
        """
        Restore a session from a dictionary.

        Args:
            session: Session dictionary

        Returns:
            Session instance
        """
        return cls(session)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session to dictionary for serialization.

        Returns:
            Dictionary representation of session
        """
        return {
            "token": self.token,
            "refresh_token": self.refresh_token,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "refresh_expires_at": self.refresh_expires_at,
            "vars": self.vars,
            "api_url": self.api_url,
        }
