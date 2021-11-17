import argparse
from typing import Match
import click
import random


class KuhnPokerGame:
    def __init__(self, deck_size, stacks=(10, 10)):
        self.deck_size = deck_size
        self.stacks = stacks
        self.community_pot = (0, 0)
        self.game_tree = ['Start',
                          'Check', 'Bet',
                          'Check', 'Bet', 'Fold', 'Call',
                          '', '', 'Fold', 'Call']
        self.tree_loc = 0  # 2*i + 1, 2*i + 2

    def build_deck():
        deck = ['J', 'Q', 'K']
        return deck

    def isTerminal(self):
        return self.tree_loc >= 9 or self.tree_loc == 3 or (self.tree_loc >= 5 and self.tree_loc <= 6)

    def getPossibleActions(self):
        return {
            self.game_tree[2 * self.tree_loc + 1]: 2 * self.tree_loc + 1,
            self.game_tree[2 * self.tree_loc + 2]: 2 * self.tree_loc + 2
        }

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
        # MOVE # (0 or 2) : {J: [prob distribution], Q: [prob distribution]}
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
def main(model, cheat):
    # net = jit.load(model)
    strategy = readPokerBot(model, 3)
    game = KuhnPokerGame(3, stacks=(1, 1))
    startingPlayer = 0  # player is 0, bot is 1
    while(True):
        click.echo(click.style(
            '---------------------------------- STARTING GAME ----------------------------------', bg='white', fg='black'))

        click.echo(">>> Requiring ante of 1")
        game.requireAnte(1)
        click.echo(">>> Current stacks: " + str(game.stacks))

        cardDealt = game.dealCards()

        if(cheat):
            click.echo(click.style(
                ">>> You have: " + str(cardDealt[0]) + ", the bot has: " + str(cardDealt[1]), fg='green'))
        else:
            click.echo(click.style(">>> You have: " +
                       str(cardDealt[0]), fg='blue'))

        currentPlayer = startingPlayer

        lastAction = ''
        while(not game.isTerminal()):
            actionList = game.getPossibleActions()

            action = 0
            if(currentPlayer == 0):
                action = click.prompt(click.style(
                    "Do you choose to: " + str(actionList.keys()), fg='green'))
            else:
                action = strategy.sampleMove(game.tree_loc, cardDealt[1])
                click.echo(click.style(
                    "Bot chose to: " + str(action), fg='red'))

            if action == 'Bet':
                game.playerBetPotUpdate(currentPlayer)
            elif action == 'Call':
                game.playerBetPotUpdate(currentPlayer)

            game.tree_loc = actionList[action]
            lastAction = action
            currentPlayer = (currentPlayer + 1) % 2

        # check winner
        winner = currentPlayer

        if(lastAction == 'Fold'):
            winner = currentPlayer
        else:
            winner = 1 if cardDealt[1] > cardDealt[0] else 0

        currentStacks = game.stacks
        if(winner == 0):
            currentStacks = (
                currentStacks[winner] + game.getPotValue(), currentStacks[1])
        else:
            currentStacks = (
                currentStacks[0], currentStacks[winner] + game.getPotValue())

        # update stack
        # reinitialize game.
        winnerName = "the bot" if winner == 1 else "you"
        click.echo(click.style("----------------- GAME OVER - Winner is " + winnerName +
                   "! Final amount: " + str(currentStacks) + " -----------------", bg='white', fg='black'))
        click.echo("")
        click.echo("")
        game = KuhnPokerGame(3, stacks=currentStacks)
        startingPlayer = (startingPlayer + 1) % 2


if __name__ == "__main__":
    main()
