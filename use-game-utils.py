import itertools
import random
import operator
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate, evaluate_hand
from pypokerengine.engine.hand_evaluator import HandEvaluator

suits = ['H','D','C','S']
nums = [ str(i) for i in range(2,10) ] + ['T','J','Q','K','A']
total_cards = []
for i in suits:
    for j in nums:
        total_cards.append(i+j)
all_poss_2_hand = [list(p) for p in itertools.product(nums, repeat=2)]
new_2_hands = []
for i in all_poss_2_hand:
    if [i[1],i[0]] in all_poss_2_hand and [i[1], i[0]] in new_2_hands:
        continue
    else:
        new_2_hands.append(i)
all_poss_2_hand = new_2_hands
print len(all_poss_2_hand)

samesuits = ['SAME','DIFF']
for samesuit in samesuits:
    for poss_hand in all_poss_2_hand:

        remaining_cards = list(total_cards)

        # not possible because same numbers cannot be same suit
        if (poss_hand[0] == poss_hand[1]) and samesuit == 'SAME':
            continue

        user_card = []
        if samesuit == 'DIFF':
            suit = random.choice(suits)
            user_card.append(suit+poss_hand[0])
            new_suit = random.choice(suits)
            while  (new_suit == suit):
                new_suit = random.choice(suits)
            user_card.append(new_suit+poss_hand[1])
        else:
            suit = random.choice(suits)
            user_card.append(suit+poss_hand[0])
            user_card.append(suit+poss_hand[1])
        hole_card = gen_cards(user_card)

        print(user_card)

        total_win_rate = 0
        for i in range(100000):
            remaining_cards = list(total_cards)
            comm_card = []
            for i in user_card:
                remaining_cards.remove(i)
            for j in range(5):
                choice = random.choice(remaining_cards)
                remaining_cards.remove(choice)
                comm_card.append(choice)
            community_card = gen_cards(comm_card)
            #print(comm_card)
            total_win_rate += estimate_hole_card_win_rate(nb_simulation=1, nb_player=2, hole_card=hole_card, community_card=community_card)
            print comm_card
            
            print HandEvaluator.gen_hand_rank_info(hole_card, community_card)
        print('Total Win Rate:', total_win_rate/100000)
