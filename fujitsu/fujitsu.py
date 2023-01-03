import datetime, random, time, requests, asyncio
from urllib.parse import urljoin
from fujitsu.hvac_info import HvacInfo, Mode, FanSpeed


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

    async def login(self):
        # Ensure that we are not logged in before, if not will get
        # error 4
        await self.logout()

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

    async def logout(self):
        requests.post(self.url("logout.cgi"), verify=False)
        self.session = None

    @retry_with_backoff(retries=5)
    async def get_all_info(self) -> list[HvacInfo]:
        if self.session is None:
            await self.login()

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

    # @retry_with_backoff(retries=3)
    async def set_settings(
        self,
        circuit: int,
        sub_id: int,
        new_power_status: bool = None,
        new_mode: Mode = None,
        new_fan_speed: FanSpeed = None,
        new_temp: float = None,
    ):
        if self.session is None:
            await self.login()

        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
        }

        response = self.session.post(
            self.url("command.cgi"),
            data={
                "arg1": 0,
                "arg2": self.to_command_str(
                    circuit, sub_id, new_power_status, new_mode, new_fan_speed, new_temp
                ),
            },
            headers=headers,
            verify=False,
        ).text

        if response != "0":
            self.logout()
            print("Error: " + response)
            raise Exception("Error found")

    def url(self, path: str) -> str:
        return urljoin(self.base_url, path)

    def to_command_str(
        self,
        circuit: int,
        sub_id: int,
        new_power_status: bool = None,
        new_mode: Mode = None,
        new_fan_speed: FanSpeed = None,
        new_temp: float = None,
    ):
        cmd = [
            circuit + 1,
            sub_id + 1,
            self.__to_change_str(new_power_status),
            0 if new_power_status else self.__bool_to_command_str(new_power_status),
            self.__to_change_str(new_mode),
            0 if new_mode is None else new_mode.cmd_value,
            self.__to_change_str(new_fan_speed),
            0 if new_fan_speed is None else new_fan_speed.value,
            self.__to_change_str(new_temp),
            0 if new_temp is None else int(new_temp * 2),
            0,  # Changed air vert?
            0,  # Air vert
            0,
            0,  # Changed air hrz
            0,  # Air hrz
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,  # Cold or hot tmp change
            0,  # Cold temp
            0,  # Hot temp
        ]
        return ",".join([r"\"" + str(val) + r"\"" for val in cmd]) + r"\r\n"

    def __to_change_str(self, changed_attr) -> int:
        return self.__bool_to_command_str(changed_attr is None)

    def __bool_to_command_str(self, changed_attr) -> int:
        return 1 if changed_attr else 0
