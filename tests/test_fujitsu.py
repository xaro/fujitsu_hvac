from urllib import response
from fujitsu.fujitsu import FujitsuHvac
import responses
from urllib.parse import urljoin

BASE_URL = "https://baseurl.com"


@responses.activate
def test_login():
    responses.add(responses.POST,
                  urljoin(BASE_URL, "login.cgi"),
                  adding_headers={
                      "set-cookie": "sessionid=cookie; " +
                      "path=/; " +
                      ""
                  })

    hvac = FujitsuHvac(BASE_URL)

    session = hvac.login("user", "password")

    assert session.cookies.get('sessionid') == 'cookie'
