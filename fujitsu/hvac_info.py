from dataclasses import dataclass
from enum import IntEnum
from typing import List


class Mode(IntEnum):
    COOL = 0
    DRY = 1
    HEAT = 2


class FanSpeed(IntEnum):
    MIN = 8
    MID = 5
    MAX = 2
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
        mode = Mode(int(data[9]))
        temp = float(data[17]) / 10.0
        fan_speed = FanSpeed(int(data[18]))
        louver = int(data[20])

        return HvacInfo(circuit, sub_id, powered, mode, temp, fan_speed, louver)
