"""
# H008b - A Within-Subjects of Caffeine Consumption and Its Effect on Insight Problem 
# Created by Lina Z., Katrina B., and Cyrus K.
# Last edited on: 2026-02-16

This code serves as the primary script for H008b, a within-subjects study 
examining the effects of caffeine consumption on insight problem-solving.

The initial rendition of this project (H008a) was a correlative design, but
lacked the power to view any type of correlation between performance and 
survey responses. Hence, this H008b version extended this to a within-subjects 
ABA/BAB design where subjects were asked to either drink or abstain from drinking
caffeine before the session. These three sessions all contained novel insight
questions that were relatively comparable in terms of user difficulty.

CODE STRUCTURE:
The first section defines a dictionary containing all insight problems and 
their solutions, categorized by mathematical, verbal, or spatial characteristics. 
In addition to correct answers, the dictionary includes potential incorrect 
responses and corresponding feedback.

In the latter section, the dictionary is integrated into an automated system 
that facilitates answering questions and providing feedback. This automation 
enables remote data collection and minimizes human bias. A large language model 
was incorporated to evaluate response accuracy. The LLM leveraged the pre-defined 
incorrect solutions and feedback to assess participant responses. 

BEHAVIORAL DATA COLLECTIONS
In this study, we collected the following behavioral data:
    1) Solution response / accuracy
    2) Participants' response time
    3) Proximity of incorrect answer (gauged by GPT; resulted in points)
    4) Hint provided by the LLM
    5) Self-report of insightful / trial-by-error thinking
"""

# Import libraries 
from csv import writer, QUOTE_MINIMAL
from datetime import datetime, timedelta
from time import time
from openai import OpenAI
import os
import sys
import shutil
from random import shuffle
from os import getcwd, mkdir, path as os_path
import string

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
GPT_model  = "gpt-4.1"# "o3-mini"

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
        "insight_answer"                : "'Reading between the lines'. This exact answer must be given. Synonyms can't be used, but capitalization doesn't matter.",
        "possible_incorrect_solution"   : "'r e a d i n g' or 'read the lines in between' or 'letters between the lines', respectively",
        "possible_incorrect_feedback"   : "'There's more to it than that. We are looking for a classic phrase' or 'You're close, but we're looking for a specific phrase' or 'You're close, but we're looking for a known phrase', respectively",
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
    "balanced_equation_problem"  : {
        "insight_question"              : """'You are given this set of numbers and symbols: 3 2 4 5 + =

                                        Using pencil and paper, WRITE and configure a balanced equation 
                                        using ONLY the above symbols and numbers once. Note, the symbols 
                                        you use to TYPE the answer may be different.
                                          """,
        "insight_answer"                : "'3^2 = 5 + 4' or '3^2 = 4 + 5' or '2 x 4 = 5 + 3' or '2 x 4 = 3 + 5' or '4 x 2 = 5 + 3' or '4 x 2 = 3 + 5'",
        "possible_incorrect_solution"   : "'3 + 2 = 54' or '23 = 4 + 5', respectively",
        "possible_incorrect_feedback"   : "'Concatenating the numbers will not result in a balanced equation' or 'You are not restricted to a linear relationship', respectively",
        "problem_type"                  : "MATHEMATICAL"
        },
    "constraint_relaxation_problem"  : {
        "insight_question"              : """'Imagine the following equation is made of matchsticks, where “X” and “+” are two crossed matchsticks and “I” is a single matchstick. If you were to move only a single matchstick to correct this arithmetic equation, what would the new equation be? X + IV = V
                               ROMAN NUMERALS
                            I   = 1   , II   = 2,
                            III = 3   , IV   = 4,
                            V   = 5   , VI   = 6,
                            VII = 7   , VIII = 8
                            IX  = 9   , X    = 10
                            XV  = 15  , XX   = 20
                                          '""",
        "insight_answer"                : "'X - IV = VI' or 'IX - IV = V'",
        "possible_incorrect_solution"   : "'X - IV ≠ V' or, respectively ",
        "possible_incorrect_feedback"   : "'You cannot create an unequal (not-equal) sign' or, respectively",
        "problem_type"                  : "MATHEMATICAL"
        },
    "chunk_decomposition_problem"  : {
        "insight_question"              : """'Imagine the following equation is made of matchsticks, where “X” is two crossed matchsticks and “I” is a single matchstick. If you were to move only a single matchstick to correct this arithmetic equation, what would the new equation be? V = XI - I
                               ROMAN NUMERALS
                            I   = 1   , II   = 2,
                            III = 3   , IV   = 4,
                            V   = 5   , VI   = 6,
                            VII = 7   , VIII = 8
                            IX  = 9   , X    = 10
                            XV  = 15  , XX   = 20

                                          '""",
        "insight_answer"                : "'X = XI - I' or 'V = VI - I'",
        "possible_incorrect_solution"   : "'V - XI = I' or 'I = XI - X' or 'V ≠ X - I', respectively",
        "possible_incorrect_feedback"   : "'This results in a calculation error' or 'In order to make this operation correct, you'd have to change the rotation of two matchsticks, which is not allowed' or 'You cannot create an unequal (not-equal) sign', respectively",
        "problem_type"                  : "MATHEMATICAL"
        },
    "water_lily_problem"  : {
        "insight_question"              : "'A lake has water lilies growing on its surface. The patch of lilies doubles in size every day. At the beginning of the summer, there is one water lily on the lake. It takes 60 days for the lake to become completely covered with water lilies. On which day was the lake half covered?'",
        "insight_answer"                : "'59th day' or '59' or 'day 59'",
        "possible_incorrect_solution"   : "'30th day' or '30' or 'day 30', respectively",
        "possible_incorrect_feedback"   : "'On that day, less than a billionth of the lake is covered' or 'Think about how the water lilies multiply and grow', respectively ",
        "problem_type"                  : "MATHEMATICAL"
        },
    "morris_number_sequence_problem"  : {
        "insight_question"              : "'What is the next number in this sequence? 1, 11, 21, 1211, 111221, '312211', ______'",
        "insight_answer"                : "'13112221'",
        "possible_incorrect_solution"   : "'112' or '122564', respectively",
        "possible_incorrect_feedback"   : "'The next number in this sequence is not 112' or 'Not quite, try thinking of the relationship between numbers differently', respectively",
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
        "possible_incorrect_feedback"   : "'You would spend 6 cents to open and close 3 links, but you're still left with an open loop of chain' or 'Opening two links at once will still cost 2 cents each to open and 1 cent each to close. With this strategy, you've spent 12 cents', respectively",
        "problem_type"                  : "SPATIAL"
        },
    "deck_of_cards_problem"  : {
        "insight_question"              : "'Three cards lie face down on a table, arranged in a row from left to right. We have the following information about them: (a) The Jack is to the left of the Queen, (b) The Diamond is to the left of the Spade, (c) The King is to the right of the Heart, and (d) The Spade is to the right of the King. Which card – by face and suit – occupies each position?'",
        "insight_answer"                : "'Jack of Hearts, King of Diamonds, Queen of Spades'",
        "possible_incorrect_solution"   : "'Jack, Queen, Diamond, Heart, King, Spade' or, respectively",
        "possible_incorrect_feedback"   : "'The faces of a deck of cards are Jack, Queen, and King. The suits of a deck of cards are Clubs, Diamonds, Hearts, and Spades' or, respectively",
        "problem_type"                  : "SPATIAL"
        }, 
    "candles_and_tacks"  : {
        "insight_question"              : "'You are given a set of matches, a box of thumbtacks, and a candle. How would you attach the candle to the vertical wall in a way that allows the candle to be lit without dripping wax onto the table below?'",
        "insight_answer"                : "'Tack an empty thumbtack box to the wall and use it as a candle holder' or 'Empty the thumbtacks from their box, attach the box to the wall as a shelf, then place the candle in the box' or 'Use the thumbtacks to mount the box to the wall to create a shelf that holds the candle and catches the dripping wax', respectively",
        "possible_incorrect_solution"   : "'Tack the candle to the wall' or 'Melt the candle and use the wax to stick it to the wall' or 'Stick matches into the candle and use it to attach it to the wall like hooks' or, respectively",
        "possible_incorrect_feedback"   : "'The tacks are too weak and not long enough to properly secure the candle to the wall' or 'Matches are too weak to be used as hooks' or 'The wax as glue is not stable enough to hold the candle' or 'Think of different ways to use the materials provided' or, respectively",
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
        "possible_incorrect_feedback"   : "'Taking the wolf first leaves the goat and cabbage together' or 'You can take everyone across in seven trips (3.5 round trips)', respectively",
        "problem_type"                  : "SPATIAL"
        }
    }

# Split questions into three banks of possibilities.
dict_of_question_banks = {
    "1" : ["light_switch_problem",
           "baseball_game_problem",
           "sock_problem",
           "morris_number_sequence_problem",
           "candles_and_tacks",
           "river_crossing_problem"],
    "2" : ["triplet_problem",
           "christmas_NY_problem",
           "balanced_equation_problem",
           "constraint_relaxation_problem",
           "chain_problem",
           "deck_of_cards_problem"],
    "3" : ["reading_problem",
           "unlisted_phone_numbers_problem",
           "chunk_decomposition_problem",
           "water_lily_problem",
           "two_string_problem",
           "alphabet_problem"
           ]
}

def GPT_evaluate_answer(prompt, user_solution):
    if user_solution == "quit":
        clear_terminal()
        print("\nThank you for participating!")
        write_data_file(False)
        sys.exit()
    elif user_solution.lower() == "pass":
        return("pass")
    else:
        print(center_text("Checking solution..."))

        combined_prompt = f"{prompt}. Here is the solution to evaluate: '{user_solution}'."
        completion = client.chat.completions.create(
            model= GPT_model, # Model; can be changed to....
            messages= [
                {"role": "user",
                    "content" : [{"type": "text","text": combined_prompt}]
                    }
                ]

            # works for "gpt-4o-mini"
            #[
            #    {"role": "system",
            #     "content": prompt}, # First is the intial prompt w/ correct answers
            #    {"role": "user",
            #     "content": user_solution} # Next is the subject solution
            #    ]
            )
        model_evaluation = completion.choices[0].message.content # grab just text output
        model_evaluation = model_evaluation.strip() 
        return(model_evaluation)

def write_data_row(resp, correct_or_incorrect, feedback, grade, TaE_s_resp, Aha_s_resp):
    # Add current response to data file
    list_of_answers.append(
    [trial_number,                  # Trial number (fixed within a question)
    question_shorthand,             # Question name shorthand
    resp,                           # Participant response
    correct_or_incorrect,           # "Correct" or "Incorrect" string
    grade,                          # Grade evaluation of incorrect answer (1-5)
    feedback,                       # GPT feedback
    trial_problem_type,             # Probelem type (e.g., "SPATIAL")
    passed_trials,                  # Number of questions "passed" by participant
    correct_trials,                 # Incrementing counter of correct answers
    incorrect_answers,              # Incrementing counter of incorrect answers
    datetime.now() - start_time,    # Session timer
    datetime.now() - trial_time,    # Trial timer
    round(time() - prev_IRI_time,3),# Inter-response-interval timer
    # New data points
    subject_ID,                     # Unique subject identifier  
    ABA_condition,                  # ABA Condition (A or B)
    question_bank_num,              # Question bank (1-3)
    earned_points,                  # Cumulative earned points in this session
    TaE_s_resp,                     # Response to trial-and-error survey
    Aha_s_resp                      # Response to insight ('aha') survey
    ])


def write_data_file(cont):
    # WRITE DATA
    # Make folder 
    data_folder_directory = getcwd() + "/data"
    if not os_path.isdir(data_folder_directory):
        mkdir(data_folder_directory)
    # Ensure timestamp var. is Windows-friendly
    myFile_loc = f"data/H008b_output_data_{timestamp}.csv"
    # This loop writes the data in the matrix to the .csv              
    edit_myFile = open(myFile_loc, 'w', newline='')
    with edit_myFile as myFile:
        w = writer(myFile, quoting=QUOTE_MINIMAL)
        w.writerows(list_of_answers) # Write all event/trial data 
    if not cont:
        print("SESSION COMPLETE")
        print(f"\n- Data file written to {myFile_loc}")
        input()

def give_survey_question(q_num, pts):
    while True:
        clear_terminal()
        print(f" Question {q_num}/6")
        print(center_text("╭──────────────────────────────────────────────╮"))
        print(center_text("│            Problem-Solving Experiment        │"))
        print(center_text("╰──────────────────────────────────────────────╯"))
        print(center_text(f"Earned points: {pts}\n\n"))
        print("\n\n\nPROBLEM-SOLVING SURVEY")
        
        trial_and_error_survey_resp = input("On a scale of 1-5, how much did you rely on trial-and-error thinking to reach your answer? (1 = very little, 5 = a great deal): ")
        try:
            trial_and_error_survey_resp = int(trial_and_error_survey_resp)
            if not 1 <= trial_and_error_survey_resp <= 5:
                raise ValueError
        except ValueError:
            input(f"Error: response must be an integer between 1 and 5. Hit enter and try again")
            continue
            
        insight_survey_resp = input("On a scale of 1-5, to what extent did you experience an 'aha' moment when solving this question? (1 = very little, 5 = a great deal): ")
        try:
            insight_survey_resp = int(insight_survey_resp)
            if not 1 <= insight_survey_resp <= 5:
                raise ValueError
        except ValueError:
            input(f"Error: response must be an integer between 1 and 5. Hit enter and try again")
            continue
            
        break
    
    # If everything is kosher, then end the survey and write data
    write_data_row(user_response, "Correct", "NA", "NA", trial_and_error_survey_resp, insight_survey_resp)
    write_data_file(True) # Write data if correct


###########################################################################
# Setup screen
clear_terminal()
print(center_text("EXPERIMENTER SETUP"))
subject_ID = input("\nInput subject ID (then hit 'enter'): ")
ABA_condition = input("Input 'A' or 'B' condition (then hit 'enter'): ").upper()
question_bank_num = input("Input question bank number 1-3 (then hit 'enter'): ")
clear_terminal()
print(center_text("EXPERIMENTER SETUP"))
print(f"\nSubject ID : {subject_ID}\nABA Condition: {ABA_condition}\nQuestion Bank: {question_bank_num}\n")
input("Hit 'enter' to start experimental session.")

# Setup questions for this subject
try:
    questions = dict_of_question_banks[question_bank_num]
except KeyError:
    input("ERROR: Question bank number should be an integer 1, 2, or 3. Restart and try again.")

# Setup data variables for session (including timer)
list_of_answers = [["TrialNumber", "Question", "Solution", "Accuracy",
                    "Grade", "GPT_Hint", "ProblemType", "PassedQuestions",
                    "CorrectTrials", "IncorrectAnswers", "SessionTimer",
                    "TrialTimer", "IRITimer",
                    # New variables
                    "Subject_ID", "ABA_Condition", "QuestionBankNum",
                    "CumulativeEarnedPoints",
                    "TrialAndErrorSurveyResp", "AhaSurveyResp"
                    ]]
trial_number        = 0
passed_trials       = 0
correct_trials      = 0
incorrect_answers   = 0
# Point system
earned_points       = 0 # cumulative earned points
correct_reward      = 250
skip_cost           = 20
GPT_score           = "NA"
added_points        = 0 # Points per a given variable response
incorrect_point_dict = { # Dictionary for point allocation
    "1" : 0,
    "2" : 10,
    "3" : 20,
    "4" : 30
    }

# Setup timing variables
start_time    = datetime.now()
trial_time    = datetime.now()
prev_IRI_time = time()
timestamp = start_time.strftime("%Y-%m-%d_%H-%M-%S")  # Replace `:` with `-`; for data file
session_duration = start_time + timedelta(minutes = 30) # Max session time is 30 min

# Quasi-randomly shuffle questions so that there are never more than 
# two repetitions of problem type in a row
good_order = False
while not good_order:
    shuffle(questions)  # Randomize the trial order
    approved = True     # Innocent until proven guilty
    c = 0  # Counter
    while c < len(questions) and approved:
        if c >= 2:
            # Ensure no more than 3 consecutive trials of the same type
            a  = dict_of_question_info[questions[c]]["problem_type"]
            a1 = dict_of_question_info[questions[c-1]]["problem_type"]
            a2 = dict_of_question_info[questions[c-2]]["problem_type"]
            if a == a1 == a2:
                approved = False
                break
        c += 1
    if approved:
        good_order = True

# Question order dict
question_order_dict = {
    questions[0] : "1",
    questions[1] : "2",
    questions[2] : "3",
    questions[3] : "4",
    questions[4] : "5",
    questions[5] : "6"
}

##############################################################################

# Main loop
try:
    for question in questions:
        # Check if timer has ellapsed
        if datetime.now() >= (session_duration):
            print("\nTime max reached")
            write_data_row("TimerElapsed", "NA", "NA", "NA", "NA", "NA")
            break
        else:
            # For each question, we set up relevant data
            tested_trial_info = dict_of_question_info[question] # Reset the question for this trial
            trial_problem_type = tested_trial_info["problem_type"] # Tested trial type
            trial_number += 1 # Increment trial number by 1
            trial_time    = datetime.now()
            prev_IRI_time = time()
            question_shorthand = question

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
            riddle: {tested_trial_info["insight_question"]}. You know that the correct 
            answer is something along the lines of: {tested_trial_info["insight_answer"]}. 
            If you are given a solution that is close enough to this one, respond with 
            'yes' and only yes.  If some other non-insightful solution, respond with a 
            sentence of feedback on why that answer is incorrect without giving away the 
            answer. For example, if someone were to give the answer 
            {tested_trial_info["possible_incorrect_solution"]} a suitable response from you 
            might be {tested_trial_info["possible_incorrect_feedback"]}. It is of paramount 
            importance that you do not give away the answer in your hint. Make sure to
            double check that your feedback does not give away the answer. Also, note
            that in your feedback, don't ever refer to these as riddles, but refer to them
            as problems.
            In addition to the verbal feedback for incorrect answers, create a numeric grade to 
            evaluate the degree of correctness of the participants answer. The number should
            on a scale of 1-4, with 1 (nonsense), 2 (sensical but far from a correct solution),
            3 (may contains some key words but far from the solution), 4 (contains some logic
            or keywords from the correct solution, but not quite enough to be correct.).
            End your feedback response for incorrect answers with a single number evaluating their
            correctness with no additional punctuation.
            """

            while True:
                # Write data to start every response
                write_data_file(True)
                clear_terminal()
                print(f" Question {question_order_dict[question]}/6")
                print(center_text("╭──────────────────────────────────────────────╮"))
                print(center_text("│            Problem-Solving Experiment        │"))
                print(center_text("╰──────────────────────────────────────────────╯"))
                print(center_text(f"Earned points: {earned_points}\n\n"))
                print("\nPlease provide a solution to the following problem:\n\n" + tested_trial_info["insight_question"])
                print("_" * int(shutil.get_terminal_size().columns) + "\n") # Aesthetics
                if prev_answer_incorrect:
                    user_response = input(f"{GPT_eval}.\nYou've earned {incorrect_point_dict[GPT_score]} points for your guess. Try again (or type 'pass' to skip for -{skip_cost} points): ") # Give a hint
                else:
                    user_response = input(f"Enter your solution (or 'pass' to skip for -{skip_cost} points): ")

                ## Evaluation
                GPT_eval = GPT_evaluate_answer(prompt, user_response)
                # If correct
                if GPT_eval.lower() == "yes":
                    correct_trials += 1
                    earned_points += correct_reward
                    # Write a row of data
                    print(f"\nCorrect! You've found a solution and earned +{correct_reward} points.")
                    input("Hit enter to continue...")
                    # Write in survey
                    give_survey_question(question_order_dict[question], earned_points) # Complete post-correct answer survey
                    break
                # If 'pass' user response
                elif GPT_eval.lower() == "pass":
                    print(f"\nPassing this question means you can come back later, but will cost {skip_cost} points.")
                    possible_pass = input("Are you sure you want to pass this question? ('yes' or 'no'): ")
                    if possible_pass.lower() == "yes":
                        earned_points -= skip_cost
                        passed_trials += 1
                        write_data_row(user_response, "Pass", "NA", "NA", "NA", "NA")
                        questions.append(question) # Add "question" to the end of the list
                        print("\nQuestion passed.")
                        input("Hit enter to continue...")
                        break
                    else:
                        prev_answer_incorrect = False
                # If incorrect
                else:
                    incorrect_answers += 1
                    # Update scoring
                    GPT_score = GPT_eval[-1] # Extract score from evaluation
                    earned_points += int(incorrect_point_dict[GPT_score])
                    # Extract eval/write data
                    GPT_eval = GPT_eval[:-2].rstrip(string.punctuation + string.whitespace) # Clean string response
                    write_data_row(user_response, "Incorrect", GPT_eval, GPT_score, "NA", "NA")
                    prev_answer_incorrect = True
                    prev_IRI_time = time()

    # WRITE DATA at the end, too
    write_data_file(False)

except Exception as e:
    clear_terminal()
    print("\nERROR DURING SESSION -- please notify experimenter")
    print("Error type:", type(e).__name__)
    print("Message:", e)
    input("\nPress Enter to end session...")


