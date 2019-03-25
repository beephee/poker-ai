from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards


# Estimate the ratio of winning games given the current state of the game
def estimate_win_rate(nb_simulation, nb_player, hole_card, community_card=None):
    if not community_card: community_card = []

    # Make lists of Card objects out of the list of cards
    community_card = gen_cards(community_card)
    hole_card = gen_cards(hole_card)

    # Estimate the win count by doing a Monte Carlo simulation
    win_count = sum([montecarlo_simulation(nb_player, hole_card, community_card) for _ in range(nb_simulation)])
    return 1.0 * win_count / nb_simulation


def montecarlo_simulation(nb_player, hole_card, community_card):
    # Do a Monte Carlo simulation given the current state of the game by evaluating the hands
    community_card = _fill_community_card(community_card, used_card=hole_card + community_card)
    unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
    opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
    opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
    my_score = HandEvaluator.eval_hand(hole_card, community_card)
    return 1 if my_score >= max(opponents_score) else 0


class NormalBot(BasePokerPlayer):
    def __init__(self):
        super(NormalBot, self).__init__()
        self.aggressive = []
        self.num_players = 2

#        self.wins = 0
#        self.losses = 0

    def declare_action(self, valid_actions, hole_card, round_state):
        # Estimate the win rate
        win_rate = estimate_win_rate(100, self.num_players, hole_card, round_state['community_card'])

        # thresholds
        aggressive = [0.2,0.4,0.65]
        balanced = [0.3,0.5,0.75]
        passive = [0.4,0.6,0.85]
        
        #change this variable to choose strategy
        strategy = 'balanced'
        
        can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
        can_fold = len([item for item in valid_actions if item['action'] == 'fold']) > 0

        # If the win rate is large enough, then raise
        
        if win_rate > locals()[strategy][1]:
            if win_rate > locals()[strategy][2]:
                action = 'raise'
            else:
                action = 'call'
        else:
            if win_rate > locals()[strategy][0]:
                action = 'call' if can_call else 'fold'
            else:
                action = 'fold' if can_fold else 'call'

        return action

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass
    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
#        is_winner = self.uuid in [item['uuid'] for item in winners]
#        self.wins += int(is_winner)
#        self.losses += int(not is_winner)

        pass
def setup_ai():
    return DataBloggerBot
