import requests
import codecs
from bs4 import BeautifulSoup


class QuestionException(Exception):
    def __init__(self, url="Error parsing question"):
        Exception.__init__(self, "Error on " + url)


class GameError(Exception):
    def __init__(self, game="Game does not exist"):
        Exception.__init__(self, "Game " + game + " does not exist")


def get_title(question):
    """
    Gets the title from the question html
    :param question: the question html 'object'
    :return: the text of the tile
    """

    items = question.find_all('strong')
    if len(items) == 0:
        raise QuestionException
    title = items[0].get_text().strip()
    if 'Savage' in title:
        title = title[:-7].strip()
    return title


def get_answers(question):
    """
    Gets a list of all the answers and the correct answer from html
    :param question: the html question 'object'
    :return: the answers then the correct answer index in a list
    """
    answers = question.find('ul', {'class': 'questions'})
    if answers is None:
        raise QuestionException("question missing")
    answers = answers.find_all('li')
    all_answers = []

    for answer in answers:
        answer = answer.get_text()
        if 'Correct' in answer:
            answer = answer[:-8]
        all_answers.append(answer)

    for answer in answers:
        # the answer has a span, incorrect does not
        if answer.find('span') is not None:
            answer_text = answer.get_text()
            # remove trailing space
            all_answers.append(answer_text[:-8])

    return all_answers


def write_one_game(url):
    # local testing file
    # soup = BeautifulSoup(open('hq.html', encoding='utf8'), 'lxml')

    headers = {"user-agent": "questionScrape"}
    req = requests.get(url, headers)
    req.encoding = 'utf-8'
    # soup the url
    soup = BeautifulSoup(req.text, "html5lib")

    # find all question classes, minus the last (winner data)
    questions = soup.find_all("div", {"class": "question"})[:-1]
    if len(questions) == 0:
        raise GameError

    # open the file to write to
    f = codecs.open('questions.txt', 'a')

    # loop through all the questions
    for q in questions:
        # wrap in try except to catch sponsors embedded in qs list
        try:
            title = get_title(q)
            title = title.replace('“', '"')
            title = title.replace('”', '"')
            title = title.replace('’', "'")
            # get the answers
            answers = get_answers(q)
            # turn answers list into string
            answers_str = ",".join(answers)
            # write the answers
            try:
                f.write(title + '|' + answers_str + '\n')
            except UnicodeEncodeError:
                print("error writing question")
                continue
        except QuestionException:
            print(QuestionException("question"))

    f.close()


def main():
    # set url
    req = requests.get('http://hqbuff.com/')
    soup = BeautifulSoup(req.text, 'html5lib')
    # get all the games from hqbuff
    links = soup.find_all("ul", {"class": "list--archive"})[0]
    all_games = [link.get('href') for link in links.find_all('a')]
    # write the data for every question in the games to the file
    for link in all_games:
        url = 'http://hqbuff.com' + link
        try:
            write_one_game(url)  # we must prepend the url
        except GameError:
            print(GameError(url))

        # now for second game

        url = 'http://hqbuff.com' + link[:-1] + "2"
        try:
            write_one_game(url)
        except GameError:
            print(GameError(url))


if __name__ == main():
    main()
