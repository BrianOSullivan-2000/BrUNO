# In[]

import random
import numpy as np

# In[]

def check_if_playable(activeCard, card):

    #Can play any card
    if card.colour == "Wild":
        return True

    #Match colour or symbol
    elif card.value == activeCard.value or card.colour == activeCard.colour:
        return True
    else:
        return False

def UNO(player):

    if player.cpu == False:
        print("UNO! (You)")
    else:
        print("UNO! ({})".format(player.name))

class Game():

    def __init__(self, names, auto=True):

        #Init variables
        self.names = names
        self.playerCount = len(self.names)
        self.firstPlayer = random.randrange(0, len(names), 1)
        ## 1 is clockwise, -1 is anti-clockwise
        self.increment = 1
        self.drawStack = 0
        self.auto = auto

        #Ready deck
        self.deck = Deck(True, "unodeck.txt")
        self.deck.shuffle()

        #Ready discard, get starting card
        self.discard = Deck()
        self.discard.cards.insert(0, self.deck.cards.pop(0))

        #Init players
        self.players = []
        for name in self.names:
            newPlayer = Player(name, self.names.index(name))
            newPlayer.draw(self.deck, n=7)
            self.players.append(newPlayer)

        #Add non-cpu player
        if auto == False:
            self.players[0].cpu = False

        print("First Card is {} {}.".format(self.discard.cards[0].colour, self.discard.cards[0].value))
        self.playCard = self.discard.cards[0]

        #Take first turn
        if self.players[self.firstPlayer].cpu == False:
            print("You start")
        else:
            print("{} will start.".format(self.names[self.firstPlayer]))

        self.Turn(self.firstPlayer)

    def Turn(self, seat):

        #Current card and player
        activeCard = self.discard.cards[0]
        currentPlayer = self.players[seat]

        #Reshuffle discard back into deck if out of cards
        if len(self.deck.cards) == 0:

            self.deck.cards.append(self.discard.cards[1:])
            self.discard.cards = self.discard.cards[0]
            self.deck.shuffle()
            print("Deck re-shuffled")

        #DrawTwo is played
        if activeCard.value == "DrawTwo" and activeCard.action == True:

            #Start draw chain
            if self.drawStack == 0:
                self.drawStack = 2

            #Check for response
            DrawTwos = []
            for card in currentPlayer.hand:
                if card.value == "DrawTwo":
                    DrawTwos.append(card)

            #Stack draw chain
            if len(DrawTwos) != 0:
                currentPlayer.play(self.discard, random.choice(DrawTwos))
                self.drawStack += 2

            #Take draw penalty
            else:

                if currentPlayer.cpu == False:
                    print("You draw {} cards".format(self.drawStack))
                else:
                    print("{} draws {} cards".format(currentPlayer.name, self.drawStack))
                currentPlayer.draw(self.deck, self.drawStack)

                #Action has been resolved
                self.drawStack = 0
                activeCard.action = False

            #Next player
            nextSeat = (seat + self.increment) % self.playerCount

            #Was that the last card?
            if len(currentPlayer.hand) == 0:
                if currentPlayer.cpu == False:
                    print("You win!")
                else:
                    print("{} wins!".format(currentPlayer.name))

            #Next turn
            else:
                if len(currentPlayer.hand) == 1:
                    UNO(currentPlayer)
                self.Turn(nextSeat)

        #DrawFour played
        elif activeCard.value == "DrawFour" and activeCard.action == True:

            #Take penalty
            if currentPlayer.cpu == False:
                print("You draw 4 cards")
            else:
                print("{} draws 4 cards".format(currentPlayer.name))

            #Resolve card and go to next seat
            currentPlayer.draw(self.deck, 4)
            activeCard.action = False
            nextSeat = (seat + self.increment) % self.playerCount
            self.Turn(nextSeat)

        else:

            #List possible plays
            options = []
            for card in currentPlayer.hand:
                if check_if_playable(activeCard, card):
                    options.append(card)

            #Play random legal card
            if len(options) != 0:
                self.playCard = random.choice(options)
                currentPlayer.play(self.discard, self.playCard)

            #No available options
            else:
                if currentPlayer.cpu == False:
                    print("You draw a card")
                else:
                    print("{} draws a card".format(currentPlayer.name))
                currentPlayer.draw(self.deck)
                newCard = currentPlayer.hand[-1]
                self.playCard.action = False

                #Drawn card is playable
                if check_if_playable(activeCard, newCard):
                    currentPlayer.play(self.discard, newCard)
                    self.playCard = newCard

            #Adjust order for skip/reverse
            if self.playCard.action == True:
                if self.playCard.value == "Reverse":
                    self.increment *= -1
                if self.playCard.value == "Skip":
                    self.increment *= 2

            #Next seat and resolve skip
            nextSeat = (seat + self.increment) % self.playerCount
            self.increment = 1 * np.sign(self.increment)

            if len(currentPlayer.hand) == 0:
                if currentPlayer.cpu == False:
                    print("You Win!")
                else:
                    print("{} wins!".format(currentPlayer.name))

            else:
                if len(currentPlayer.hand) == 1:
                    UNO(currentPlayer)
                self.Turn(nextSeat)


class Deck():

    def __init__(self, first=False, filename=None):

        #List of Card class
        self.cards = []
        self.first = first
        self.filename = filename

        if self.first:
            self.build()

    def build(self):

        #Read UNO cards from .txt file
        f = open(self.filename, 'r')

        for card in f.readlines():
            colour = card.split()[0]
            value = card.split()[1]
            action = card.split()[2]

            self.cards.append(Card(colour, value, action))

    def show(self):

        for card in self.cards:
            card.show()

    def shuffle(self):

        #Some shuffle algorithm (can't remember name)
        for i in range(len(self.cards) - 1, 0, -1):
            r = random.randint(0, i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def drawCard(self):

        return self.cards.pop(0)


class Card():

    def __init__(self, colour, val, action):

        #Card has colour, symbol, and action status
        self.colour = colour
        self.value = val
        self.action = action
        if self.action == "False":
            self.action = False
        else:
            self.action = True

    def show(self):

        if self.value == "ChangeColour":
            print("Wild")
        else:
            print("{} {}".format(self.colour, self.value))

class Player():

    def __init__(self, name, seat, cpu=True):

        self.name = name
        self.seat = seat
        self.hand = []
        self.cpu = cpu

    def draw(self, deck, n=1):

        #Number of cards from specified deck
        for i in range(n):
            self.hand.append(deck.drawCard())

    def showHand(self):

        #List of cards
        if self.cpu == False:
            print("Your hand:")
        else:
            print("{}'s Hand:".format(self.name))
        report = ""
        for card in self.hand:
            whatCard = "{} {}, ".format(card.colour, card.value)
            report += whatCard
        print(report)

    def play(self, deck, card):

        #Play card from hand to specified deck
        if self.cpu == False:
            print("You play {} {}".format(card.colour, card.value))
        else:
            print("{} plays {} {}".format(self.name, card.colour, card.value))

        #If wild change the colour of card
        if card.colour == "Wild":
            newColour = random.choice(["Red", "Blue", "Green", "Yellow"])
            if self.cpu == False:
                print("You select {}".format(newColour))
            else:
                print("{} selects {}".format(self.name, newColour))
            card.colour = newColour

        #Move card from hand to discard
        self.hand.remove(card)
        deck.cards.insert(0, card)

# In[]

#Sample test with friends
names = ["Brian", "Scott", "Vlad", "Oisin"]
Game(names, auto=False)
