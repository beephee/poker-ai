## Poker Project - Group 26

### Set up environment
In this project, we design an intelligent agent to play Limit Texas Hold’Em Poker. We propose a novel adaptive agent designed to predict an accurate representation of its hand strength, through Monte Carlo simulations, and to extract information about the opponent’s behaviour and hand strength through opponent mapping. The agent utilises a nested evaluation function to determine its actions through Bayesian Inference, adapting its strategy based on the opponent.

### Running the Game Simulation

The "example.py" file can be used to run a simulation of the two-player game.

### Poker Agent

Our poker agent can be found in the Group26Player.py file. The agent can be called using "from Group26Player import Group26Player".

#### Detailed Report

Please do take a look at "Poker Project - Team 26.pdf" for our full technical report!

In this limited version, user only allowed to raise for four time in one round game.    
In addition, in each street (preflop,flop,turn,river), each player is only allowed to raise for four times.

Other information is similar to the PyPokerEngine,please check the detail about the parameter [link](https://github.com/ishikota/PyPokerEngine/blob/master/AI_CALLBACK_FORMAT.md)
