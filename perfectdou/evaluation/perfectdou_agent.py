import os
import numpy as np
import onnxruntime as ort
from perfectdou.env.encode import (
    encode_obs_landlord,
    encode_obs_peasant,
    _decode_action,
)
from perfectdou.env.game import bombs


def _load_model(position):
    model_dir = "{}/../model/perfectdou".format(os.path.dirname(__file__))
    sess_options = ort.SessionOptions()
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    sess_options.inter_op_num_threads = 1
    sess_options.intra_op_num_threads = 1
    sess_options.log_severity_level = 3
    return ort.InferenceSession("{}/{}.onnx".format(model_dir, position), sess_options)


RLCard2EnvCard = {
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
    "2": 17,
    "B": 20,
    "R": 30,
}


class PerfectDouAgent:
    def __init__(self, position):
        self.model = _load_model(position)
        self.position = position
        self.bomb_num = 0
        self.control = 0
        self.have_bomb = 0

    def act(self, infoset):
        if infoset.player_position == "landlord":
            obs = encode_obs_landlord(infoset)
        elif infoset.player_position == "landlord_up":
            obs = encode_obs_peasant(infoset)
        elif infoset.player_position == "landlord_down":
            obs = encode_obs_peasant(infoset)
        input_name = self.model.get_inputs()[0].name
        input_data = np.concatenate(
            [obs["x_no_action"].flatten(), obs["legal_actions_arr"].flatten()]
        ).reshape(1, -1)
        logit = self.model.run(["action_logit"], {input_name: input_data})
        action_id = np.argmax(logit)
        action = _decode_action(action_id, obs["current_hand"], obs["actions"])
        action = [] if action == "pass" else [RLCard2EnvCard[e] for e in action]
        return action
