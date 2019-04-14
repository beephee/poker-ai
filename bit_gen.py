from sklearn.model_selection import train_test_split
import operator
from keras.callbacks import EarlyStopping
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import Embedding
from keras.preprocessing.text import Tokenizer
import numpy as np

# conversion dictionaries

poss_suits = ['D','C','H','S']

value_convert = {}
value_convert['2'] = 2
value_convert['3'] = 3
value_convert['4'] = 4
value_convert['5'] = 5
value_convert['6'] = 6
value_convert['7'] = 7
value_convert['8'] = 8
value_convert['9'] = 9
value_convert['T'] = 10
value_convert['J'] = 11
value_convert['Q'] = 12
value_convert['K'] = 13
value_convert['A'] = 14

convert_binary = {}
convert_binary[0] = '0000'
convert_binary[2] = '0010'
convert_binary[3] = '0011'
convert_binary[4] = '0100'
convert_binary[5] = '0101'
convert_binary[6] = '0110'
convert_binary[7] = '0111'
convert_binary[8] = '1000'
convert_binary[9] = '1001'
convert_binary[10] = '1010'
convert_binary[11] = '1011'
convert_binary[12] = '1100'
convert_binary[13] = '1101'
convert_binary[14] = '1110'

hand_strength = {}
hand_strength['HIGHCARD'] = '00000000'
hand_strength['PAIR'] = '00000001'
hand_strength['TWO PAIR'] = '00000010'
hand_strength['TRIPLE'] = '00000100'
hand_strength['STRAIGHT'] = '00001000'
hand_strength['FLUSH'] = '00010000'
hand_strength['FULL HOUSE'] = '00100000'
hand_strength['FOUR OF A KIND'] = '01000000'
hand_strength['STRAIGHT FLUSH'] = '10000000'

# write end of file to stop checking
with open('results.txt','a') as writefile:
    writefile.write('EOF\n')

def train_model(input_size, vocab_size, x_train, y_train, num_epochs, batch_size):
    
    early_stopping = EarlyStopping(monitor='loss', patience=2)
    optim = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=True)

    model = Sequential()
    model.add(Dense(24, input_dim = input_size, activation = 'relu'))
    model.add(Dense(12, activation = 'relu'))
    model.add(Dense(1, activation = 'relu'))
    model.compile(loss = 'sparse_categorical_crossentropy', optimizer = optim, metrics = ['accuracy'])
    model.fit(x_train, y_train, epochs = num_epochs, verbose = 2, batch_size = batch_size, validation_split = 0.2)#, callbacks = [early_stopping])
    
    return model

# determines best hand given cards (community + user)
def best_hand(user_hand):

    split_cards = []
    for i in user_hand:
        split_cards.append([i[0], value_convert[i[1]]])

    user_hand = split_cards
    user_hand = sorted(user_hand, key=operator.itemgetter(1))
    user_nums = [p[1] for p in user_hand]
    user_suits = [p[0] for p in user_hand]

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
            if len(counts) > 2 and counts[2][1] == 2:
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
            first_pair_highcard = first_pair_highcard[0]
            second_pair_highcard = max(all_pairs, key=lambda z: z[0])[0]
        else:
            pair = 1
            first_pair_highcard = max(all_pairs, key=lambda z: z[0])[0]

    else:
            single_highcard = 0
            second_highcard = 0
            for num in user_nums:
                if num > single_highcard:
                    single_highcard = num
            if user_nums.count(single_highcard) >= 2:
                second_highcard = single_highcard
            else:
                for num in user_nums:
                    if num > second_highcard and num != single_highcard:
                        second_highcard = num

    if straight == 1 and flush == 1:
        return hand_strength['STRAIGHT FLUSH'] + convert_binary[straight_highcard] + convert_binary[0]
    elif four_kind == 1:
        return hand_strength['FOUR OF A KIND'] + convert_binary[four_highcard] + convert_binary[single_highcard]
    elif full_house == 1:
        return hand_strength['FULL HOUSE'] + convert_binary[house_highcard] + convert_binary[pair_highcard]
    elif flush == 1:
        return hand_strength['FLUSH'] + convert_binary[flush_highcard] + convert_binary[0]
    elif straight == 1:
        return hand_strength['STRAIGHT'] + convert_binary[straight_highcard] + convert_binary[0]
    elif triple == 1:
        return hand_strength['TRIPLE'] + convert_binary[triple_highcard] + convert_binary[0]
    elif double_pair == 1:
        return hand_strength['TWO PAIR'] + convert_binary[first_pair_highcard] + convert_binary[second_pair_highcard]
    elif pair == 1:
        return hand_strength['PAIR'] + convert_binary[first_pair_highcard] + convert_binary[0]
    else:
        return hand_strength['HIGHCARD'] + convert_binary[single_highcard] + convert_binary[second_highcard]
    
three_cards_x = []
three_cards_y = []
four_cards_x = []
four_cards_y = []
five_cards_x = []
five_cards_y = []

# read and process file
with open('results.txt','r') as infile:
    readln = infile.readline().strip()
    curr_hole = readln
    while readln != 'EOF':
        if len(readln.split(',')) == 2:             # hole cards
                curr_hole = readln.split(',')
                comm_cards = infile.readline().strip().split(',')
                if len(comm_cards) != 1:
                    bits = best_hand(curr_hole + comm_cards)
                    if len(comm_cards) == 3:
                        three_cards_x.append(curr_hole + comm_cards + [bits[0:8],] + [bits[8:12],] + [bits[12:],] + [str(infile.readline().strip()),])
                        three_cards_y.append(float(infile.readline().strip()))
                    elif len(comm_cards) == 4:
                        four_cards_x.append(curr_hole + comm_cards + [bits[0:8],] + [bits[8:12],] + [bits[12:],] + [str(infile.readline().strip()),])
                        four_cards_y.append(float(infile.readline().strip()))
                    elif len(comm_cards) == 5:
                        five_cards_x.append(curr_hole + comm_cards + [bits[0:8],] + [bits[8:12],] + [bits[12:],] + [str(infile.readline().strip()),])
                        five_cards_y.append(float(infile.readline().strip()))
        readln = infile.readline().strip()

three_x_train, three_x_test, three_y_train, three_y_test  = train_test_split(three_cards_x, three_cards_y, test_size=0.2, random_state=1)
four_x_train, four_x_test, four_y_train, four_y_test  = train_test_split(four_cards_x, four_cards_y, test_size=0.2, random_state=1)
five_x_train, five_x_test, five_y_train, five_y_test  = train_test_split(five_cards_x, five_cards_y, test_size=0.2, random_state=1)

three_card_tokeniser = Tokenizer()
three_card_tokeniser.fit_on_texts(three_cards_x)

new_three_x_train = []
new_three_x_test = []
for i in three_x_train:
    new_three_x_train.append(three_card_tokeniser.texts_to_sequences([i])[0])
for i in three_x_test:
    new_three_x_test.append(three_card_tokeniser.texts_to_sequences([i])[0])

print(three_x_train[0:5])
print(three_y_train[0:5])

new_three_x_train = np.array(new_three_x_train)
three_y_train = np.array(three_y_train)
new_three_x_test = np.array(new_three_x_test)
three_y_test = np.array(three_y_test)

three_card_vocab_size = len(three_card_tokeniser.word_index)+1
three_card_model = train_model(len(new_three_x_train[0]), three_card_vocab_size, new_three_x_train, three_y_train, 10000, 64)
three_card_model.save('three_card_model.h5')

predictions = three_card_model.predict(new_three_x_test)
with open('predict_three_card.txt','a') as outfile:
    outfile.write('PREDICTED\t\tACTUAL\n')
    for i in range(len(predictions)):
        outfile.write(str(predictions[i]) + '\t\t' + str(three_y_test[i]) + '\n')

four_card_tokeniser = Tokenizer()
four_card_tokeniser.fit_on_texts(four_cards_x)

new_four_x_train = []
new_four_x_test = []
for i in four_x_train:
    new_four_x_train.append(four_card_tokeniser.texts_to_sequences([i])[0])
for i in four_x_test:
    new_four_x_test.append(four_card_tokeniser.texts_to_sequences([i])[0])

new_four_x_train = np.array(new_four_x_train)
four_y_train = np.array(four_y_train)
new_four_x_test = np.array(new_four_x_test)
four_y_test = np.array(four_y_test)

four_card_vocab_size = len(four_card_tokeniser.word_index)+1
four_card_model = train_model(len(new_four_x_train[0]), four_card_vocab_size, new_four_x_train, four_y_train, 500, 64)
four_card_model.save('four_card_model.h5')

predictions = four_card_model.predict(new_four_x_test)
with open('predict_four_card.txt','a') as outfile:
    outfile.write('PREDICTED\t\tACTUAL\n')
    for i in range(len(predictions)):
        outfile.write(str(predictions[i]) + '\t\t' + str(four_y_test[i]) + '\n')

five_card_tokeniser = Tokenizer()
five_card_tokeniser.fit_on_texts(five_cards_x)

new_five_x_train = []
new_five_x_test= []
for i in five_x_train:
    new_five_x_train.append(five_card_tokeniser.texts_to_sequences([i])[0])
for i in five_x_test:
    new_five_x_test.append(five_card_tokeniser.texts_to_sequences([i])[0])

new_five_x_train = np.array(new_five_x_train)
five_y_train = np.array(five_y_train)
new_five_x_test = np.array(new_five_x_test)
five_y_test = np.array(five_y_test)

five_card_vocab_size = len(five_card_tokeniser.word_index)+1
five_card_model = train_model(len(new_five_x_train[0]), five_card_vocab_size, new_five_x_train, five_y_train, 10000, 64)
five_card_model.save('five_card_model.h5')

predictions = five_card_model.predict(new_five_x_test)
with open('predict_five_card.txt','a') as outfile:
    outfile.write('PREDICTED\t\tACTUAL\n')
    for i in range(len(predictions)):
        outfile.write(str(predictions[i]) + '\t\t' + str(five_y_test[i]) + '\n')
