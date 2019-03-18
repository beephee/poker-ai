import itertools
import random
import operator

# card format: [num, suit]
NUM_ROUNDS = 5000000
outfile = 'Poker_Probs.txt'
poss_cards = list(range(2,15))
poss_suits = ['D','C','H','S']
all_cards = [list(p) for p in itertools.product(poss_cards, poss_suits)]
all_poss_2_hand = [list(p) for p in itertools.product(poss_cards, repeat=2)]
new_2_hands = []
for i in all_poss_2_hand:
    if [i[1],i[0]] in all_poss_2_hand and [i[1], i[0]] in new_2_hands:
        continue
    else:
        new_2_hands.append(i)
all_poss_2_hand = new_2_hands
full_results = {}
summary_results = {}

def winner(comm_cards, user_cards, opp_cards):

    # user's best hand
    user_hand = comm_cards + user_cards
    user_result, user_highcard1, user_highcard2 = best_hand(user_hand)

##    print(user_hand)
##    print(user_result, user_highcard1, user_highcard2)
    
    # opp's best hand
    opp_hand = comm_cards + opp_cards
    opp_result, opp_highcard1, opp_highcard2 = best_hand(opp_hand)

##    print(opp_hand)
##    print(opp_result, opp_highcard1, opp_highcard2)

    if opp_result == user_result:
        if user_highcard1 > opp_highcard1:
            return 'USER'
        elif user_highcard1 < opp_highcard1:
            return 'OPP'
        else:
            if user_highcard2 > opp_highcard2:
                return 'USER'
            elif user_highcard2 < opp_highcard2:
                return 'OPP'
            else:
                return 'DRAW'

    hand_strength = {}
    hand_strength['HIGHCARD'] = 1
    hand_strength['PAIR'] = 2
    hand_strength['TWO PAIR'] = 3
    hand_strength['TRIPLE'] = 4
    hand_strength['STRAIGHT'] = 5
    hand_strength['FLUSH'] = 6
    hand_strength['FULL HOUSE'] = 7
    hand_strength['FOUR OF A KIND'] = 8
    hand_strength['STRAIGHT FLUSH'] = 9
    hand_strength['ROYAL FLUSH'] = 10

    if hand_strength[user_result] > hand_strength[opp_result]:
        return 'USER'
    elif hand_strength[user_result] < hand_strength[opp_result]:
        return 'OPP'
    
# determines best hand given 7 cards (community + user)
def best_hand(user_hand):

    user_hand = sorted(user_hand, key=operator.itemgetter(0))
    user_nums = [p[0] for p in user_hand]
    user_suits = [p[1] for p in user_hand]

    # check straight
    straight = 0
    straight_highcard = 0
    for i in user_nums:
        if (i+1) in user_nums and (i+2) in user_nums and (i+3) in user_nums and (i+4) in user_nums:
            straight = 1
            straight_highcard = i+4

    # check flush
    suit_with_most = 0
    suit = 0
    flush = 0
    for i in poss_suits:
        counted = user_suits.count(i)
        if counted >= 5:
            flush = 1
            suit = i
            break
    if suit != 0:
        largest = 0
        flush_highcard = 0
        for j in user_hand:
            if j[1] == suit and j[0] > flush_highcard:
                flush_highcard = j[0]

    four_kind = 0
    full_house = 0
    triple = 0
    double_pair = 0
    pair = 0
    four_highcard = 0
    house_highcard = 0
    triple_highcard = 0
    first_pair_highcard = 0
    second_pair_highcard = 0
    single_highcard = 0
    
    # check count (pair/triple/full house)
    counts = sorted([[x,user_nums.count(x)] for x in set(user_nums)], key=operator.itemgetter(1), reverse=True)       # [ [num, count],... ]
    if counts[0][1] == 4:       # four of a kind
        four_highcard = counts[0][0]
        four_kind = 1
        single_highcard = 0
        for num in user_nums:
            if num != four_highcard and num > single_highcard:
                single_highcard = num

    elif counts[0][1] == 3:      # triple
        if counts[1][1] == 3:
            house_highcard = max(counts[0][0], counts[1][0])
            full_house = 1
            pair_highcard = min(counts[0][0], counts[1][0])
        elif counts[1][1] == 2:
            house_highcard = counts[0][0]
            full_house = 1
            if counts[2][1] == 2:
                pair_highcard = max(counts[1][0], counts[2][0])
            else:
                pair_highcard = counts[1][0]
        else:
            triple = 1
            triple_highcard = counts[0][0]

    elif counts[0][1] == 2:      # pair
        all_pairs = []
        for p in counts:
            if p[1] == 2:
                all_pairs.append(p)
        if len(all_pairs) >= 2:
            double_pair = 1
            first_pair_highcard = max(all_pairs, key=lambda z: z[0])
            all_pairs.remove(first_pair_highcard)
            second_pair_highcard = max(all_pairs, key=lambda z: z[0])
        else:
            pair = 1
            first_pair_highcard = max(all_pairs, key=lambda z: z[0])

    else:
            single_highcard = 0
            for num in user_nums:
                if num > single_highcard:
                    single_highcard = num

    if straight == 1 and flush == 1 and straight_highcard == 14:
        return 'ROYAL FLUSH', 14, 0
    elif straight == 1 and flush == 1:
        return 'STRAIGHT FLUSH', straight_highcard, 0
    elif four_kind == 1:
        return 'FOUR OF A KIND', four_highcard, single_highcard
    elif full_house == 1:
        return 'FULL HOUSE', house_highcard, pair_highcard
    elif flush == 1:
        return 'FLUSH', flush_highcard, 0
    elif straight == 1:
        return 'STRAIGHT', straight_highcard, 0
    elif triple == 1:
        return 'TRIPLE', triple_highcard, 0
    elif double_pair == 1:
        return 'TWO PAIR', first_pair_highcard, second_pair_highcard
    elif pair == 1:
        return 'PAIR', first_pair_highcard, 0
    else:
        return 'HIGHCARD', single_highcard, 0

###################################
# play games (cards not from same suit)  #
###################################

for samesuit in range(2):
    for hand in all_poss_2_hand:

        if samesuit == 1 and hand[0]==hand[1]:
            continue

        num_win = 0
        num_lose = 0
        num_draw = 0

        # play for 100000000 rounds per hand
        for game in range(NUM_ROUNDS):

            if game%100000 == 0:
                if samesuit == 0:
                    print('Playing game ' + str(game) + ' for hand ' + str(hand) + ' (DIFFERENT SUITS)')
                else:
                    print('Playing game ' + str(game) + ' for hand ' + str(hand) + ' (SAME SUIT)')
                print('Rounds won:',num_win)

            # set user cards and remove from possible cards
            remaining_cards = list(all_cards)
            user_cards = []
            if samesuit == 1 and hand[0] != hand[1]:           # same suit
                suit = random.choice(poss_suits)
                for i in hand:
                    user_cards.append([i, suit])
                    remaining_cards.remove([i, suit])
            else:                                                                                   # different suits
                orig_suit = random.choice(poss_suits)
                for i in hand:
                    user_cards.append([i, orig_suit])
                    suit = random.choice(poss_suits)
                    while (suit == orig_suit):
                        suit = random.choice(poss_suits)
                    orig_suit = suit

            # set community cards and opponent cards
            comm_cards = []
            opp_cards = []
            for i in range(5):
                next_card = random.choice(remaining_cards)
                comm_cards.append(next_card)
                remaining_cards.remove(next_card)
            for i in range(2):
                next_card = random.choice(remaining_cards)
                opp_cards.append(next_card)
                remaining_cards.remove(next_card)

            result = winner(comm_cards, user_cards, opp_cards)
            if result == 'USER':            # user wins
                num_win += 1
            elif result == 'DRAW':       # user draws
                num_draw += 1
            elif result == 'OPP':           # user loses
                num_lose += 1

        print('')
        if samesuit == 1:
            print('Total statistics for hand ' + str(hand) + ' (SAME SUIT)')
        else:
            print('Total statistics for hand ' + str(hand) + ' (DIFFERENT SUITS)')
        print('Rounds played: ' + str(NUM_ROUNDS))
        print('Rounds won: ' + str(num_win) + ' (' + str(round(100*num_win/NUM_ROUNDS, 2)) + '%)')
        print('Rounds drawn: ' + str(num_draw) + ' (' + str(round(100*num_draw/NUM_ROUNDS, 2)) + '%)')
        print('Rounds lost: ' + str(num_lose) + ' (' + str(round(100*num_lose/NUM_ROUNDS, 2)) + '%)')
        print('')
        
        with open(outfile,'a') as writefile:
            if samesuit == 1:
                writefile.write('Total statistics for hand ' + str(hand) + ' (SAME SUIT)\n')
            else:
                writefile.write('Total statistics for hand ' + str(hand) + ' (DIFFERENT SUITS)\n')
            writefile.write('Rounds played: ' + str(NUM_ROUNDS) + '\n')
            writefile.write('Rounds won: ' + str(num_win) + ' (' + str(round(100*num_win/NUM_ROUNDS, 2)) + '%)\n')
            writefile.write('Rounds drawn: ' + str(num_draw) + ' (' + str(round(100*num_draw/NUM_ROUNDS, 2)) + '%)\n')
            writefile.write('Rounds lost: ' + str(num_lose) + ' (' + str(round(100*num_lose/NUM_ROUNDS, 2)) + '%)\n\n')

        if samesuit == 1:
            full_results[str(hand[0]) + ',' + str(hand[1]) + ',samesuit'] = [num_win, num_draw, num_lose]
            summary_results[str(hand[0]) + ',' + str(hand[1]) + ',samesuit'] = round(100*num_win/NUM_ROUNDS, 2)
        else:
            full_results[str(hand[0]) + ',' + str(hand[1]) + ',diffsuit'] = [num_win, num_draw, num_lose]
            summary_results[str(hand[0]) + ',' + str(hand[1]) + ',diffsuit'] = round(100*num_win/NUM_ROUNDS, 2)

sorted_summary = sorted(summary_results.items(), key=operator.itemgetter(1), reverse=True)
with open(outfile,'a') as writefile:
    print('WINNING PROBABILITIES\n')
    writefile.write('\n\nWINNING PROBABILITIES\n\n')
    for i in sorted_summary:
        print('Hand ' + str(i[0]) + ' : ' + str(i[1]) + '%')
        writefile.write('Hand ' + str(i[0]) + ' : ' + str(i[1]) + '%\n')
            
