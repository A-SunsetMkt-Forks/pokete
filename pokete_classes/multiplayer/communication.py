import threading
import socket

import bs_rpc
from pokete_classes.context import Context
from pokete_classes.generate import gen_maps, gen_obs
from pokete_classes.multiplayer import msg
from pokete_classes.multiplayer.exceptions import ConnectionException, \
    VersionMismatchException, UserPresentException, InvalidPokeException
from pokete_classes.multiplayer.msg import position, error, map_info
from pokete_classes.multiplayer.msg.position.update import User
from pokete_classes.multiplayer.pc_manager import pc_manager
from pokete_classes import ob_maps as obmp, roadmap


class CommunicationService:
    def __init__(self):
        self.client: bs_rpc.Client | None = None
        self.saved_pos = ()

    def __subscribe_position_updates(self):
        gen = self.client.call_for_responses(
            position.SubscribePosition({})
        )

        for body in gen():
            match body.get_type():
                case position.UPDATE_TYPE:
                    data: User = body.data
                    pc_manager.set(
                        data["name"],
                        data["position"]["map"],
                        data["position"]["x"],
                        data["position"]["y"],
                    )
                case position.REMOVE_TYPE:
                    data: position.RemoveData = body.data
                    pc_manager.remove(data["user_name"])

    def __call__(self):
        threading.Thread(
            target=self.__subscribe_position_updates,
            daemon=True
        ).start()

    def connect(self, host: str, port: int):
        con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            con.connect((host, port))
        except Exception as e:
            raise ConnectionException(e)

        def listener():
            try:
                self.client.listen(self)
            finally:
                con.close()

        self.client = bs_rpc.Client(con, msg.get_registry())
        threading.Thread(
            target=listener,
            daemon=True
        ).start()

    def handshake(
        self, ctx: Context, user_name,
        version
    ):  # Here COmntext usage outside of the UI context
        """Sends and handles the handshake with the server"""
        resp = self.client.call_for_response(
            msg.Handshake({
                "user_name": user_name,
                "version": version,
                "pokes": [p.dict() for p in ctx.figure.pokes]
            }))
        match resp.get_type():
            case error.VERSION_MISMATCH_TYPE:
                raise VersionMismatchException(resp.data["version"])
            case error.USER_EXISTS_TYPE:
                raise UserPresentException()
            case error.INVALID_POKE_TYPE:
                data: error.InvalidPokeData = resp.data
                raise InvalidPokeException(data["error"])
            case map_info.INFO_TYPE:
                data: map_info.InfoData = resp.data
                obmp.ob_maps = gen_maps(data["assets"]["maps"], fix_center=True)
                gen_obs(
                    data["assets"]["obmaps"],
                    data["assets"]["npcs"],
                    data["assets"]["trainers"],
                    ctx.figure,
                )
                roadmap.roadmap = roadmap.RoadMap(
                    data["assets"]["stations"],
                    data["assets"]["decorations"]
                )
                pos = data["position"]
                self.saved_pos = (
                    ctx.figure.map.name,
                    ctx.figure.oldmap.name,
                    ctx.figure.last_center_map.name,
                    ctx.figure.x,
                    ctx.figure.y,
                )
                ctx.figure.remove()
                ctx.figure.add(obmp.ob_maps[pos["map"]], pos["x"], pos["y"])
                for user in data["users"]:
                    pc_manager.set(
                        user["name"],
                        user["position"]["map"],
                        user["position"]["x"],
                        user["position"]["y"],
                    )
                return data["greeting_text"]

    def pos_update(self, _map, x, y):
        """Sends a position update to the server
        ARGS:
            _map: Name of the map the player is on
            x: X-coordinate
            y: Y-coordinate"""
        resp = self.client.call_for_response(
            position.Update({
                "name": "",
                "position": {
                    "map": _map,
                    "x": x,
                    "y": y,
                },
                "client": None,
                "pokes": [],
            }))


com_service: CommunicationService = CommunicationService()
