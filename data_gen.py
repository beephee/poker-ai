from sklearn.model_selection import train_test_split
import operator
from keras.callbacks import EarlyStopping
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint
from keras.models import Sequential
from keras.layers import Dense, Bidirectional, LSTM, Conv1D, MaxPooling1D, Flatten, Embedding, GlobalAveragePooling1D, Dropout
from keras.preprocessing.text import Tokenizer
import numpy as np

# conversion dictionaries

poss_suits = ['C','D','H','S']

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

win_convert = {}
win_convert['WIN'] = [1,0]
win_convert['DRAW'] = [1,0]
win_convert['LOSE'] = [0,1]

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
hand_strength['ONEPAIR'] = '00000001'
hand_strength['TWOPAIR'] = '00000010'
hand_strength['THREECARD'] = '00000100'
hand_strength['STRAIGHT'] = '00001000'
hand_strength['FLASH'] = '00010000'
hand_strength['FULLHOUSE'] = '00100000'
hand_strength['FOURCARD'] = '01000000'
hand_strength['STRAIGHTFLASH'] = '10000000'

# write end of file to stop checking
with open('win_results.txt','a') as writefile:
    writefile.write('EOF\n')

def train_model(input_size, vocab_size, x_train, y_train, num_epochs, batch_size):
    early_stopping = EarlyStopping(monitor='val_loss', patience=5)
    optim = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=True)
    model = Sequential()
    model.add(Embedding(vocab_size, 32, input_length = input_size))
    model.add(Bidirectional(LSTM(16)))  
    #model.add(Dense(24, input_dim = input_size, activation = 'sigmoid'))
    model.add(Dense(8, activation = 'relu'))
    model.add(Dense(2, activation = 'softmax'))
    model.compile(loss = 'categorical_crossentropy', optimizer = optim, metrics = ['accuracy'])
    model.fit(x_train, y_train, epochs = num_epochs, verbose = 2, batch_size = batch_size, shuffle = True, validation_split = 0.2, callbacks = [early_stopping])
    return model

def train_cnn(input_size, vocab_size, x_train, y_train, num_epochs, batch_size):
    early_stopping = EarlyStopping(monitor='val_loss', patience=5)
    optim = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=True)
    model = Sequential()
    model.add(Conv1D(100, 10, activation='relu'))
    model.add(Conv1D(100, 10, activation='relu'))
    model.add(MaxPooling1D(3))
    model.add(Conv1D(160, 10, activation='relu'))
    model.add(Conv1D(160, 10, activation='relu'))
    model.add(GlobalAveragePooling1D())
    model.add(Dropout(0.5))
    model.add(Dense(2, activation = 'softmax'))
    model.compile(loss = 'categorical_crossentropy', optimizer = optim, metrics = ['accuracy'])
    model.fit(x_train, y_train, epochs = num_epochs, verbose = 2, batch_size = batch_size, shuffle = True, validation_split = 0.2, callbacks = [early_stopping])
    return model

five_cards_x = []
five_cards_y = []

# read and process file
with open('win_results.txt','r') as infile:
    readln = infile.readline().strip()
    while readln != 'EOF':
        line = []
        if readln == '':
            continue
        for i in readln.split(','):
            line.append(convert_binary[int(i)])
            
        comm_cards = infile.readline().strip().split(',')
        suits = [i[0] for i in comm_cards]
        nums = [value_convert[i[1]] for i in comm_cards]
        nums.sort(reverse=True)
        suits_input = [str(suits.count(i)) for i in poss_suits]
        suits_input.sort(reverse=True)
        nums_input = [convert_binary[i] for i in nums]
        line.append(''.join(suits_input))
        #line.extend(suits_input)
        line.extend(nums_input)

        best_hand = infile.readline().strip().split(',')
        best_hand_input = []
        best_hand_input.append(hand_strength[best_hand[0]])
        best_hand_input.append(convert_binary[int(best_hand[1])])
        best_hand_input.append(convert_binary[int(best_hand[2])])
        line.extend(best_hand_input)
        ##
        #line = best_hand_input
        ##

        five_cards_x.append(line)
        result = infile.readline().strip()
        five_cards_y.append(win_convert[result])

        readln = infile.readline().strip()
        if readln == 'EOF':
            break
        readln = infile.readline().strip()

five_x_train, five_x_test, five_y_train, five_y_test  = train_test_split(five_cards_x, five_cards_y, test_size=0.2, random_state=1)
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
five_card_model = train_model(len(new_five_x_train[0]), five_card_vocab_size, new_five_x_train, five_y_train, 1000, 32)
five_card_model.save('five_card_model.h5')

predictions = five_card_model.predict(new_five_x_test)
with open('predict_five_card.txt','a') as outfile:
    outfile.write('PREDICTED\t\tACTUAL\n')
    for i in range(len(predictions)):
        outfile.write(str(predictions[i]) + '\t\t' + str(five_y_test[i]) + '\n')

correct = 0
wrong = 0
for i in range(len(predictions)):
    
    pred_idx = 0
    for j in range(len(predictions[i])):
        if predictions[i][j] > predictions[i][pred_idx]:
            pred_idx = j
    actual_idx = 0
    for j in range(len(five_y_test[i])):
        if five_y_test[i][j] > five_y_test[i][actual_idx]:
            actual_idx = j
    
    if pred_idx == actual_idx:
        correct += 1
    else:
        wrong += 1
        
print('Total Correct: %s ( %2f )' % (str(correct), (correct/(correct+wrong))))
print('Total Wrong: %s ( %2f )' % (str(wrong), (wrong/(correct+wrong))))
