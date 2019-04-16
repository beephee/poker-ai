from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from Group26 import Group26Player
from Group26_copy import Group26CopyPlayer
from passive_player import PassivePlayer
from honest_player import HonestPlayer
from normal_bot import NormalBot

#TODO:config the config as our wish
config = setup_config(max_round=100, initial_stack=100000, small_blind_amount=10)



config.register_player(name="FT1", algorithm=Group26Player())
config.register_player(name="FT2", algorithm=Group26CopyPlayer())


game_result = start_poker(config, verbose=1)
