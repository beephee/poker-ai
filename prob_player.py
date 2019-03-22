from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate, gen_cards
from pypokerengine.utils.game_state_utils import restore_game_state
from time import sleep
import time
import pprint
import array

p1hand = []
p2hand = []

preflop_offsuit = {"AA" : 84.93, "KK" : 82.11, "QQ" : 79.63, "JJ" : 77.15,
                   "TT" : 74.66, "99" : 71.66, "88" : 68.71, "77" : 65.72,
                   "AK" : 64.46, "AQ" : 63.50, "AJ" : 62.53, "66" : 62.70,
                   "AT" : 61.56, "KQ" : 60.43, "A9" : 59.44, "KJ" : 59.44,
                   "55" : 59.64, "A8" : 58.37, "KT" : 58.49, "A7" : 57.16,
                   "QJ" : 56.90, "K9" : 56.40, "A6" : 55.87, "A5" : 55.74,
                   "QT" : 55.94, "44" : 56.25, "A4" : 54.73, "K8" : 54.43,
                   "A3" : 53.85, "Q9" : 53.86, "JT" : 53.82, "K7" : 53.41,
                   "A2" : 52.94, "K6" : 52.29, "33" : 52.83, "Q8" : 51.93,
                   "K5" : 51.25, "J9" : 51.63, "K4" : 50.22, "Q7" : 49.90,
                   "T9" : 49.81, "J8" : 49.71, "K3" : 49.33, "Q6" : 48.99,
                   "K2" : 48.42, "22" : 48.38, "Q5" : 47.95, "T8" : 47.81,
                   "J7" : 47.72, "Q4" : 46.92, "Q3" : 46.02, "98" : 46.06,
                   "T7" : 45.82, "J6" : 45.71, "Q2" : 45.10, "J5" : 44.90,
                   "97" : 44.07, "J4" : 43.86, "T6" : 43.84, "J3" : 42.96,
                   "87" : 42.69, "96" : 42.10, "J2" : 42.04, "T5" : 41.85,
                   "T4" : 41.05, "86" : 40.69, "95" : 40.13, "T3" : 40.15,
                   "76" : 39.95, "T2" : 39.23, "85" : 38.74, "94" : 38.08,
                   "75" : 37.67, "93" : 37.42, "65" : 37.01, "84" : 36.70,
                   "92" : 36.51, "74" : 35.66, "54" : 35.07, "64" : 35.00,
                   "83" : 34.74, "82" : 34.08, "73" : 33.71, "53" : 33.16,
                   "63" : 33.06, "43" : 32.06, "72" : 31.71, "52" : 31.19,
                   "62" : 31.07, "42" : 30.11, "32" : 29.23}

preflop_samesuit = {"AK" : 66.21, "AQ" : 65.31, "AJ" : 64.39, "AT" : 62.22,
                    "KQ" : 62.40, "A9" : 61.50, "KJ" : 61.47, "A8" : 60.50,
                    "KT" : 60.58, "A7" : 59.38, "QJ" : 59.07, "K9" : 58.63,
                    "A6" : 58.17, "A5" : 58.06, "QT" : 58.17, "A4" : 57.13,
                    "K8" : 56.79, "A3" : 56.33, "Q9" : 56.22, "K7" : 55.84,
                    "JT" : 56.15, "A2" : 56.15, "K6" : 54.80, "Q8" : 54.41,
                    "K5" : 53.83, "J9" : 54.11, "K4" : 52.88, "Q7" : 52.52,
                    "K3" : 52.07, "T9" : 52.37, "J8" : 52.31, "Q6" : 51.67,
                    "K2" : 51.23, "Q5" : 50.71, "T8" : 50.50, "J7" : 50.45,
                    "Q4" : 49.76, "Q3" : 48.93, "98" : 48.85, "T7" : 48.65,
                    "J6" : 48.57, "Q2" : 48.10, "J5" : 47.82, "97" : 46.99,
                    "J4" : 46.86, "T6" : 46.80, "J3" : 46.04, "87" : 45.68,
                    "96" : 45.15, "J2" : 45.20, "T5" : 44.93, "T4" : 44.20,
                    "86" : 43.81, "95" : 43.31, "T3" : 43.37, "76" : 42.82,
                    "T2" : 42.54, "85" : 41.99, "94" : 41.40, "75" : 40.97,
                    "93" : 40.80, "65" : 40.34, "84" : 40.34, "92" : 39.97,
                    "74" : 39.10, "54" : 38.53, "64" : 38.48, "83" : 38.28,
                    "82" : 37.67, "73" : 37.30, "53" : 36.75, "63" : 36.68,
                    "43" : 35.72, "72" : 35.43, "52" : 34.92, "62" : 34.83,
                    "42" : 33.91, "32" : 33.09}

# preflop odds : credits goes to https://caniwin.com/texasholdem/preflop/heads-up.php 

def pattern(hole_card):
    if hole_card[0][0] == hole_card[1][0]:     # suits match
        suit = 'same'
    else:
        suit = 'diff'
    nums = hole_card[0][1] + hole_card[1][1]
    return suit, nums

class ProbPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    start = time.time()
    #print hole_card
    #print round_state['community_card']
    prob = estimate_hole_card_win_rate(150, 2, gen_cards(hole_card), gen_cards(round_state['community_card']))
    prob2 = estimate_hole_card_win_rate(150, 2, gen_cards(hole_card), gen_cards(round_state['community_card']))
    #print prob
    '''
    suit, nums = pattern(hole_card)
    if suit == 'same':
        if nums in preflop_samesuit:
            prob = preflop_samesuit[nums]
        else:
            prob = preflop_samesuit[nums[1] + nums[0]]
    else:
        if nums in preflop_offsuit:
            prob = preflop_offsuit[nums]
        else:
            prob = preflop_offsuit[nums[1] + nums[0]]
    print prob
    '''
#    studyPlayer()
#    if round_state['street'] == 'river':
#        print round_state
#        studyPlayer()

    end = time.time()
    timetaken = end-start
#    print 'timetaken:'+ str(timetaken)

    if len(round_state['community_card']) == 0:
        return 'call'
    
    if prob >= 0.75:
        return 'raise'
    elif prob >= 0.3:
        return 'call'
    else:
        return 'fold'

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass
  
  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass
  
  def preflop_odds(card1,card2):
    temp = card1[1] + card2[1];
    if (card1[0] == card2[0]):
        return (preflop_samesuit.get(temp))
    else:
        return (preflop_offsuit.get(temp))

def setup_ai():
  return ProbPlayer()
