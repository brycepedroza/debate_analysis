import json
import nltk


def read_json(file_name: str) -> dict:
    with open(file_name, 'r') as infile:
        return json.load(infile)


def word_freq(arr: list, num_of_words: int):
    """
    Frequency Distribution on an arr of strs.
    :param arr: all words
    :param num_of_words: number of top responses to be saved

    :return: dict to be used for a word map?
    """
    freq_dist = nltk.FreqDist(arr)
    trimmed_result = freq_dist.most_common(num_of_words)
    return trimmed_result


def analyze_candidate(candidate: dict) -> list:
    all_quotes = []
    for quote in candidate:
        all_quotes.extend(quote.get('parsed'))
    return word_freq(all_quotes, 20)
    pass



if __name__ == "__main__":
    night_one = read_json('night_one.json')
    night_two = read_json('night_two.json')
    for key, value in night_one.items():
        most_common_words = analyze_candidate(value)
        pass
    pass


