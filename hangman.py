from random import choice
from datetime import datetime
from typing import List


class YangDS:
    def __init__(self, dictionary):
        self.length_char_frequency = {}
        self.length_char_freq_sorted = {}  # {1, ["a","e"]}
        self.length_word = {}  # lookup by the length of the word
        for word in dictionary:
            temp = {}
            if len(word) not in self.length_word:
                # first item is the char lookup
                self.length_word[len(word)] = {}
            if len(word) not in self.length_char_frequency:
                self.length_char_frequency[len(word)] = {}
            for i in range(len(word)):
                char = word[i]
                if char not in temp:
                    temp[char] = []
                temp[char].append(i)  # "a":[1,2]
            self._add_temp_into_char_frequency(len(word), temp, self.length_char_frequency)
            # add temp into the length_char_frequency
            self._add_temp_into_hash(word, temp, self.length_word)
            # convert temp into hashes, then append hash into the self.length_word, # 3 : {"a1":["bad"], "b0":"[bad], "d2":["bad"]}
        for k, v in self.length_char_frequency.items():
            self.length_char_freq_sorted[k] = [k for k, _ in
                                               sorted(v.items(), reverse=True, key=lambda item: item[1])]

    def _add_temp_into_hash(self, word, temp, length_word):
        for k, v in temp.items():
            position_hash = str(v)
            char_hash = f"{k}:{position_hash}"
            if char_hash not in length_word[len(word)]:
                length_word[len(word)][char_hash] = []
            length_word[len(word)][char_hash].append(word)

    def _add_temp_into_char_frequency(self, length, temp, char_frequency):
        for k, v in temp.items():
            if k not in char_frequency[length]:
                char_frequency[length][k] = len(v)
            char_frequency[length][k] += len(v)
        return char_frequency


class HangManGame:
    def __init__(self, dictionary):
        self.finished = True
        self.attempts = 6
        self.word = None
        self.shown = None
        self.guessed = {}
        self.dictionary = dictionary

    def restart(self):
        self.finished = False
        self.attempts = 6
        self.word = self.get_random_word()
        self.shown = ["*" for _ in range(len(self.word))]
        self.guessed = {}
        return self.shown

    def guess(self, character):
        if self.finished:
            raise Exception("game over")
        if character in self.guessed:
            return self.shown
        self.guessed[character] = True
        if character not in self.word:
            self.attempts -= 1
            if self.attempts < 1:
                self.finished = True
            return self.shown
        # character is guess correctly
        for i in range(len(self.word)):
            if self.word[i] == character:
                self.shown[i] = character
        if "*" not in self.shown:
            self.finished = True
        return self.shown

    def get_random_word(self):
        # todo grab a word from a dictionary
        return choice(self.dictionary)


def correct_guess(prev, current):
    return not prev == current


def success(current):
    return "*" not in current


class HangManGuesser:
    def __init__(self, hangman_game: HangManGame, dictionary: List[str]):
        self.game = hangman_game
        self.first_level_memo_state = YangDS(dictionary)

    def build_hash_from_display(self, char, state):
        pos = []
        for i in range(len(state)):
            if state[i] == char:
                pos.append(i)
        position_hash = str(pos)
        char_hash = f"{char}:{position_hash}"
        return char_hash

    def solve(self):
        # tries to solve the game, and result either in solving it, or failing to solve
        game_display = self.game.restart()[:]
        num_of_char = len(game_display)
        look_up_ds = self.first_level_memo_state
        first_lookup = True
        guessed = []
        while True:
            most_likely_character = look_up_ds.length_char_freq_sorted[num_of_char]
            for char in most_likely_character:
                if char in guessed:
                    continue
                new_game_state = self.game.guess(char)
                if not correct_guess(game_display, new_game_state):
                    continue
                if success(new_game_state):
                    return new_game_state
                guessed.append(char)
                game_display = new_game_state[:]
                break  # break if correct guess
            # find the hash of the first char
            guessed_hash = self.build_hash_from_display(guessed[-1], game_display)
            possible_words = look_up_ds.length_word[num_of_char][guessed_hash]
            if len(possible_words) == 1:
                return possible_words[0]
            # update the look_up_ds.
            look_up_ds = YangDS(possible_words)

            # given guessed characters, and the possible words, have a function return back the most likely char, and the hashmap lookup
            # else still need to search.

            # find the second most likely character... and continue


if __name__ == "__main__":
    with open('dictionary.txt') as word_file:
        my_dictionary = word_file.read().split()

    # my_dictionary = ["random", "hello", "world"]
    t1 = datetime.now()
    game = HangManGame(my_dictionary)
    guesser = HangManGuesser(game, my_dictionary)
    print(f"with dictionary size of {len(my_dictionary)} memoization time {datetime.now() - t1}")
    guessed = 0
    correct = 0
    iterations = 10000
    print(f"with dictionary size of {len(my_dictionary)} with {iterations}# of iterations")
    start_time = datetime.now()
    for n in range(iterations):
        try:
            result = guesser.solve()
            correct += 1
        except Exception:
            pass
        finally:
            guessed += 1
    delta = datetime.now() - start_time
    print(f"guessed {guessed}, got {correct} many correct, {correct / guessed * 100}% success rate")
    print(f"took {delta} in total, avg of {delta / iterations}")
    # hangman game randomly picks out a word, and it would return back the result in ****** to represent the game.
#
