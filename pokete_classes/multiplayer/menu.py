"""Contains classes ralated to the mode choosing meni"""

import sys

import scrap_engine as se

from .pc_manager import pc_manager
from .. import loops, roadmap
from ..asset_service.service import asset_service, ValidationException
from ..context import Context
from ..generate import gen_obs
from ..input import get_action, ACTION_DIRECTIONS, Action
from ..input_loops import ask_ok
from ..landscape import MapInteract
from ..multiplayer.modeprovider import modeProvider, Mode
from ..ui.elements import BetterChooseBox
from . import connector
from .communication import com_service


class ModeChooser(BetterChooseBox):
    """The menu to choose modes in"""

    def __init__(self):
        super().__init__(
            1, [
                se.Text("Singleplayer", state="float"),
                se.Text("Multiplayer", state="float"),
                se.Text("Leave...", state="float"),
            ], name="Mode"
        )

    def __choose(self, ctx: Context):
        try:
            while True:
                action = get_action()
                if action.triggers(*ACTION_DIRECTIONS):
                    self.input(action)
                else:
                    if action.triggers(Action.CANCEL):
                        sys.exit()
                    elif action.triggers(Action.ACCEPT):
                        num = self.index[0]
                        if num == 0:
                            modeProvider.mode = Mode.SINGLE
                            asset_service.load_assets_from_p_data()
                        elif num == 1:
                            connector.connector(ctx.with_overview(self))
                            modeProvider.mode = Mode.MULTI
                            com_service()
                        else:
                            sys.exit()
                        # roadmap.RoadMap.check_maps()
                        gen_obs(ctx.figure)
                        ctx.figure.self_add()
                        MapInteract.set_ctx(ctx)
                        pc_manager.set_waiting_users()
                        roadmap.roadmap = roadmap.RoadMap()
                        return
                loops.std(ctx.with_overview(self))
        except ValidationException as e:
            ask_ok(ctx.with_overview(self),
                   f"An error ocured validating game data:\n{e}")
            self.__choose(ctx)

    def __call__(self, ctx: Context):
        """Opens the menu"""
        self.set_ctx(ctx)
        with self:
            self.__choose(ctx)
