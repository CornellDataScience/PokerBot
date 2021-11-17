import argparse
from typing import Match
import click
import random


class KuhnPokerGame:
    def __init__(self, deck_size, stacks, first_player):
        self.deck_size = deck_size
        self.stacks = stacks
        self.community_pot = (0, 0)
        self.game_tree = ['Start',
                          'Check', 'Bet',
                          'Check', 'Bet', 'Fold', 'Call',
                          'youve come to a terrible ', 'terrible place', 'Fold', 'Call']
        self.tree_loc = 0  # children: 2*i + 1, 2*i + 2
        self.dealt_cards = self.dealCards()
        self.deck = ['J', 'Q', 'K']
        self.first_player = first_player
        self.current_player = first_player
        self.last_action = 'Start'

    def build_deck():
        deck = ['J', 'Q', 'K']
        return deck

    def isTerminal(self):
        return self.tree_loc >= 9 or self.tree_loc == 3 or (self.tree_loc >= 5 and self.tree_loc <= 6)

    def getWinner(self):
        assert(self.isTerminal())
        if(self.last_action == 'Fold'):
            return self.current_player
        else:
            return 1 if self.dealt_cards[1] > self.dealt_cards[0] else 0

    def updateWinnerStack(self):
        winner = self.getWinner()
        if(winner == 0):
            self.stacks = (
                self.stacks[winner] + self.getPotValue(), self.stacks[1])
        else:
            self.stacks = (
                self.stacks[0], self.stacks[winner] + self.getPotValue())
        return self.stacks

    def getPossibleActions(self):
        return {
            self.game_tree[2 * self.tree_loc + 1]: 2 * self.tree_loc + 1,
            self.game_tree[2 * self.tree_loc + 2]: 2 * self.tree_loc + 2
        }

    def switchPlayer(self, action):
        self.current_player = (self.current_player + 1) % 2
        self.last_action = action

    def moveTreeLocation(self, loc):
        self.tree_loc = loc

    def requireAnte(self, ante):
        self.community_pot = (
            self.community_pot[0] + ante, self.community_pot[1] + ante)
        self.stacks = (self.stacks[0] - ante, self.stacks[1] - ante)

    def getPotValue(self):
        return self.community_pot[0] + self.community_pot[1]

    def dealCards(self):
        first = random.randint(0, self.deck_size - 1)
        second = first
        while(second == first):
            second = random.randint(0, self.deck_size - 1)
        return (first, second)

    def playerBetPotUpdate(self, player):
        if(player == 0):
            self.community_pot = (
                self.community_pot[0] + 1, self.community_pot[1])
            self.stacks = (self.stacks[0] - 1, self.stacks[1])
        else:
            self.community_pot = (
                self.community_pot[0], self.community_pot[1] + 1)
            self.stacks = (self.stacks[0], self.stacks[1] - 1)


class Bot:
    def __init__(self, deck_size):
        self.strategy_distribution = {}
        self.deck_size = deck_size
        self.action_index = ['Fold', 'Call', 'Check', 'Bet']

    def sampleMove(self, node, card):
        moveProb = random.random()
        lowerBound = 0
        for i in range(0, len(self.strategy_distribution[node][card])):
            if moveProb > lowerBound and moveProb < lowerBound + float(self.strategy_distribution[node][card][i]):
                return self.action_index[i]
            lowerBound += float(self.strategy_distribution[node][card][i])


def readPokerBot(model, deck_size):
    lines = open(model).readlines()
    count = 0
    strategy = Bot(deck_size)
    for line in lines:
        count += 1
        if(count == 1):
            continue
        node_strategy = line.split("|")
        node_lastmove = node_strategy[0].strip().split("\t")
        node = int(node_lastmove[0][node_lastmove[0].index('=') + 1:])
        strategy.strategy_distribution[node] = {}
        for i in range(1, len(node_strategy)):
            hand_actdistribution = node_strategy[i].strip().split(" ")
            hand = int(hand_actdistribution[0][hand_actdistribution[0].index(
                '=') + 1])
            strategy.strategy_distribution[node][hand] = hand_actdistribution[1:]
    return strategy


@ click.command()
@ click.argument('model', type=click.Path(exists=True))
@ click.option('--cheat', type=bool, default=False)
@ click.option('--firstplayer', type=bool, default=True)
@ click.option('--initstack', type=int, default=10)
def main(model, cheat, firstplayer, initstack):
    # net = jit.load(model)
    bot = readPokerBot(model, 3)
    game = KuhnPokerGame(3, (initstack, initstack), 0 if firstplayer else 1)
    # player is 0, bot is 1
    while(True):
        click.echo(click.style(
            '---------------------------------- STARTING GAME ----------------------------------', bg='white', fg='black'))
        click.echo(">>> Requiring ante of 1...")
        game.requireAnte(1)
        click.echo(">>> Current stacks - You: " +
                   str(game.stacks[0]) + ", Bot: " + str(game.stacks[1]))

        cardDealt = game.dealt_cards

        if(cheat):
            click.echo(click.style(
                ">>> You have: " + game.deck[cardDealt[0]] + ", the bot has: " + game.deck[cardDealt[1]], fg='blue'))
        else:
            click.echo(click.style(">>> You have: " +
                       game.deck[cardDealt[0]], fg='green'))

        while(not game.isTerminal()):
            #### Prompt for next action ####
            actionList = game.getPossibleActions()
            click.echo("")
            if(game.current_player == 0):
                action = click.prompt(click.style(
                    "Do you choose to " + str(actionList.keys()), fg='green'))
            else:
                action = bot.sampleMove(game.tree_loc, cardDealt[1])
                click.echo(click.style(
                    "Bot chose to: " + str(action), fg='red'))

            #### Update pot with action ####
            if action == 'Bet':
                game.playerBetPotUpdate(game.current_player)
            elif action == 'Call':
                game.playerBetPotUpdate(game.current_player)

            #### Continue in game ####
            game.moveTreeLocation(actionList[action])
            game.switchPlayer(action)

        currentStacks = game.updateWinnerStack()
        winner = game.getWinner()

        # reinitialize game.
        winnerName = "the bot" if winner == 1 else "you"
        click.echo(click.style("------------------ GAME OVER - Winner is " + winnerName +
                   "! You: " + str(currentStacks[0]) + " Bot: " + str(currentStacks[1]) + " ------------------", bg='white', fg='black'))
        click.echo("")
        click.echo("")
        game = KuhnPokerGame(3, currentStacks, (game.first_player + 1) % 2)


if __name__ == "__main__":
    main()
