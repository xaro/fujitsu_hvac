import datetime, random, time, requests
from urllib.parse import urljoin
from fujitsu.hvac_info import HvacInfo


HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
}

SESSION_ERROR = "-13"

# Disable warnings as there will always be a self signed cert
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)


def retry_with_backoff(retries=5, backoff_in_seconds=1):
    def rwb(f):
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return f(*args, **kwargs)
                except:
                    if x == retries:
                        raise

                    sleep = backoff_in_seconds * 2**x + random.uniform(0, 1)
                    time.sleep(sleep)
                    x += 1

        return wrapper

    return rwb


class FujitsuHvac:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = None

    def login(self):
        # Ensure that we are not logged in before, if not will get
        # error 4
        self.logout()

        # TODO: Handle failures like bad user/pass
        payload = {
            "username": self.username,
            "password": self.password,
            "logintime": (datetime.datetime.now()).isoformat(),
        }

        session = requests.Session()

        response = session.post(
            self.url("login.cgi"), data=payload, verify=False, headers=HEADERS
        )

        if response.text != "0":
            print("Error logging in: " + response.text)
            raise Exception("Error response " + response.text)

        self.session = session

    def logout(self):
        requests.post(self.url("logout.cgi"), verify=False)
        self.session = None

    @retry_with_backoff(retries=5)
    def get_all_info(self) -> list[HvacInfo]:
        if self.session is None:
            self.login()

        response = self.session.post(
            self.url("getmondata.cgi"),
            data={"FunctionNo": 2, "Argument1": -1},
            headers=HEADERS,
            verify=False,
        ).text

        if response == SESSION_ERROR:
            self.logout()
            print("Session Error -13 found")
            raise Exception("Session error found")

        infos = []
        for info in response.split("\n"):
            if len(info.strip()) == 0:
                break
            infos.append(HvacInfo.from_info(info.split(",")))
        return infos

    def url(self, path: str) -> str:
        return urljoin(self.base_url, path)
