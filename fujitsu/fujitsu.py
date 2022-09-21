from datetime import datetime
from urllib.parse import urljoin
import requests

HEADERS = {
  'X-Requested-With': 'XMLHttpRequest',
  'Content-Type': 'application/x-www-form-urlencoded',
}


class FujitsuHvac:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def login(self, username: str, password: str) -> requests.Session:
        # TODO: Handle failures like bad user/pass
        payload = {
            "username": username,
            "password": password,
            "logintime": datetime.now().isoformat()
        }

        session = requests.Session()

        session.post(
            urljoin(self.base_url, "login.cgi"),
            data=payload,
            verify=False,
            headers=HEADERS
        )

        return session
