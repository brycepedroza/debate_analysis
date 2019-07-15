import requests
import re
import string
import json

from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer


def quote_to_arr(quote: str) -> tuple:
    quote = ''.join([i if ord(i) < 128 else ' ' for i in quote])

    # grab stop words
    stop_words = stopwords.words('english')
    add_to_stop_words = [',', '-', ';', ':', '--', "'", '(', ')',
                         "\"", "\'", '', 'it\'s', 'thats', 'ok',
                         'okay', 'got', 'dont', 'hes', 'im']
    stop_words.extend(add_to_stop_words)
    exclude = set(string.punctuation)
    stop_words = set(stop_words)
    lemma = WordNetLemmatizer()
    stop_free = " ".join([i for i in quote.lower().split() if i not in stop_words])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized.split(), quote.split()

    # remove them
    # for i in stop_words:
    #     if i in quote_arr:
    #         while i in quote_arr:
    #             quote_arr.remove(i)
    #
    # return quote_arr, raw_quote_arr


def get_webpage(url: str) -> list:
    page = requests.get(url)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, 'html.parser')
    # Grab all the p tags
    p_tags = soup.find_all('p')
    quotes = [p.get_text() for p in p_tags]
    return quotes


def parse_first_transcript(transcript) -> dict:
    quotes = {
        'corpus': []
    }
    order = 1
    pattern = '^.\\S*:'
    person = ''

    for line in transcript:
        if re.search(pattern, line) or line.startswith("DIAZ BALART:"):
            # Then we found a line that starts with 'BIDEN:' for example
            split_line = line.split(': ')
            try:
                person = split_line[0].replace(" ", "")
                quote = split_line[1]
            except IndexError:
                print("There was a problem parsing the following line in the transcript \n{}".format(line))
                continue
            if len(split_line) > 2:
                # Make sure the entire quote is in one str
                quote = ":".join(split_line[1:])
                # quote = split_line[1:].join(':')
            quote_arr, raw_quote = quote_to_arr(quote)
            if quotes.get(person):
                quotes.get(person).append(
                    {'parsed': quote_arr, 'raw': raw_quote, 'order': order})
            else:
                quotes.update(
                    {person: [{'parsed': quote_arr, 'raw': raw_quote, 'order': order}]})
        else:
            # If the line didn't start with the regex,
            # then its new line from the previous speaker
            quote_arr, raw_quote = quote_to_arr(line)
            quotes.get(person).append(
                {'parsed': quote_arr, 'raw': raw_quote, 'order': order})
        quotes.get('corpus').append(
            {'parsed': quote_arr, 'raw': raw_quote, 'order': order})
        order += 1
    return quotes


def parse_second_transcript(transcript) -> dict:
    quotes = {
        'corpus': []
    }
    order = 1
    person = ''
    pattern = '^.\\S*:'

    for line in transcript:
        if re.search(pattern, line) or line == "DIAZ BALART:":
            # Then this is the person that is talking
            person = line[:len(line) - 1].replace(" ", "")
        else:
            # Then we can add this line to the person if it is not
            # applause, laughter, or crosstalk
            if not line.startswith("(LAUGHTER)") \
                    and not line.startswith("(APPLAUSE)") \
                    and not line.startswith("(CROSSTALK)"):
                quote_arr, raw_quote = quote_to_arr(line)
                if quotes.get(person):
                    quotes.get(person).append(
                        {'parsed': quote_arr, 'raw': raw_quote, 'order': order})
                else:
                    quotes.update(
                        {person: [{'parsed': quote_arr, 'raw': raw_quote, 'order': order}]})
                order += 1
                quotes.get('corpus').append(
                    {'parsed': quote_arr, 'raw': raw_quote, 'order': order})
    return quotes


if __name__ == '__main__':
    debate_night_two = "https://www.nytimes.com/2019/06/28/us/politics/transcript-debate.html"
    debate_night_one = "https://www.nytimes.com/2019/06/26/us/politics/democratic-debate-transcript.html"

    # The two transcripts have different styles, which makes it impossible to parse the same way for both
    first_night_transcript = get_webpage(debate_night_one)
    first_night_transcript = first_night_transcript[3:548]
    first_night_quotes = parse_first_transcript(first_night_transcript)

    # Now the second night
    second_night_transcript = get_webpage(debate_night_two)
    second_night_transcript = second_night_transcript[3:1424]
    second_night_quotes = parse_second_transcript(second_night_transcript)

    # Lets write it out to a JSON so we can save it and use it for later
    with open('night_one.json', '+w') as outfile:
        json.dump(first_night_quotes, outfile)
    with open('night_two.json', '+w') as outfile:
        json.dump(second_night_quotes, outfile)
