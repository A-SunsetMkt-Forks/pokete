# DO NOT EDIT!
# This code was auto generated by the `protoc-gen-pokete-resources-python` plugin,
# part of the pokete project, by <lxgr@protonmail.com>
from typing import TypedDict


class AttackDict(TypedDict):
    name: str
    factor: float
    action: str | None
    world_action: str
    move: list[str]
    miss_chance: float
    min_lvl: int
    desc: str
    types: list[str]
    effect: str | None
    is_generic: bool
    ap: int
    

class Attack:
    def __init__(
        self,
        name: str,
        factor: float,
        action: str | None,
        world_action: str,
        move: list[str],
        miss_chance: float,
        min_lvl: int,
        desc: str,
        types: list[str],
        effect: str | None,
        is_generic: bool,
        ap: int
    ):
        self.name: str = name
        self.factor: float = factor
        self.action: str | None = action
        self.world_action: str = world_action
        self.move: list[str] = move
        self.miss_chance: float = miss_chance
        self.min_lvl: int = min_lvl
        self.desc: str = desc
        self.types: list[str] = types
        self.effect: str | None = effect
        self.is_generic: bool = is_generic
        self.ap: int = ap
        
    @classmethod
    def from_dict(cls, _d: AttackDict | None) -> "Attack" | None:
        if _d is None:
            return None
        return cls(
            name=_d["name"],
            factor=_d["factor"],
            action=_d.get("action", None),
            world_action=_d["world_action"],
            move=_d["move"],
            miss_chance=_d["miss_chance"],
            min_lvl=_d["min_lvl"],
            desc=_d["desc"],
            types=_d["types"],
            effect=_d.get("effect", None),
            is_generic=_d["is_generic"],
            ap=_d["ap"],
        )
