import numpy as np
import pandas as pd
import scipy as sp
import json
import random
from itertools import combinations


def handRank(hand):
    """
    This function takes a list of cards and returns a number representing the rank of the hand
    """
    strength = 0.0
    handType = ''

    faceTransformation = {'T': '10', 'J': '11', 'Q': '12', 'K': '13', 'A': '14'}

    fixed = []
    for card in hand:
        rank, suit = card[0], card[1]
        if rank in faceTransformation:
            rank = faceTransformation[rank]
        fixed.append(rank + suit)
    hand = fixed
        
    cardNums = [int(card[:-1]) for card in hand]
    cardSuits = [card[-1] for card in hand]

    # Check for a high card
    maxCard = max(cardNums)
    strength = maxCard/100
    handType = 'High Card'
            
        
    # Check for pair
    for card in cardNums:
        if cardNums.count(card) == 2:
            strength = 1 + card/100
            handType = 'Pair'

            #check for two pair
            if len(hand) >= 4:
                for card2 in cardNums:
                    if cardNums.count(card2) == 2 and card != card2:
                        minPair = min(card, card2)
                        maxPair = max(card, card2)
                        strength = 2 + maxPair/100 + minPair/10000
                        handType = 'Two Pair'
        # Check for four of a kind
        if cardNums.count(card) == 4:
            strength = 8 + card/100
            handType = 'Four of a Kind'
            break
            
        # Check for three of a kind
        if cardNums.count(card) == 3:
            strength = 3 + card/100
            handType = 'Three of a Kind'        


    if len(hand) >= 5:

        # Check for a flush:
        for suit in cardSuits:
            if cardSuits.count(suit) >= 5:
                if strength < 6:
                    strength = 6
                    handType = 'Flush'
                    suitIndexes = [True if cardSuits[i] == suit else False for i in range(len(cardSuits))]
                    cardNums = [cardNums[i] for i in range(len(cardNums)) if suitIndexes[i]]
                    maxCard = max(cardNums)
                    strength += maxCard/100
        
        # Check for straight if there are 5 or more cards
        handLib = {hand: [hand[:-1], hand[-1]] for hand in hand}
        for card in list(handLib.keys()):
            if handLib[card][0] in faceTransformation:
                handLib[card][0] = faceTransformation[handLib[card][0]]
            handLib[card][0] = int(handLib[card][0])
            if handLib[card][0] == 14:
                new_card = "1" + handLib[card][1]
                handLib[new_card] = [1, handLib[card][1]]
        
        straightSuits = []
        for card in list(handLib.values()):
            temp = card[0]
            straightSuits.append(card)
            for cardComp in list(handLib.values()):
                if cardComp[0] == temp + 1:
                    temp = cardComp[0]
                    straightSuits.append(cardComp)
                if len(straightSuits) >= 5:
                    straightSuits = sorted(straightSuits, key=lambda x: x[0])
                    for s in ['H', 'D', 'C', 'S']:
                        filteredStraightFlush = list(filter(lambda x : x[1] == s, straightSuits))
                        if len(filteredStraightFlush) >= 5:
                            if strength < 8:
                                strength = 8 + max([i[0] for i in filteredStraightFlush])/100
                                handType = 'Straight Flush'
                                break
                        else:
                            strength = 4 + max([i[0] for i in straightSuits])/100
                            handType = 'Straight'
                            break
            straightSuits = []


        # Check for a full house
        for card in cardNums:
            if cardNums.count(card) == 3:
                for card2 in cardNums:
                    if cardNums.count(card2) == 2:
                        if strength < 7:
                            strength = 7 + card/100 + card2/10000
                            handType = 'Full House'

    strength += maxCard/1000000
    
    return strength, handType


def better(hand1, hand2, boardcards):
    """
    This function takes two tuples of length two representing two hands and a list representing community cards 
    it returns a positive number if hand1 is better than hand2, and a negative number if hand2 is better
    """
    hand1 = list(hand1) + boardcards
    hand2 = list(hand2) + boardcards
    return handRank(hand1)[0] - handRank(hand2)[0]


def simulate(numPlayers, hand, boardCards, trials = 1000):
    with open('Deck.json', 'r') as file:
        data = json.load(file)
    deck = [card["cardID"] for card in data['Deck']]

    known = list(hand) + boardCards
    for card in known:
        deck.remove(card)
    
    if len(boardCards) <= 5:
        won = 0
        for _ in range(trials):
            trialDeck = deck.copy()
            results = []

            trialBoard = boardCards.copy()

            while len(trialBoard) < 5:
                trialBoard.append(random.choice(trialDeck))
                trialDeck.remove(trialBoard[-1])

            for i in range(numPlayers):
                cards = random.sample(trialDeck, 2)
                trialDeck.remove(cards[0])
                trialDeck.remove(cards[1])
                results.append(better(hand, cards, trialBoard) > 0)
            if all(results):
                won += 1
        
        return won/trials
    
    else:
        won = 0
        for _ in range(trials):
            trialDeck = deck.copy()
            results = []

            for i in range(numPlayers):
                cards = random.sample(trialDeck, 2)
                trialDeck.remove(cards[0])
                trialDeck.remove(cards[1])
                results.append(better(hand, cards, boardCards) < 0)
            if all(results):
                won += 1
        
        return won/trials

print(simulate(1, ['KD', '6H'], [], trials=20000))