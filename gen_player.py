# -*- coding: utf-8 -*-
"""OptimalPlayer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NwAL9gbXXE_S1V95yRoE9kR3tSbQIxMO
"""

from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate, gen_cards
from pypokerengine.utils.game_state_utils import restore_game_state
from pypokerengine.engine.hand_evaluator import HandEvaluator
from time import sleep
import time
import pprint
import array
import operator
import random

# track opponent's behaviour, assume opponent balanced / logical at the start
opp_behaviour = {}
opp_behaviour['passive'] = 0
opp_behaviour['aggressive'] = 0
opp_behaviour['balanced'] = 1

# randomly initialise weights w1 and w2 for eval function
# values are floats between 0 and 1
w1 = 0.7 #random.random()
w2 = 0.3 #random.random()
w3 = 0.5
win_prob = 0
round_ctr = 1
opp_raise_threshold = 100
counter = 0

win_rate_history = []
ob_fn_history = []
hand_strength_history = []

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

class Group26Player(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    #start = time.time()
    
    # win_prob is between 0 - 100
    global win_prob
    win_prob = estimate_hole_card_win_rate(75, 2, gen_cards(hole_card), gen_cards(round_state['community_card'])) * 100

    # take into account opponent raise threshold after 20 rounds (when threshold has stabilised)
    if round_ctr > 20:
      # more likely to win than opponent
      if win_prob > opp_raise_threshold:
        if len(valid_actions) != 3:
          return 'call'
        return 'raise'
    
    # ob_fn is between 0 - 100
    global ob_fn
    prob_passive = float(opp_behaviour['passive'])/sum(opp_behaviour.values())
    prob_agg = float(opp_behaviour['aggressive'])/sum(opp_behaviour.values())
    ob_fn = 50 + (prob_passive*50) + (-prob_agg*50)
    #print ob_fn
    
    # final eval_fn is between -100 and 200
    eval_fn = w1*(win_prob) + w2*(ob_fn) + w3*((win_prob-opp_raise_threshold)/100.0)

    global win_rate_history
    global ob_fn_history
    global hand_strength_history

    hand_strength = HandEvaluator.eval_hand(gen_cards(hole_card), gen_cards(round_state['community_card']))
    hand_strength_history.append(hand_strength)
    win_rate_history.append(win_prob)
    ob_fn_history.append(ob_fn)
    
    # always call if no community cards out yet
    if len(round_state['community_card']) == 0:
      if win_prob >= 70:
        if len(valid_actions) != 3:
          return 'call'
        return 'raise'
      else:
        return 'call'

    #end = time.time()
    #timetaken = end-start
    #print 'timetaken:'+ str(timetaken)
    
    curr_behaviour = max(opp_behaviour.iteritems(), key=operator.itemgetter(1))[0]
    
    if eval_fn >= 60:
      if len(valid_actions) != 3:
        return 'call'
      return 'raise'
    elif eval_fn >= 20:
        return 'call'
    else:
        return 'call'   #fold

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):

    if len(hand_info) != 2:
      return
    
    # obtain opponent uuid
    for player in round_state['seats']:
      if player['uuid'] != self.uuid:
        opp_uuid = player['uuid']
        break

    # can see opponent's hand
    if len(hand_info) == 2:
      for user in hand_info:
        if user['uuid'] == opp_uuid:
          opp_hand = user['hand']['card']
    
    # obtain history of opponent actions
    opp_actions = []
    opp_flop = []
    opp_turn = []
    opp_river = []
    for turn in round_state['action_histories']:

      if not turn in round_state['action_histories']:
        return

      for actions in round_state['action_histories'][turn]:
        if actions['uuid'] == opp_uuid and not actions['action'] in ['BIGBLIND','SMALLBLIND']:
          opp_actions.append(actions['action'])
          if turn == 'flop':
            opp_flop.append(actions['action'])
          elif turn == 'turn':
            opp_turn.append(actions['action'])
          elif turn == 'river':
            opp_river.append(actions['action'])

    if len(hand_info) == 2:
      opp_win_prob_first = estimate_hole_card_win_rate(75, 2, gen_cards(opp_hand), gen_cards([])) * 100
      opp_hand_strength_first = HandEvaluator.eval_hand(gen_cards(opp_hand), gen_cards([]))
      opp_win_prob_flop = estimate_hole_card_win_rate(75, 2, gen_cards(opp_hand), gen_cards(round_state['community_card'][:3])) * 100
      opp_hand_strength_flop = HandEvaluator.eval_hand(gen_cards(opp_hand), gen_cards(round_state['community_card'][:3]))
      opp_win_prob_turn = estimate_hole_card_win_rate(75, 2, gen_cards(opp_hand), gen_cards(round_state['community_card'][:4])) * 100
      opp_hand_strength_turn = HandEvaluator.eval_hand(gen_cards(opp_hand), gen_cards(round_state['community_card'][:4]))
      opp_win_prob_river = estimate_hole_card_win_rate(75, 2, gen_cards(opp_hand), gen_cards(round_state['community_card'])) * 100
      opp_hand_strength_river = HandEvaluator.eval_hand(gen_cards(opp_hand), gen_cards(round_state['community_card']))

      global opp_raise_threshold

      if opp_flop != []:
        if 'RAISE' in opp_flop:
          opp_raise_threshold = min(opp_raise_threshold,opp_win_prob_flop)
      if opp_turn != []:
        if 'RAISE' in opp_turn:
          opp_raise_threshold = min(opp_raise_threshold,opp_win_prob_turn)
      if opp_river != []:
        if 'RAISE' in opp_river:
          opp_raise_threshold = min(opp_raise_threshold,opp_win_prob_river)
    
    num_raise = opp_actions.count('RAISE')
    num_call = opp_actions.count('CALL') + opp_actions.count('CHECK')
    num_fold = opp_actions.count('FOLD')
    
    try:
      percentage_raise = float(num_raise)/len(opp_actions)
      percentage_call = float(num_call)/len(opp_actions)
      percentage_fold = float(num_fold)/len(opp_actions)
    except ZeroDivisionError:
      return
    
    # map opponent behaviour

    # draw or opponent won, check if he is passive
    # if our win probability is high and he doesn't raise, likely passive
    if len(winners) == 2 or winners[0]['uuid'] == opp_uuid:
        if win_prob/100.0 > 0.5 and percentage_raise < 0.5:
            opp_behaviour['passive'] += (win_prob/100.0)*2

    # draw or we won, check if he is aggressive
    # if our win probability is low and he keeps raising, likely aggressive
    if len(winners) == 2 or winners[0]['uuid'] == self.uuid:
        if win_prob/100.0 < 0.5 and percentage_raise > 0.5:
            opp_behaviour['aggressive'] += (1-win_prob/100.0)*4

    global round_ctr
    round_ctr += 1

    global win_rate_history
    global ob_fn_history
    global hand_strength_history

    if len(win_rate_history) == 4:
    
      with open('rl_data.txt','a') as outfile:
          outfile.write(str(win_rate_history[0]) + '\n')
          outfile.write(str(hand_strength_history[0]) + '\n')
          outfile.write(str(ob_fn_history[0]) + '\n')
          outfile.write(str(opp_win_prob_first) + '\n')
          outfile.write(str(opp_hand_strength_first) + '\n')

          outfile.write(str(win_rate_history[1]) + '\n')
          outfile.write(str(hand_strength_history[1]) + '\n')
          outfile.write(str(ob_fn_history[1]) + '\n')        
          outfile.write(str(opp_win_prob_flop) + '\n')
          outfile.write(str(opp_hand_strength_flop) + '\n')

          outfile.write(str(win_rate_history[2]) + '\n')
          outfile.write(str(hand_strength_history[2]) + '\n')
          outfile.write(str(ob_fn_history[2]) + '\n')        
          outfile.write(str(opp_win_prob_turn) + '\n')
          outfile.write(str(opp_hand_strength_turn) + '\n')

          outfile.write(str(win_rate_history[3]) + '\n')
          outfile.write(str(hand_strength_history[3]) + '\n')
          outfile.write(str(ob_fn_history[3]) + '\n')        
          outfile.write(str(opp_win_prob_river) + '\n')
          outfile.write(str(opp_hand_strength_river) + '\n')

          if len(winners) == 1 and winners[0]['uuid'] == opp_uuid:
              outfile.write("LOSE\n\n")
          elif len(winners) == 2:
              outfile.write("DRAW\n\n")
          else:
              outfile.write("WIN\n\n")

          global counter
          counter += 1
          if counter % 10000 == 0:
            print 'counter is ' + str(counter)

    win_rate_history = []
    ob_fn_history = []
    hand_strength_history = []
    
def setup_ai():
  return ProbPlayer()
