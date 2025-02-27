"""
# H008a - A Correlational Study of Caffeine Consumption and Its Effect on Insight Problem 
# Created by Lina Z. and Cyrus K.
# Last edited on: 2025-02-27

This code serves as the primary script for H008a, a correlational study 
examining the effects of caffeine consumption on insight problem-solving. 
The first section defines a dictionary containing all insight problems and 
their solutions, categorized by mathematical, verbal, or spatial characteristics. 
In addition to correct answers, the dictionary includes potential incorrect 
responses and corresponding feedback.

In the latter section, the dictionary is integrated into an automated system 
that facilitates answering questions and providing feedback. This automation 
enables remote data collection and minimizes human bias. A large language model 
was incorporated to evaluate response accuracy. The LLM leveraged the pre-defined 
incorrect solutions and feedback to assess participant responses. 

In the preliminary pilot study, we collected the participants' response time, 
solutions, and hint provided by the system.

"""

# Import libraries 
from csv import writer, QUOTE_MINIMAL
from datetime import datetime
from openai import OpenAI
import os
import sys
import shutil
import random


# Function to clear the terminal
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def center_text(text):
    """Centers text horizontally in the terminal."""
    columns, _ = shutil.get_terminal_size()
    horizontal_padding = (columns - len(text)) // 2
    return " " * horizontal_padding + text

# Setup ChatGPT client
client = OpenAI()

# Setup insight questions
dict_of_question_info = {
    # VERBAL PROBLEMS
    "christmas_NY_problem"  : {
        "insight_question"              : "'In what year did Christmas and New Year's fall in the same year?'",
        "insight_answer"                : "'Every year'",
        "possible_incorrect_solution"   : "'0 AD' or '2025' or 'None of them', respectively",
        "possible_incorrect_feedback"   : "'That's not the only year' or 'They did fall in the same year', respectively",
        "problem_type"                  : "VERBAL"
        },
    "triplet_problem"  : {
        "insight_question"              : "'Marsha and Marjorie were born on the same day of the same month of the same year to the same mother and the same father - yet they are not twins. How is that possible?'",
        "insight_answer"                : "'They're triplets' or 'They're quadruplets' or 'They're quintuplets', respectively",
        "possible_incorrect_solution"   : "'They're fraternal twins' or 'After giving birth to one child, the mother and father travel to another country in a different child to have the second child', respectively",
        "possible_incorrect_feedback"   : "'Regardless of if they're fraternal or identical, twins are twins, and these two are not twins' or 'This doesn't change the fact that they're not twins', respectively",
        "problem_type"                  : "VERBAL"
        },
    "light_switch_problem"  : {
        "insight_question"              : "'The legendary runner Flash Fleetfoot was so fast that his friends said he could turn off the light switch and jump into bed before the room darkened. On one occasion, Flash proved he could do it. How?'",
        "insight_answer"                : "'He went to bed during the day'",
        "possible_incorrect_solution"   : "'He has superpowers' or 'He's really fast', respectively",
        "possible_incorrect_feedback"   : "'He's a regular human' or 'We already established he's fast', respectively",
        "problem_type"                  : "VERBAL"
        },
    "reading_problem"  : {
        "insight_question"              : "'What is the common phrase illustrated here? |r|e|a|d|i|n|g|'",
        "insight_answer"                : "'Reading between the lines'",
        "possible_incorrect_solution"   : "'r e a d i n g' or 'read the lines in between', respectively",
        "possible_incorrect_feedback"   : "'There's more to it than that. We are looking for a classic phrase' or 'You're close, but we're looking for a specific phrase', respectively",
        "problem_type"                  : "VERBAL"
        },
    "unlisted_phone_numbers_problem"  : {
        "insight_question"              : "'There is a town in Northern Ontario where 5 percent of all the people living there have unlisted phone numbers. If you selected 100 names at random from the town's phone directory, on average, how many of these people selected would have unlisted phone numbers?'",
        "insight_answer"                : "'None, unlisted phone numbers are not in the directory'",
        "possible_incorrect_solution"   : "'5' or '100', respectively",
        "possible_incorrect_feedback"   : "'5 percent of 100 is 5, but that doesn't indicate the average' or 'There are 100 names selected at random', respectively",
        "problem_type"                  : "VERBAL"
        },
    "baseball_game_problem"  : {
        "insight_question"              : "'A famous super-psychic could tell the score of any baseball game before it starts. What was his secret?'",
        "insight_answer"                : "'The starting score is always 0 to 0'",
        "possible_incorrect_solution"   : "'He's a time traveler' or 'He can predict the future', respectively",
        "possible_incorrect_feedback"   : "'Time traveling is not possible' or 'Although he's a psychic, he's unable to predict the future', respectively",
        "problem_type"                  : "VERBAL"
        },
    # MATHEMATICAL PROBLEMS
    "sock_problem"  : {
        "insight_question"              : "'If you have black socks and brown socks in your drawer, mixed in a ratio of 4 to 5, how many socks will you have to take out to ensure you have a pair of the same color?'",
        "insight_answer"                : "'Three - if the first is brown and the second black, then the third one will match either the brown or black'",
        "possible_incorrect_solution"   : "'9' or '2', respectively",
        "possible_incorrect_feedback"   : "'Taking the sum of the ratio does not make a pair' or 'Two socks make a pair, but does not guarantee a matching pair', respectively",
        "problem_type"                  : "MATHEMATICAL"
        },
    "matchstick_problem"  : {
        "insight_question"              : """'Describe verbally how you could move three matchsticks to make five squares: 
                                 __    __
                                |  |  |  |
                                 ¯¯|¯¯|¯¯
                                    ¯¯
                                          '""",
        "insight_answer"                : "'Move the right-most matchstick and the two adjacent horizontal matchsticks to create a large square separated into four quadrant squares'",
        "possible_incorrect_solution"   : "'Move three matchsticks to make five evenly-sized squares' or 'Break the matchsticks in half to make smaller squares'",
        "possible_incorrect_feedback"   : "'Not quite, please provide more details' or 'You cannot alter the matchsticks in this problem', respectively",
        "problem_type"                  : "MATHEMATICAL"
        },
    "constraint_relaxation_problem"  : {
        "insight_question"              : """'Imagine the following Roman Numerals are made of vertical matchsticks, where “X” is two crossed matchsticks and “I” is a single matchstick. Move only a single matchstick to make a correct arithmetic equation: X + IV = V
                               ROMAN NUMERALS
                            I   = 1   , II   = 2,
                            III = 3   , IV   = 4,
                            V   = 5   , VI   = 6,
                            VII = 7   , VIII = 8
                            IX  = 9   , X    = 10
                            XV  = 15  , XX   = 20
                                          '""",
        "insight_answer"                : "'Imagine the following Roman Numerals are made of vertical matchsticks, where “X” is two crossed matchsticks and “I” is a single matchstick. Move the vertical matchstick from the “+” sign to create a sum of “VI”'",
        "possible_incorrect_solution"   : "'Use one of the matchsticks from the plus sign to create an unequal sign' or, respectively ",
        "possible_incorrect_feedback"   : "'You cannot create an unequal (not-equal) sign' or, respectively",
        "problem_type"                  : "MATHEMATICAL"
        },
    "chunk_decomposition_problem"  : {
        "insight_question"              : """'Move only a single matchstick to make a correct arithmetic equation: V = XI - I
                               ROMAN NUMERALS
                            I   = 1   , II   = 2,
                            III = 3   , IV   = 4,
                            V   = 5   , VI   = 6,
                            VII = 7   , VIII = 8
                            IX  = 9   , X    = 10
                            XV  = 15  , XX   = 20

                                          '""",
        "insight_answer"                : "'Move a matchstick from the “X” to create a “V”' or 'Move the vertical matchstick from the plus sign to the “X” to create “IX”'",
        "possible_incorrect_solution"   : "'Switch the equal signs' or 'Take a matchstick from “V” and add it to the “I” to create “X”' or 'Use one of the matchsticks from the plus sign to create an unequal sign', respectively",
        "possible_incorrect_feedback"   : "'This results in a calculation error' or 'In order to make this operation correct, you'd have to change the rotation of two matchsticks, which is not allowed' or 'You cannot create an unequal (not-equal) sign', respectively",
        "problem_type"                  : "MATHEMATICAL"
        },
    "coin_problem"  : {
        "insight_question"              : """'Move two coins so that each coin touches three other coins:
                                 _   _   _
                                (_)_(_)_(_)
                                 _(_)_(_)_
                                (_) (_) (_)

                                          '""",
        "insight_answer"                : "'Move two coins such that each coin creates two stacks of four'",
        "possible_incorrect_solution"   : "'Move one of the right coins to the top, in between the two top-most coins. Then move the other right coin to the bottom, in between the two bottom-most coins'",
        "possible_incorrect_feedback"   : "'With this formation, the only coin touching three other coins is the center coin. All other coins touch two'",
        "problem_type"                  : "MATHEMATICAL"
        },
    "fill_in_the_blank_problem"  : {
        "insight_question"              : "'Fill in the blank: 2, 4, 6, 30 32, 34, 36, 40, 42, 44, 46, 50, 52, 54, 56, 60, 62, 64, 66, __?'",
        "insight_answer"                : "'2000 (the next number without an e in it)'",
        "possible_incorrect_solution"   : "'70' or '90', respectively",
        "possible_incorrect_feedback"   : "'The next number in this sequence is not 70' or 'Unlike the jump between 6 and 30, you do not add 30 to achieve the next number in the sequence', respectively",
        "problem_type"                  : "MATHEMATICAL"
        },
    # SPATIAL PROBLEMS
    "two_string_problem"    : {
        "insight_question"              : "'You are in a room with two strings hanging from the ceiling and a pair of pliers. The strings are too far apart to grab both at the same time. How can you tie them together?'",
        "insight_answer"                : "'The solution involves using the pliers as a weight to create a pendulum effect by swinging one string toward the other'",
        "possible_incorrect_solution"   : "'Cut one string and tie it to the other' or 'Throw one string and catch the other', respectively",
        "possible_incorrect_feedback"   : "'You cannot cut the strings' or 'The string is too light to be thrown and are attached to the ceiling', respectively",
        "problem_type"                  : "SPATIAL"
        },
    "chain_problem"  : {
        "insight_question"              : """'A girl has three pieces of chain. Each piece is made up of two links (below). She wants to join the pieces into a single closed loop of chain, like a necklace. To open a link costs 2 cents, and to close a link costs 1 cent. She only has 6 cents. How does she do it?
                                  ⚭ ⚭ ⚭
                                          '""",
        "insight_answer"                : "'Open all the links from one piece and use those to attach the three remaining pieces together'",
        "possible_incorrect_solution"   : "'Open one link from each chain and link them together' or 'Open two links at once from two of the chains. Use those four open links to connect all the chains', respectively",
        "possible_incorrect_feedback"   : "'You would spend 6 cents to open and close 3 links, but you're still left with an open loop of chain' or 'Opening two links at once will still cost 2 cents each to open and 1 cents each to close. With this strategy, you've spent 12 cents', respectively",
        "problem_type"                  : "SPATIAL"
        },
    "deck_of_cards_problem"  : {
        "insight_question"              : "'Three cards lie face down on a table, arranged in a row from left to right. We have the following information about them: (a) The Jack is to the left of the Queen, (b) The Diamond is to the left of the Spade, (c) The King is to the right of the Heart, and (d) The Spade is to the right of the King. Which card – by face and suit – occupies each position?'",
        "insight_answer"                : "'Jack of Hearts, King of Diamonds, Queen of Spades'",
        "possible_incorrect_solution"   : "'Jack, Queen, Diamond, Heart, King, Spade' or, respectively",
        "possible_incorrect_feedback"   : "'The faces of a deck of cards are Jack, Queen, and King. The suits of a deck of cards are Clubs, Diamonds, Hearts, and Spades' or, respectively",
        "problem_type"                  : "SPATIAL"
        }, 
    "star_coin_problem"  : {
        "insight_question"              : """'How can you arrange these 10 pennies so that you have 5 rows (lines) of 4 pennies in each row?
                            ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯
                                          '""",
        "insight_answer"                : "'Arrange the coins in a star-shaped formation, where each “line” of the star is made up of 4 pennies'",
        "possible_incorrect_solution"   : "'Create a square' or, respectively",
        "possible_incorrect_feedback"   : "'It's not possible to create a square that meets this criteria' or, respectively",
        "problem_type"                  : "SPATIAL"
        },
    "alphabet_problem"  : {
        "insight_question"              : """'Where to put the letter Z, top or bottom line, and why?

                                AEFHIKLMNTVWXY
                                --------------
                                 BCDGJOPQRSU

                                          '""",
        "insight_answer"                : "'The “Z” is placed at the top of the line because all letters with a curved element are on the bottom'",
        "possible_incorrect_solution"   : "'The bottom line to get it closer to an even distribution' or, respectively",
        "possible_incorrect_feedback"   : "'The solution does not regard the even distribution of letters' or, respectively",
        "problem_type"                  : "SPATIAL"
        },
    "river_crossing_problem"  : {
        "insight_question"              : "'A traveler comes to a riverbank with a wolf, a goat, and a head of cabbage. There is a boat for crossing over to the other bank, but he can’t carry more than two at a time–the traveler himself and one of the two animals or the cabbage. If left alone together, the goat will eat the cabbage and the wolf will eat the goat. The wolf does not eat cabbage. How does the traveler transport his animals and his cabbage to the other side in the minimum number of round trips (back-and-forth = 1 trip)?'",
        "insight_answer"                : "'The traveler will take the goat with him to the other side. After dropping the goat off, he will row back to the riverbank. Next, the traveler will pick up the wolf and take it to the other side. He will return to the riverbank with the goat. Then, the traveler will leave the goat and take the cabbage across with him. Finally, the traveler will pick up the goat and take it to the other side' or 'First, the traveler will take the goat with him to the other side. After dropping the goat off, he will row back to the riverbank. Next, the traveler will take the cabbage with him and take it to the other side. On his return trip, the traveler will take the goat to the original riverbank. Then, the goat is dropped off and the traveler takes the wolf across, dropping the wolf off with the cabbage. Finally, the traveler will take the goat,' respectively",
        "possible_incorrect_solution"   : "'Take the wolf first,' respectively",
        "possible_incorrect_feedback"   : "'Taking the wolf first leaves the goat and cabbage together' or 'You can take everyone across in seven trips', respectively",
        "problem_type"                  : "SPATIAL"
        },
    }


def GPT_evaluate_answer(prompt, user_solution):
    if user_solution == "quit":
        clear_terminal()
        print("\nThank you for participating!")
        write_data()
        sys.exit()
    else:
        print(center_text("Checking solution..."))
        completion = client.chat.completions.create(
            model="gpt-4o-mini", # Model; can be changed to....
            messages=[
                {"role": "system",
                 "content": prompt}, # First is the intial prompt w/ correct answers
                {"role": "user",
                 "content": user_solution} # Next is the subject solution
                ]
            )
        model_evaluation = completion.choices[0].message.content # grab just text output
        model_evaluation = model_evaluation.strip() 
        return(model_evaluation)

def write_data():
    # WRITE DATA
    myFile_loc = f"data/H008a_output_data_{datetime.now()}.csv"
    # This loop writes the data in the matrix to the .csv              
    edit_myFile = open(myFile_loc, 'w', newline='')
    with edit_myFile as myFile:
        w = writer(myFile, quoting=QUOTE_MINIMAL)
        w.writerows(list_of_answers) # Write all event/trial data 
    print(f"\n- Data file written to {myFile_loc}")


# TO-DO: Shuffle order systematically
# TO-DO: Make the spatial problems suitable for participants
# TO-DO: Build data structure

list_of_answers = [["TrialNumber", "Solution", "Accuracy", "GPT_Hint"]]
trial_number = 0

# questions = list(dict_of_question_info.keys())
# random.shuffle(questions)

for question in dict_of_question_info:

    tested_trial_info = dict_of_question_info[question] # Reset the question for this trial
    trial_number += 1 # Increment trial number by 1

    # Setup loop to run experiment
    prev_answer_incorrect = False
    GPT_eval = "NA" # Output of GPT
    GPT_hint = "NA"

    # The function below interacts with ChatGPT to evaluate a subject's written
    # response. It takes two arguments: the subject's solution and the following
    # prompt, and will return either "yes" or "no" based on how close it is.
    prompt = f"""
    You are an expert in the psychological process of insight. Your goal is to
    evaluate the responses of experimental subjects to the following insight
    question: {tested_trial_info["insight_question"]}. You know that the correct 
    answer is something along the lines of: {tested_trial_info["insight_answer"]}. 
    If you are given a solution that is close enough to this one, respond with 
    'yes' and only yes.  If some other non-insightful solution, respond with a 
    sentence of feedback on why that answer isincorrect without giving away the 
    answer. For example, if someone were to give the answer 
    {tested_trial_info["possible_incorrect_solution"]} a suitable response from you 
    might be {tested_trial_info["possible_incorrect_feedback"]}. Be careful to not give 
    away the answer in your feedback. Also, note that in your feedback, don't ever 
    refer to these as riddles, but refer to them as problems. 
    """

    while True:
        clear_terminal()
        print("\n")
        print(center_text("** Insight Experiment **"))
        print("\nPlease provide a solution to the following problem:\n\n" + tested_trial_info["insight_question"])
        print("_" * int(shutil.get_terminal_size().columns) + "\n") # Aesthetics
        if prev_answer_incorrect:
            user_response = input(f"{GPT_eval} Try again: ") # Give a hint
        else:
            user_response = input("Enter your solution (or 'quit' to exit): ")

        # Evaluation
        GPT_eval = GPT_evaluate_answer(prompt, user_response)
        if GPT_eval.lower() == "yes":
            list_of_answers.append([trial_number, user_response, "Correct", "NA"])
            print("\nCorrect! You've found an insightful solution.")
            input("Hit enter to continue...")
            break
        else:
            list_of_answers.append([trial_number, user_response, "Incorrect", GPT_eval])
            prev_answer_incorrect = True



# WRITE DATA
write_data()






