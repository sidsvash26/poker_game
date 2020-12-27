'''
Poker Module

Author: Siddharth Vashishtha
Date Created: December 23, 2020

Usage:
python poker_module.py \
       -b 1000 \
       -p "pranjal manu pranshu" \
       -s "manu"

table = PokerGame(players = ['manu', 'pranjal', 'pranshu', 'manthan'], email_ids=['svashishtha.iitkgp@gmail.com', 
                                                                            'pranjal.alwar@gmail.com', 
                                                                            'pranshu04.alwar@gmail.com',
                                                                            'manthan2727@gmail.com'])       
'''

from typing import * 
import random
from termcolor import colored
import time
from collections import defaultdict
from operator import itemgetter
from itertools import combinations
import numpy as np
import argparse
import os
from decouple import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

## TWILIO Credentials
from twilio.rest import Client
TWILIO_NUMBER = '+16592075400'
# Environment variables TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
# Saved in current dir's .env file
API_USERNAME = config('TWILIO_ACCOUNT_SID')
API_KEY = config('TWILIO_AUTH_TOKEN')
client = Client(API_USERNAME, API_KEY)

## FAST2SMS Credentials
import requests 
import json
from decouple import config

FAST2SMS_API_KEY = config('FAST2SMS_API_KEY')

GMAIL_PASS = config('GMAIL_PASS')


def send_message_fast2sms(phone_number, api_key=FAST2SMS_API_KEY,
                          message=''):
    '''
    Send messsage to an Indian phone number
    using fast2sms
    '''
        # mention url 
    url = "https://www.fast2sms.com/dev/bulk"


    # create a dictionary 
    my_data = { 
        # Your default Sender ID 
        'sender_id': 'FSTSMS', 

        # Put your message here! 
        'message': message, 

        'language': 'unicode', 
        'route': 'p', 

        # You can send sms to multiple numbers 
        # separated by comma. 
        'numbers': phone_number
    } 

    # create a dictionary 
    headers = { 
        'authorization': api_key, 
        'Content-Type': "application/x-www-form-urlencoded", 
        'Cache-Control': "no-cache"
    }
    
        # make a post request 
    response = requests.request("POST", 
                                url, 
                                data = my_data, 
                                headers = headers) 
    # load json data from source 
    returned_msg = json.loads(response.text) 
    # print the send message 
    # print(returned_msg['message'])

def send_email(gmail_pass,
               email_address_to='',
              subject="Poker Game",
              message=''):
    '''
    Send a message in email
    '''
    
    # create message object instance
    msg = MIMEMultipart()

    # setup the parameters of the message
    password = gmail_pass
    msg['From'] = "sidsvash26@gmail.com"
    msg['To'] = email_address_to
    msg['Subject'] = subject

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    #create server
    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()
    #print("successfully sent email to %s:" % (msg['To']))

class Card(object):
    '''
    A Playing Card Object
    '''
    def __init__(self, val, suit):
        self.val = val
        self.suit = suit
        self.face_score = {'A': 14,
                          'K': 13,
                          'Q': 12,
                          'J': 11}
        
    def __repr__(self):
        return f"{self.val}{self.suit}"
    
    def __str__(self):
        return f"{self.val}{self.suit}"
    
    def __gt__(self, other_card):
        val1 = self.val
        val2 = other_card.val
        if isinstance(val1,int) and isinstance(val2,int):
            return val1 > val2
        elif isinstance(val1,str) and isinstance(val2,str):
            return self.face_score[val1] > self.face_score[val2]
        elif isinstance(val1,str) and isinstance(val2,int):
            return True
        else:
            return False
        
    def __ge__(self, other_card):
        val1 = self.val
        val2 = other_card.val
        if isinstance(val1,int) and isinstance(val2,int):
            return val1 >= val2
        elif isinstance(val1,str) and isinstance(val2,str):
            return self.face_score[val1] >= self.face_score[val2]
        elif isinstance(val1,str) and isinstance(val2,int):
            return True
        else:
            return False
        
    def __lt__(self, other_card):
        val1 = self.val
        val2 = other_card.val
        if isinstance(val1,int) and isinstance(val2,int):
            return val1 < val2
        elif isinstance(val1,str) and isinstance(val2,str):
            return self.face_score[val1] < self.face_score[val2]
        elif isinstance(val1,str) and isinstance(val2,int):
            return False
        else:
            return True
        
    def __le__(self, other_card):
        val1 = self.val
        val2 = other_card.val
        if isinstance(val1,int) and isinstance(val2,int):
            return val1 <= val2
        elif isinstance(val1,str) and isinstance(val2,str):
            return self.face_score[val1] <= self.face_score[val2]
        elif isinstance(val1,str) and isinstance(val2,int):
            return False
        else:
            return True
        
    def __eq__(self, other_card):
        val1 = self.val
        val2 = other_card.val
        if isinstance(val1,int) and isinstance(val2,int):
            return val1 == val2
        elif isinstance(val1,str) and isinstance(val2,str):
            return self.face_score[val1] == self.face_score[val2]
        elif isinstance(val1,str) and isinstance(val2,int):
            return False
        else:
            return False
        
    def __sub__(self, other_card):
        val1 = self.val
        val2 = other_card.val
        if isinstance(val1,int) and isinstance(val2,int):
            return val1 - val2
        elif isinstance(val1,str) and isinstance(val2,str):
            return self.face_score[val1] - self.face_score[val2]
        elif isinstance(val1,str) and isinstance(val2,int):
            return self.face_score[val1] - val2
        else:
            return val1 - self.face_score[val2]
        
    def __hash__(self):
        return hash(tuple([self.val, self.suit]))
    
class PokerHand(object):
    '''
    A poker hand of 5 cards objects
    '''
    def __init__(self, cards: List[Card]):
        assert len(cards) == 5 # Poker Hand has 5 cards
        #Sort the cards based on value
        self.cards = sorted(cards, reverse=True) 
        self.label = classify_hand(self.cards)
        #Sort the cards based on hand
        self._hand_order() 
        self.hand_scores = {'High Card': 1,
                          "One Pair": 2,
                          "Two Pair":3,
                          "Three of a Kind": 4,
                          "Straight":5,
                          "Flush":6,
                          "Full House":7,
                          "Four of a Kind":8,
                          "Straight Flush":9,
                          'Royal Flush':10}
        
    def _hand_order(self):
        '''
        Sort the cards in order of hand power
        so that it's easy to compare with other cards
        '''
        label = self.label
        card_to_count = defaultdict(int)
        count_to_card = defaultdict(list)
        
        for card in self.cards:
            card_to_count[card.val] += 1
            
        for card_val, count in card_to_count.items():
            count_to_card[count].append(card_val)
            
        if label=="One Pair" or label=="Two Pair":
            cards = [] 
            pair_vals = count_to_card[2]
            ## Get the pairs:
            for card in self.cards:
                if card.val in pair_vals:
                    cards.append(card)
            ## Append remaining
            for card in self.cards:
                if card.val not in pair_vals:
                    cards.append(card)
            self.cards = cards
        
        elif label=="Three of a Kind" or label=="Full House":
            cards = [] 
            pair_vals = count_to_card[3]
            ## Get the triplet:
            for card in self.cards:
                if card.val in pair_vals:
                    cards.append(card)
            ## Append remaining
            for card in self.cards:
                if card.val not in pair_vals:
                    cards.append(card)
            self.cards = cards
            
        elif label=="Four of a Kind":
            cards = [] 
            pair_vals = count_to_card[4]
            ## Get the quadruplet:
            for card in self.cards:
                if card.val in pair_vals:
                    cards.append(card)
            ## Append remaining
            for card in self.cards:
                if card.val not in pair_vals:
                    cards.append(card)
            self.cards = cards
            
    def __repr__(self):
        string = ""
        for card in self.cards:
            string += f"{card.val}{card.suit}  "
        return string
    
    def __gt__(self, other):
        label1 = classify_hand(self.cards)
        label2 = classify_hand(other.cards)
        
        score1 = self.hand_scores[label1]
        score2 = self.hand_scores[label2]
        
        if score1 != score2:
            return score1 > score2
        else:
            for card1, card2 in zip(self.cards, 
                                    other.cards):
                if card1==card2:
                    continue
                else:
                    return card1 > card2
            return False
        
    def __ge__(self, other):
        label1 = classify_hand(self.cards)
        label2 = classify_hand(other.cards)
        
        score1 = self.hand_scores[label1]
        score2 = self.hand_scores[label2]
        
        if score1 != score2:
            return score1 > score2
        else:
            for card1, card2 in zip(self.cards, 
                                    other.cards):
                if card1==card2:
                    continue
                else:
                    return card1 > card2
            return True
        
    def __lt__(self, other):
        label1 = classify_hand(self.cards)
        label2 = classify_hand(other.cards)
        
        score1 = self.hand_scores[label1]
        score2 = self.hand_scores[label2]
        
        if score1 != score2:
            return score1 < score2
        else:
            for card1, card2 in zip(self.cards, 
                                    other.cards):
                if card1==card2:
                    continue
                else:
                    return card1 < card2
            return False
        
    def __le__(self, other):
        label1 = classify_hand(self.cards)
        label2 = classify_hand(other.cards)
        
        score1 = self.hand_scores[label1]
        score2 = self.hand_scores[label2]
        
        if score1 != score2:
            return score1 < score2
        else:
            for card1, card2 in zip(self.cards, 
                                    other.cards):
                if card1==card2:
                    continue
                else:
                    return card1 < card2
            return True
        
    def __eq__(self, other):
        label1 = classify_hand(self.cards)
        label2 = classify_hand(other.cards)
        
        score1 = self.hand_scores[label1]
        score2 = self.hand_scores[label2]
        
        if score1 != score2:
            return False
        else:
            for card1, card2 in zip(self.cards, 
                                    other.cards):
                if card1!=card2:
                    return False
            return True
    
class Player(object):
    '''
    A poker player's object
    '''
    def __init__(self, name="Ram", 
                      buy_in=1000,
                      phone_number='',
                      email_id = ''):
        self.name = name
        self.buy_in=1000
        self.chips = buy_in
        self.holes = None
        self.fold = False
        self.small = False
        self.big = False
        self.next = None #Next player in the order
        self.current_bet = 0
        self.total_bet = 0
        self.phone_number = phone_number
        self.email_id = email_id
        self.all_in = False
        self.separate_pot = False

        if len(self.name.strip())==0:
            raise ValueError("Name cannot be empty!")
            
    def chips(self):
        '''
        Current amount of chips
        '''
        return self.chips
    
    def raise_(self, amount):
        '''
        Implement Raise
        raise to total amount
        '''
        if self.chips - self.current_bet > amount:
            print(f"{self.name} raises to total ${amount}")
            self.chips -= (amount-self.current_bet)
            self.total_bet += (amount-self.current_bet)
            self.current_bet += (amount-self.current_bet)
            
        elif self.chips - self.current_bet == amount:
            print(f"{self.name} puts ${self.chips} and goes ALL IN!!!")
            self.all_in = True
            self.chips -= self.chips
            self.total_bet += self.chips
            self.current_bet += self.chips
            
        else:
            print(f"{self.name} doesn't have ${amount} to raise")

        print(f"{self.name} current bet: {self.current_bet}")
        print(f"{self.name} total bet: {self.total_bet}")

            
    def bet_(self, amount):
        '''
        Implement Bet
        bet by amount. Bet is only done when current total bet is zero
        '''
        if self.chips > amount:
            print(f"{self.name} bets ${amount}")
            self.chips -= amount
            self.current_bet += amount
            self.total_bet += amount
        elif self.chips == amount:
            print(f"{self.name} puts ${self.chips} and goes ALL IN!!!")
            self.all_in = True
            self.chips -= amount
            self.current_bet += amount
            self.total_bet += amount
        else:
            print(f"{self.name} doesn't have ${amount} to bet")


        print(f"{self.name} current bet: {self.current_bet}")
        print(f"{self.name} total bet: {self.total_bet}")

            
    def call_(self, amount):
        '''
        Implement Call

        amount is -> Current max bet on the table
        '''
        if self.chips - self.current_bet > amount:
            print(f"{self.name} calls, and matches ${amount}")
            self.chips -= (amount - self.current_bet)
            self.total_bet += (amount-self.current_bet)
            self.current_bet += (amount-self.current_bet)
        else:
            print(f"{self.name} puts ${self.chips} and goes ALL IN!!!")
            self.all_in = True
            self.chips -= self.chips
            self.total_bet += self.chips
            self.current_bet += self.chips

        print(f"{self.name} current bet: {self.current_bet}")
        print(f"{self.name} total bet: {self.total_bet}")
            
    def check_(self):
        '''
        Implement Check
        '''
        print(f"{self.name} checks!")
        
    def fold_(self):
        '''
        Implement Fold
        '''
        print(f"{self.name} folds!")
        self.fold = True
        
    def show(self):
        '''
        Show cards
        '''
        print(f"{self.name}'s cards: {self.holes}")
        
    def __repr__(self):
        return f"{self.name} (${self.chips})"
    
class PokerGame(object):
    '''
    A Poker Game's object (i.e. the Poker Table)
    '''
    def __init__(self, chips=1000,
                players = ['a', 'b'],
                phone_numbers=[],
                email_ids = [],
                phone_client=''):
        '''
        phone_client: "fast2sms" or "twilio"

        '''
        self.num_players = len(players)
        self.nums = ['A',2,3,4,5,6,7,8,9,10,'J','Q', 'K']
        self.suits = {'clubs':"\u2663\uFE0F",
                     'hearts':"\u2764\uFE0F",
                     'spades':"\u2660\uFE0F",
                     'diamonds':"\u2666\uFE0F"}

        self.chips = chips
        self.deck = [Card(n,s) for s in self.suits.values() for n in self.nums]
        self.small_blind_amount = chips/100
        self.big_blind_amount = chips/50
        self.current_pot = 0
        self.public_cards = []
        self.phone_client = phone_client
        self.pots = []
        
        ## Initialize Player objecys
        self._initialize_players(players, phone_numbers, email_ids)
        
    def _check_player_name_errors(self, players: List[str]):
        '''
        Produce error if the player names
        are either duplicates or have an 
        empty name
        '''
        if len(set(players)) != len(players):
            raise ValueError(f"Your players have duplicate names, try again!!!")
            
        elif '' in players:
            raise ValueError(f"Player name cannot be empty, try again!")
            
        else:
            return None
        
    def _initialize_players(self, players: List[str], 
                                    phone_numbers: List[str],
                                    email_ids: List[str]):
        '''
        Create player objects and 
        Give chips to everyone
        '''
        self._check_player_name_errors(players)
        
        self.players = {}
        
        ## create empty phone numbers if not provided
        if not phone_numbers:
            phone_numbers = ['']*len(players)

        if not email_ids:
            email_ids = ['']*len(players)

        for player_name, phone_number, email_id in zip(players, phone_numbers, email_ids):
            player = Player(name=player_name, 
                            buy_in=self.chips,
                            phone_number=phone_number,
                            email_id = email_id)

            self.players[player_name] = player
        print(f"Welcome to our Poker Table!")
        self.seating_position()
        
    def reset(self):
        '''
        Reset game from the beginning with current players
        '''
        for player in self.players.values():
            self.players[player.name] = Player(name=player.name, 
                                                buy_in=self.chips)
        self.seating_position()
        
    def _reset_current_bets(self):
        '''
        Reset current bets for players who are currently in the game (haven't folded)
        '''
        for player in self.current_players:
            player.current_bet = 0

    def _init_pot_round(self):
        '''
        Initialize variables when a pot ends on table
        for a new round
        '''
        ## reset all player's bets, and fold status
        for player in self.players.values():
            player.current_bet = 0
            player.total_bet = 0
            player.fold = False
            
        ## Shift blinds
        self.small_blind_player = self.big_blind_player
        self.big_blind_player = self.small_blind_player.next
        
        ## Reset pot amount
        self.current_pot = 0
        self.curr_max_bet = 0

        ## Reset public cards
        self.public_cards = []
        
    def seating_position(self, verbose=True):
        '''
        Create a single linked list of seating positions
        and print the positions
        '''
        # Create pointers to next players
        position_string = ""
        player_objects = list(self.players.values())
        for idx in range(len(player_objects)-1):
            player_objects[idx].next = player_objects[idx+1]
            position_string+=player_objects[idx].name + " ---> "
        
        #Complete the pointer cycle
        player_objects[-1].next = player_objects[0]
        position_string+=player_objects[-1].name + " ---> " + player_objects[0].name
        
        if verbose:
            print(f"\n**** Seat positions of the game ****")
            print(position_string)
        
        ## Initialize small and big blinds
        self.small_blind_player = player_objects[0]
        self.big_blind_player = self.small_blind_player.next
        
        return position_string
            
    def leave_table(self, player: str):
        '''
        Input Player leaves the table, seating pointers updated
        '''
        print(f"{player} has left the table!")
        self.players.pop(player)
        self.num_players-=1
        
        self.seating_position()
        
    def join_table(self, player: str, phone_number=''):
        '''
        Input Player leaves the table, seating pointers updated
        '''
        if player in self.players:
            raise ValueError(f"{player} is already on the table. Choose a different name")
            
        player = Player(name=player, 
                        buy_in=self.chips,
                        phone_number=phone_number)
        
        # Pointer to the last current player
        player.next = self.players[list(self.players.keys())[-1]]
        
        self.players[player.name] =  player
        self.num_players+=1
        print(f"{player} has joined the table!")     
        self.seating_position()
        
    def distribute_cards(self):
        '''
        Distribute cards to all current players
        '''
        ## Select a random sample of cards for each player (2 cards for each player)
        self.all_private_cards = random.sample(self.deck,self.num_players*2)
        idx=0
        
        ## Initialize fold = False
        for player in self.players.values():
            player.fold= False
        
        ## Distribute cards to all players
        for player in self.players:
            self.players[player].holes = [self.all_private_cards[idx], 
                                          self.all_private_cards[idx+1]]
            idx+=2
            
        print("Cards distributed!")


    def play(self, show=[]):
        '''
        Start the game

        Input:
        show: a list of player names whose cards are to be shown
        '''
        next_round = "y"
        while next_round.lower()=="y":
            self._start_round(show)

            print(f"Next round? (y/n)")
            next_round = input()
            while True:
                if next_round.lower() in ["y", "n"]:
                    break
                else:
                    print(f"Please enter valid response (y/n)")
                    next_round = input()

        print(f"Thanks for playing!!")

        return None

    def _show_cards(self, show: List[str]):
        '''

        show private cards of the players in the input list
        '''
        for player_name in show:
            player = self.players[player_name]
            print(f"{player_name}'s private cards : {player.holes[0]}  {player.holes[1]}")

    def _send_message_on_phone(self):
        '''
        send private cards on message to players
        '''
        for player in self.players.values():
            message = f"Your private cards: {player.holes[0]}  {player.holes[1]}"

            if player.phone_number:
                if self.phone_client=="twilio":
                    # print("twilio debug")
                    client.messages.create(body=message,
                              from_ = TWILIO_NUMBER,
                              to='+91'+player.phone_number)

                elif self.phone_client=="fast2sms":
    
                    send_message_fast2sms(player.phone_number,
                                          message=message)
            elif player.email_id:
                send_email(GMAIL_PASS,
                           email_address_to=player.email_id,
                              message=message)

    def _start_round(self, show: List[str]):
        '''
        Input:
        show: a list of player names whose cards are to be shown
        
        
        Start a new round:
        1. distribute cards
        2. Start bettings
        3. Find winner
        4. Ask for next round
        5. Shift blinds
        '''
        print(f"Small blind: {self.small_blind_player}")
        print(f"Big blind: {self.big_blind_player}\n")
        time.sleep(1)
        
        ## Distribute_cards
        self.distribute_cards()
    
        self._show_cards(show)

        self._send_message_on_phone()
        #******************************
        # PREFLOP STARTS
        #******************************
        self._betting_round(round_name="preflop")
        
        if len(self.current_players)==1:
            self._end_round(all_fold=True)
            return None
        else:
            print(f"Pre-flop ends, current total pot: {self.current_pot}")
            self.remaining_deck = list(set(self.deck) - 
                                       set(self.all_private_cards))
        
            #******************************
            # FLOP STARTS
            #******************************
            self.flop = random.sample(self.remaining_deck,3)
            self.public_cards = self.flop
            time.sleep(1)
            print(f"\n********************")
            print(f"Flop opens")
            print(f"{self.flop[0]}  {self.flop[1]}  {self.flop[2]}")
            print(f"**********************")
            
            self._show_cards(show)

            self._betting_round(round_name="flop")
            
            if len(self.current_players)==1:
                self._end_round(all_fold=True)
                return None
            else:
                print(f"Flop round ends, current total pot: {self.current_pot}")
                self.remaining_deck = list(set(self.deck) - 
                                           set(self.all_private_cards) - 
                                           set(self.flop))
                
                #******************************
                # TURN STARTS
                #******************************
                self.turn = random.sample(self.remaining_deck,1)
                self.public_cards += self.turn
                time.sleep(1)
                print(f"\n********************")
                print(f"Turn opens") 
                print(f"{self.flop[0]}  {self.flop[1]}  {self.flop[2]}  {self.turn[0]}")
                print(f"**********************")
                self._show_cards(show)

                self._betting_round(round_name="turn")
                
                if len(self.current_players)==1:
                    self._end_round(all_fold=True)
                    return None
                else:
                    print(f"Turn round ends, current total pot: {self.current_pot}")
                    self.remaining_deck = list(set(self.deck) - 
                                               set(self.all_private_cards) - 
                                               set(self.flop) - 
                                               set(self.turn))
                    
                    #******************************
                    # RIVER STARTS
                    #******************************
                    self.river = random.sample(self.remaining_deck,1)
                    self.public_cards += self.river
                    time.sleep(1)
                    print(f"\n********************")
                    print(f"River opens")
                    print(f"{self.flop[0]}  {self.flop[1]}  {self.flop[2]}  {self.turn[0]}  {self.river[0]}")
                    print(f"**********************")
                    self._show_cards(show)
                    self._betting_round(round_name="river")
                          
                    if len(self.current_players)==1:
                        self._end_round(all_fold=True)
                        return None
                    else:
                        self._end_round(all_fold=False)
                        return None
            
    def _end_round(self, all_fold=True):
        '''
        Declare the winner and reset the table
        for next round
        
        all_fold = True when everyone except one player has folded
        '''
        if all_fold:
            print(f"\n{self.current_players[0].name} wins the pot and takes ${self.current_pot}\n")
            self.current_players[0].chips += self.current_pot
        else:
            ## Implement winner
            self._find_winner()
        
        self._init_pot_round()
            
    def _betting_round(self, round_name="preflop"):
        
        '''
        Implement betting rounds
        '''
        count_players = 0
        total_players = len(self.players)
        
        if round_name == "preflop":
            print(f"\n********************")
            print(f"Pre-flop betting starts")
            print(f"********************")
            time.sleep(1)
            self._update_current_players()

            ## Small Blind puts on table
            self.small_blind_player.bet_(self.small_blind_amount)
            self.current_pot += self.small_blind_amount
            
            ## Big Blind puts on table
            self.big_blind_player.bet_(self.big_blind_amount)
            self.current_pot += self.big_blind_amount
            
            ## Current Bet is big blind, and turn starts after big blind
            curr_max_bet = self.big_blind_amount
            current_player = self.big_blind_player.next
            
        elif round_name in ["flop", "turn", "river"]:
            #print(f"\n********************")
            #print(f"{round_name} betting starts")
            #print(f"********************")
            time.sleep(1)
            #self._display_table(self.small_blind_player)
            curr_max_bet = -1 # hack to start the loop
            current_player = self.small_blind_player #start with small blind player
            
        ## Main round betting loop    
        while current_player.current_bet != curr_max_bet:
            ## Skip player's turn if they have folded or are ALL-IN
            if not current_player.fold:
                self._display_table(current_player)
                
                if curr_max_bet==-1:
                    print(f"\nCurrent calling bet: {colored(0, 'magenta')}, Total pot: {colored(self.current_pot, 'magenta')}\n")
                else:
                    print(f"\nCurrent calling bet: {colored(curr_max_bet, 'magenta')}, Total pot: {colored(self.current_pot, 'magenta')}\n")
                    
                print(f"{current_player.name}'s TURN")
                #print(f"{current_player.name}'s existing bet: {current_player.current_bet}")
                print(f"Choose your action:")
                
                ## Choose current player's actions
                if curr_max_bet==-1:
                    print(f"Check: (ch), Bet: (b), Fold: (f)")
                    player_response = input()
                    while player_response.lower() not in ['ch', 'b', 'f']:
                        print("Invalid response, try again!")
                        player_response = input()     
                else:
                    print(f"Call (c), Raise: (r), Fold: (f)")
                    player_response = input()
                    while player_response.lower() not in ['c', 'r', 'f']:
                        print("Invalid response, try again!")
                        player_response = input()
                
                ## Respond to Current Player's Actions
                if player_response=="ch":
                    '''
                    Check
                    '''
                    current_player.check_()
                    
                elif player_response=="f":
                    '''
                    Fold
                    '''
                    current_player.fold_()
                    
                elif player_response=="c":
                    '''
                    Call
                    '''
                    amount = curr_max_bet
                    previous_bet = current_player.current_bet
                    current_player.call_(amount)
                    self.current_pot += (amount - previous_bet)
                
                elif player_response=="b" or player_response=="r":
                    '''
                    Bet or raise
                    '''
                    print(f"Enter bet/raise amount: ")
                    
                    if curr_max_bet == -1:
                        curr_max_bet = 0
                        
                    while True:
                        try:
                            bet_amount = float(input())
                            while (bet_amount <= curr_max_bet) or (bet_amount > current_player.chips):
                                if bet_amount <= curr_max_bet:
                                    print(f"Please enter a number > {curr_max_bet}")
                                else:
                                    print(f"Your bal ${current_player.chips} is less than input amount. Try again!")
                                bet_amount = float(input())
                        except:
                            print(f"Invalid input, please enter a real number")  
                            continue
                        else:            
                            amount = bet_amount 
                            if player_response=="b":
                                previous_bet = current_player.current_bet
                                current_player.bet_(amount)
                                self.current_pot += (amount - previous_bet)
                            else:
                                previous_bet = current_player.current_bet
                                current_player.raise_(amount)
                                self.current_pot += (amount - previous_bet)
                                
                            break
                            
                    curr_max_bet = bet_amount
                    
                                
            ## Go to next player
            current_player = current_player.next
            count_players+=1
            
            ## If everyone checks, stop the loop
            if count_players == total_players and curr_max_bet==-1:
                break
        
        ## Update stuff at the end of round
        self._update_current_players()
        self._display_table(self.small_blind_player)
        self._reset_current_bets()

    def _update_pots(self):
        '''
        Create new pots if someone is all-in
        '''
        # Find players for which new_pots are to be created
        new_all_in_players = [player for player in self.current_players 
                                    if (player.all_in and not player.separate_pot)]
        
        for player in new_all_in_players:
            pass

    def _print_public_cards(self):
        '''
        print public cards
        '''
        string = '\nCurrent public cards: '

        for card in self.public_cards:
            string += f"{card}  "

        print(string)
    
    def _find_winner(self):
        '''
        Find winner after river
        and give the pot to the winner
        '''
        best_hands = []
        print(f"Cards on the table:")
        self._print_public_cards()
        #print(f"{self.public_cards[0]}  {self.public_cards[1]}  {self.public_cards[2]}  {self.public_cards[3]}  {self.public_cards[4]}")
        for player in self.current_players:
            time.sleep(1)
            print(f"\n{player.name} shows his cards: {player.holes[0]}  {player.holes[1]}")
            total_cards = self.public_cards + player.holes

            ## Find all combinations of hands
            combs = list(combinations(total_cards,5))
            hands = []
            for comb in combs:
                hands.append(PokerHand(comb))

            best_hand = sorted(hands, reverse=True)[0]
            best_class = classify_hand(best_hand.cards)
            best_hands.append(best_hand)
            print(f"{player.name}'s best hand is a {best_class}: {best_hand}")

        winner_idxs = [idx for idx in range(len(best_hands)) if best_hands[idx] == np.amax(best_hands)]
        
        splits = len(winner_idxs)
        split_amount = self.current_pot/splits
        winner_players = [self.current_players[idx] for idx in winner_idxs] 
        
        if len(winner_players)==1:
            winner_string = f"\n{winner_players[0].name} wins with {colored(best_hands[winner_idxs[0]].label, 'blue')}"
            winner_string += f" and takes the pot ${self.current_pot}"
        else:
            winner_string = f"We have more than one winners with {colored(best_hands[winner_idxs[0]].label, 'blue')}"
            winner_string += f"The pot ${self.current_pot} will be split into {splits} between "
            winner_string += f"{' and '.join([pl.name for pl in winner_players])}"
            
        print(winner_string)

        ## Give the winners all pot winnings:
        for player in winner_players:
            player.chips += split_amount
    
    def _update_current_players(self):
        '''
        Updates the list of current players (who haven't folded)
        '''
        self.current_players = [player for player in self.players.values() 
                                       if not player.fold]
                
    def _display_table(self, colored_player: Player):
        '''
        Display current table's bet status

        Highlight the colored_player
        '''
        player = self.small_blind_player 
        player_string = ""
        bet_string = ""

        count = 0
        while count!=len(self.players):
            if player.name==colored_player.name and not player.fold:
                current_player_string = f" {colored(player, 'green')} " + "-->"
                #print(f"length of {player}: {len(current_player_string)}")
                offset = 9
            else:
                if player.fold:
                    current_player_string = f" {colored(player, 'red')} " + "-->"
                    #print(f"length of {player}: {len(current_player_string)}")
                    offset=9
                elif player.all_in:
                    current_player_string = f" {colored(player, 'magenta')} " + "-->"
                    #print(f"length of {player}: {len(current_player_string)}")
                    offset=9

                else:
                    current_player_string = f" {colored(player, 'yellow')} " + "-->"
                    #print(f"length of {player}: {len(current_player_string)}")
                    offset=9
                    
            current_bet_string = ""
            player_string += current_player_string

            if player.fold:
                current_bet_string += " "
                fold_str = f"fold $({player.total_bet})"
                current_bet_string += fold_str
                ## offset for colored string
                current_bet_string += " "*(len(current_player_string)-len(current_bet_string)-offset)
            elif player.all_in:
                current_bet_string += " "
                fold_str = f"ALL IN $({player.total_bet})"
                current_bet_string += fold_str
                ## offset for colored string
                current_bet_string += " "*(len(current_player_string)-len(current_bet_string)-offset)

            else:
                current_bet_string += " "
                amount_str = f"${player.current_bet}"
                current_bet_string += amount_str
                current_bet_string += " "*(len(current_player_string)-len(current_bet_string)-offset)

            bet_string += current_bet_string
            player = player.next
            count+=1
            

        print(f"\n{'*'*(len(player_string)-offset)}")
        print(f"{player_string}")
        print(bet_string)
        if self.public_cards:
            self._print_public_cards()
        print(f"{'*'*(len(player_string)-offset)}")
        
    def show_all(self):
        '''
        Show everyone's cards (who are in the current round)
        '''
        for player in self.players.values():
            print(f"{player.name}'s cards: {player.holes}'")
            
def classify_hand(cards: List[Card]):
    '''
    Classify a poker hand (5 cards) into categories
    
    Parameters
    '''
    assert len(cards)==5
    cards = sorted(cards, reverse=True)
    
    count_dct = defaultdict(int)
    for card in cards:
        count_dct[card.val]+=1
        
    count_lst = list(count_dct.values())
    
    nums = [card.val for card in cards]
    suits = [card.suit for card in cards]
    
    if len(set(nums))==5 and len(set(suits))>1 and abs(cards[0]-cards[4])!=4:
        return "High Card"
    
    elif len(set(nums))==4:
        return "One Pair"
    
    elif count_lst.count(2)==2 :
        return "Two Pair"
    
    elif count_lst.count(3) == 1  and  count_lst.count(2) == 0:
        return "Three of a Kind"
    
    elif abs(cards[0]-cards[4])==4 and len(set(suits))!=1:
        return "Straight"
    
    elif len(set(suits))==1 and abs(cards[0]-cards[4])!=4:
        return "Flush"
    
    elif count_lst.count(3) != 0 and  count_lst.count(2) == 1:
        return "Full House"
    
    elif count_lst.count(4) != 0:
        return "Four of a Kind"
    
    elif abs(cards[0]-cards[4])==4 and len(set(suits))==1 and cards[0].val!='A':
        return "Straight Flush"
    
    else:
        return 'Royal Flush'

def print_sorted_dct(d):
    lst = [(k, v) for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True)]
    for t in lst: 
        print(f'{t[0]} : {t[1]}')

def main():
    parser = argparse.ArgumentParser(description='Set up a poker table and play')
    
    parser.add_argument('-b', '--buyin', 
                        type=int, 
                        default=1000,
                        help='buy in amount')

    parser.add_argument('-p', '--players', 
                        type=str, 
                        default="a b",
                        help='player names separated by space')

    parser.add_argument('-s', '--show', 
                        type=str, 
                        default="a",
                        help='player names separated by space whose private cards are to be shown')

    args = parser.parse_args()

    game = PokerGame(chips=args.buyin,
                     players = args.players.split())

    game.play(show=args.show.split())

if __name__ == "__main__":
    main()


