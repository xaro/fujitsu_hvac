from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import List, TypeVar


TMode = TypeVar("TMode", bound="Mode")


class Mode(Enum):
    COOL = (0, 2)
    DRY = (1, 3)
    HEAT = (2, 4)

    # The enum values are different depending if we are reading
    # the info or if we are sending a command
    def __init__(self, info_value: int, cmd_value: int) -> None:
        self.info_value = info_value
        self.cmd_value = cmd_value

    def from_info_value(info_value: int) -> TMode:
        for mode in list(Mode):
            if mode.info_value == info_value:
                return mode
        return None


class FanSpeed(IntEnum):
    MIN = 8
    MID = 5
    MAX = 2
    AUTO = 1
    OFF = 0


@dataclass
class HvacInfo:
    circuit: int
    sub_id: int
    powered: bool
    mode: Mode
    temp: float
    fan_speed: FanSpeed
    louver: int

    def from_info(data: List[str]):
        split_display_id = data[2].split("-")
        circuit = int(split_display_id[0])
        sub_id = int(split_display_id[1])
        powered = data[8] == "1"
        mode = Mode.from_info_value(int(data[9]))
        temp = float(data[17]) / 10.0
        fan_speed = FanSpeed(int(data[18]))
        louver = int(data[20])

        return HvacInfo(circuit, sub_id, powered, mode, temp, fan_speed, louver)
