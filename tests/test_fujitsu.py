from nis import match
from fujitsu.fujitsu import FujitsuHvac
from fujitsu.hvac_info import FanSpeed, HvacInfo, Mode
import responses
from responses import matchers
from urllib.parse import urljoin

BASE_URL = "https://baseurl.com"


@responses.activate
def test_login():
    mock_login("0", "cookie")
    mock_logout()

    hvac = FujitsuHvac(BASE_URL, "user", "pass")

    hvac.login()

    assert hvac.session.cookies.get("sessionid") == "cookie"


@responses.activate
def test_get_all_info():
    mock_login("0", "cookie")
    mock_logout()
    mock_getmondata(
        """2,514,01-01,0,0,0,0,0,0,0,0,0,0,0,0,0,1,240,0,0,7,8,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-2,-2,0
2,515,01-02,0,0,0,0,0,0,0,0,0,0,0,0,0,1,230,0,0,7,8,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-2,-2,0
2,516,02-01,0,0,0,0,0,0,0,0,0,0,0,0,0,1,230,0,0,7,8,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-2,-2,0"""
    )

    hvac = FujitsuHvac(BASE_URL, "user", "pass")

    info = hvac.get_all_info()

    assert info == [
        HvacInfo(1, 1, False, Mode.COOL, 24.0, FanSpeed.OFF, 7),
        HvacInfo(1, 2, False, Mode.COOL, 23.0, FanSpeed.OFF, 7),
        HvacInfo(2, 1, False, Mode.COOL, 23.0, FanSpeed.OFF, 7),
    ]


@responses.activate
def test_get_all_info_retries():
    mock_login("0", "cookie")
    mock_logout()
    # Add one error that should be retried
    mock_getmondata("-13")
    mock_getmondata(
        "2,514,01-01,0,0,0,0,0,0,0,0,0,0,0,0,0,1,240,0,0,7,8,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-2,-2,0"
    )
    hvac = FujitsuHvac(BASE_URL, "user", "pass")

    info = hvac.get_all_info()

    assert info == [
        HvacInfo(1, 1, False, Mode.COOL, 24.0, FanSpeed.OFF, 7),
    ]


@responses.activate
def test_set_settings():
    mock_login("0", "cookie")
    mock_logout()
    mock_command(
        {
            "arg1": 0,
            "arg2": r"\"2\",\"2\",\"1\",\"1\",\"1\",\"2\",\"1\",\"1\",\"1\",\"53\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\"\r\n",
        },
        "0",
    )
    hvac = FujitsuHvac(BASE_URL, "user", "pass")

    hvac.set_settings(1, 2, new_power_status=True)


def mock_login(body: str, session_id: str):
    responses.add(
        responses.POST,
        urljoin(BASE_URL, "login.cgi"),
        adding_headers={
            "set-cookie": "sessionid=" + session_id + "; " + "path=/; " + ""
        },
        body=body,
    )


def mock_logout():
    responses.add(
        responses.POST,
        urljoin(BASE_URL, "logout.cgi"),
        adding_headers={"set-cookie": "sessionid=; " + "path=/; " + ""},
    )


def mock_getmondata(body: str):
    responses.add(
        responses.POST,
        urljoin(BASE_URL, "getmondata.cgi"),
        body=body,
    )


def mock_command(request_body: dict, body: str):
    responses.add(
        responses.POST,
        urljoin(BASE_URL, "command.cgi"),
        body=body,
        match=[matchers.json_params_matcher(request_body)],
    )
