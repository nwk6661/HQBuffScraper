# -*- coding: utf-8 -*-
import requests
import codecs
from bs4 import BeautifulSoup
import json
import os, sys

# Make a top level dict for answer distributions
answers = {1: 0, 2: 0, 3: 0}


class GameError(Exception):
    def __init__(self, game="Game does not exist"):
        Exception.__init__(self, "Game " + game + " does not exist")


def write_one_game(url, file):
    """
    Writes one game to the file
    :param url: the url of the game we are writing (date format)
    :param file: the file we are writing to
    :return:
    """
    url = "https://hqbuff.com/api/" + url

    headers = {"user-agent": "questionScrape"}
    req = requests.get(url, headers)
    req.encoding = 'utf-8'

    data = json.loads(req.text)
    if len(data) == 0:
        raise GameError

    # loop through every game
    for game in data:
        # we only care about the question key
        for question in game['questions']:
            answer_str = ""
            correct = ""
            title = question['text']
            # loop through all answers, store the correct one
            for a in question['answers']:
                answer_str += a['text'] + ","
                if a['correct']:
                    correct = a['text']
            answer_str += correct

            # write the final output to the file
            try:
                file.write(title + '|' + answer_str + '\n')
            # this should'nt come up anymore, but just in case there is a strange symbol
            except UnicodeEncodeError:
                print("error writing question")
                continue


def one_game_statistics(url):
    """
    Generates statistics for a game, such as answer distribution or savage questions
    :param url: the url of the game we are writing (date format)
    :return:
    """

    # global the dict to store answers across all games
    global answers

    url = "https://hqbuff.com/api/" + url

    headers = {"user-agent": "questionScrape"}
    req = requests.get(url, headers)
    req.encoding = 'utf-8'

    data = json.loads(req.text)
    if len(data) == 0:
        raise GameError

    # loop through every game for the day
    for game in data:
        # we only care about the question key
        for question in game['questions']:
            answer_str = ""
            correct = ""
            title = question['text']
            # loop through all answers, store the correct one
            # keep track of the answer number (1,2,3)
            ans_num = 1
            for a in question['answers']:
                answer_str += a['text'] + ","
                if a['correct']:
                    correct = a['text']
                    # Add optional 'if' statement here#
                    answers[ans_num] += 1
                ans_num += 1
            answer_str += correct


def main():
    # set url
    req = requests.get('http://hqbuff.com/')
    soup = BeautifulSoup(req.text, 'html5lib')
    # get all the games from hqbuff
    links = soup.find_all("ul", {"class": "list--archive"})[0]
    # slice the game urls to be in YYYY-MM-DD format
    all_games = [link.get('href')[6:16] for link in links.find_all('a')]

    # open the file outside of the loop so we dont open and close the file many times
    if len(sys.argv) == 2:
        f = codecs.open('questions/questions.txt', 'w', encoding='utf-8')
    else:
        f = codecs.open('questions.txt', 'w', encoding='utf-8')

    # set this to true to use statistics mode
    statistics = False

    # write the data for every question in the games to the file
    for link in all_games:
        try:
            if statistics:
                one_game_statistics(link)
            else:
                write_one_game(link, f)  # we must prepend the url
        except GameError:
            print(GameError(link))

    f.close()

    # print answer distribution
    if statistics:
        print(answers)
        print(sum(answers.values()))


if __name__ == main():
    main()
