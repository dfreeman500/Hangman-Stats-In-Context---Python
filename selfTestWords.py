# import random
from collections import Counter
from collections import defaultdict ### handles error no key present - fills in the value
import csv
import timeit
import time
from tqdm import tqdm
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

red = "\033[0;31m"
end="\033[0m"

start = timeit.default_timer()
print('Time: ', start)

#Function to write to worddata.csv
def writeToCSV(test_word=0, already_guessed=0, already_guessed_incorrect=0, filename=0, mode='w', solved=True):
    with open('worddata.csv', mode=mode) as csv_file:
        fieldnames = ['word', 'word_length_for_file', 'number_of_guess_for_file',
                  'number_of_incorrect_guesses_for_file', 'which_list_solved_word', 'letters_guessed_in_order', 'letters_guessed_incorrectly']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, lineterminator='\n')

        if mode=='w':
            writer.writeheader()
        if mode=='a' and solved==False:
            writer.writerow({'word': test_word, 'word_length_for_file': len(test_word),
                        'number_of_guess_for_file': len(already_guessed),
                        'number_of_incorrect_guesses_for_file': len(already_guessed_incorrect),
                        'which_list_solved_word': filename,
                        'letters_guessed_in_order': already_guessed,
                        'letters_guessed_incorrectly': already_guessed_incorrect
                        })

        if mode=='a' and solved== True:
            writer.writerow({'word': test_word, 'word_length_for_file': len(test_word),
                                'number_of_guess_for_file': len(already_guessed),
                                'number_of_incorrect_guesses_for_file': len(already_guessed_incorrect),
                                'which_list_solved_word': filename,
                                'letters_guessed_in_order': already_guessed,
                                'letters_guessed_incorrectly': already_guessed_incorrect
                                })
#writes the header to worddata.csv
writeToCSV(test_word=0, already_guessed=0, already_guessed_incorrect=0, filename=0, mode='w', solved=True)


####House Keeping - Run Once ####
# Creates  dictionaries with key being length of word 
# and value being [word, enumerated dictionary of word, lowercase word, set of letters in word]
# defaultdict is used to fill in key value to handle errors if a word is
# passed in that has key not present (ex: 100 letter long word)

word_list_5000 = defaultdict(list)
word_list_big = defaultdict(list)

list_of_filenames = ["5000EnglishWordsFrequency.txt", "words.txt"]


for x in list_of_filenames:
    with open(dir_path+"/"+x) as wordbook:   #'with' opens file and then closes immediatly after
        words = (line.rstrip('\n') for line in wordbook)
        for word in words:
            if word.isalpha():
                if x == "5000EnglishWordsFrequency.txt":
                    word_list_5000[len(word)].append((word.lower(), dict(enumerate(word.lower())), list(word.lower()), set(list(word.lower()))))
                if x == "words.txt":
                    word_list_big[len(word)].append((word.lower(), dict(enumerate(word.lower())), list(word.lower()), set(list(word.lower()))))

### End House Keeping ###

def computer_guess_word (test_word, length, partial_word, word_group):
    already_guessed = [] #keeps track of letters already guessed so far
    if word_group == word_list_5000[len(test_word)]:
        filename= "5000EnglishWordsFrequency.txt"

    if len(word_group)==0:  # if the small frequency word list has no items in it, switch to the big word list
        word_group =word_list_big[length]

    while True:
        list_of_sets_of_letters = [] #will contain the set of letters from valid words- used for letter frequency
        compare_dict={} #will be a dictionary of partial word and the letters by position
        user_supplied_letters = list(''.join(filter(str.isalpha, partial_word.lower()))) #takes the alpha only items in partial_word and stores it into user supplied letters
        already_guessed_incorrect = set(already_guessed) - set(user_supplied_letters)

        x=0
        for item in partial_word: # iterate through item in partial word that is supplied by the user
            if item.isalpha():  # if the item is alphabetic
                compare_dict[x]=item.lower()    #take it and store it as a value in a dictionary where key, value is index,
            x+=1

        if word_group == word_list_big[length]:
            filename = "words.txt"

        new_word_list = [] #This list has all of the words that are of the correct length and also have the guessed letters in the correct location
        for word in word_group:    #go through all of the words in the word_group list,
            isCandidate = True
            if set(compare_dict.items()) <= set(word[1].items()) and word[3].isdisjoint(already_guessed_incorrect):  # # For each word it takes the 2 dictionaries and if the dictionary of user given index,letters is within the dictionary of the index,letters for the word of the same length it is saved
                for (key, value) in (word[1].items()):
                    if (key, value) not in compare_dict.items() and value in user_supplied_letters:  ### DO i need after the 'and'
                        isCandidate = False
                        break
                if isCandidate:
                    new_word_list.append(word)
                    list_of_sets_of_letters.extend(word[3])  # Gets the set of letters from the word and puts in list_of_letters for word frequency

        ## try sorting counter - don't need .most_common. Can use 'sorted' function
        letter_frequency=Counter(list_of_sets_of_letters).most_common(26) #Gets the  26 most frequent letters (lower case)
        letter_frequency_just_letters_in_order=[]

        for x in letter_frequency:
            letter_frequency_just_letters_in_order.append(x[0])

        if word_group == word_list_big[length] and len(new_word_list)==0:            
            print(red + "Woah, Something doesn't seem right! Please look at the letters I've already guessed and make sure they are in the correct spots." + end)
            writeToCSV(test_word, already_guessed, already_guessed_incorrect, filename="NOT IN ANY LIST", mode='a', solved=False)
            break

        if word_group == word_list_5000[length] and len(new_word_list)==0:
            word_group = word_list_big[length]
            continue            #Goes to the top of the While loop

        # use for x in reversed(letter_frequency_just_letters_in_order): to solve using lowest frequency
        for x in letter_frequency_just_letters_in_order: 
            if x not in compare_dict.values() and x not in already_guessed:
                    already_guessed.append(x)
                    break

        partial_word = []
        for item in test_word.lower(): #recreates the partial word based on letters guessed
            if item in already_guessed:
                partial_word.append(item.lower())
            else:
                partial_word.append("_")
        partial_word = ''.join(partial_word)

        if partial_word == test_word.lower(): #checks if the partial word is equal to the original test_word
            writeToCSV(test_word, already_guessed, already_guessed_incorrect, filename, mode='a', solved=True)
            break


with open("5000EnglishWordsFrequency.txt") as wordbook:
    words = (line.rstrip('\n') for line in wordbook)
    # words = ['alksdhflkajhfalkdfh','asdlfjkhasdfiqwureiuher','asdfffffffffffffffffffffffffff', 'teratoblastoma','run'] #test to see how manages not found words
    for test_word in tqdm(words):
        if test_word.isalpha():
            partial_word = test_word.lower()
            computer_guess_word(test_word, len(test_word), len(test_word) * "_", word_group = word_list_5000[len(test_word)])



stop = timeit.default_timer()
print('Time: ', stop - start)  