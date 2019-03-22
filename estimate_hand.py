from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

nb_simulation = 1000
nb_player = 3
hole_card = gen_cards(['H4', 'D4'])
community_card = gen_cards([])
def estimate_hand_strength(nb_simulation, nb_player, hole_card, community_card):
    simulation_results = []
    for i in range(nb_simulation):
        opponents_cards = []
        for j in range(nb_player-1):  # nb_opponents = nb_player - 1
            opponents_cards.append(draw_cards_from_deck(num=2))
        nb_need_community = 5 - len(community_card)
        community_card.append(draw_cards_from_deck(num=nb_need_community))
        result = observe_game_result(hole_card, community_card, opponents_cards)  # return 1 if win else 0
        simulation_results.append(result)
    average_win_rate = 1.0 * sum(simulation_results) / len(simulation_results)
    return average_win_rate
print(estimate_hole_card_win_rate(nb_simulation=1000, nb_player=3, hole_card=hole_card, community_card=community_card))