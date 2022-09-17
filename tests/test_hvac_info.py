from fujitsu.hvac_info import FanSpeed, HvacInfo, Mode


def test_from_info():
    actual = HvacInfo.from_info(["2", "514", "01-01", "0", "0", "0", "0", "0", "1", "2", "0", "0", "0", "0", "0", "0", "1", "230", "8", "0", "7", "8", "0", "0", "0", "0", "0", "0", "0", "1",
                       "1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "-2", "-2", "0"])

    assert actual == HvacInfo(1, 1, True, Mode.HEAT, 23, FanSpeed.MIN, 7)
