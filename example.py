from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer

from Group26Player import Group26Player
from NormalBot import NormalBot
from raise_player import RaisedPlayer
from RL1 import RL1
from RL2 import RL2
#TODO:config the config as our wish
for i in range(1000):
    config = setup_config(max_round=200, initial_stack=10000, small_blind_amount=10)
    
    
    
    config.register_player(name="f1", algorithm=RL1())
    config.register_player(name="FT2", algorithm=RL2())
    
    
    game_result = start_poker(config, verbose=1)
