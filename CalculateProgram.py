import numpy as np
import random
import copy
from enum import Enum
import sys
import math

# Enum for representing what kind of workout a specific day of the week is
class WorkoutType(Enum):
    REST = 0
    LOWER = 1
    UPPER = 2
    JUMP = 3

# Maps the number of reps to an intensity range (the range uses percentage of One Rep Max - or %ORM) for the top set
TOP_SET_INTENSITIES = {
    1 : (0.88, 0.95),
    2 : (0.86, 0.93),
    3 : (0.82, 0.91),
    4 : (0.79, 0.87),
    5 : (0.76, 0.84)
}
# Maps the number of reps to an intensity range for the backoff sets
BACKOFF_SET_INTENSITIES = {
    3 : (0.80, 0.86),
    4 : (0.76, 0.82),
    5 : (0.72, 0.80),
    6 : (0.68, 0.78)
}

# Array that essentially maps an index to the day of the week 
DAYS_OF_THE_WEEK = [ "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" ]

# Below the absolute strength cutoff represents a rep range specifically for absolute strength and above the cutoff represents a rep range for hypertrophy
ABSOLUTE_STRENGTH_CUTOFF = 3
# Simply the number of top sets and backoff sets that should be scheduled
NUM_TOP_SETS = 1
NUM_BACKOFF_SETS = 3

# Round a number to the nearest 5
def round_five(num):
    return 5 * round(num / 5)

# Checks if a given variable is a pair
def is_pair(var):
  return isinstance(var, (tuple, list)) and len(var) == 2

# This function uses the number of weeks specified by the user to generate a %ORM progression for each possible number of reps
def generate_progressions(num_weeks):
    # Empty maps that will be filled with a %ORM progression
    top_set_progression = {
        1 : [],
        2 : [],
        3 : [],
        4 : [],
        5 : []
    }
    backoff_set_progression = {
        3 : [],
        4 : [],
        5 : [],
        6 : []
    }

    # Loop through the top set intensities and generate a %ORM array that has num_weeks-1 percentages
    for rep, percent_range in TOP_SET_INTENSITIES.items():
        percent_step = (percent_range[1] - percent_range[0]) / (num_weeks - 2)
        top_set_progression[rep] = np.arange(percent_range[0], percent_range[1] + 0.01, percent_step)

    # Loop through the backoff set intensities and generate a %ORM array that has num_weeks - 1 percentages
    for rep, percent_range in BACKOFF_SET_INTENSITIES.items():
        percent_step = (percent_range[1] - percent_range[0]) / (num_weeks - 2)
        backoff_set_progression[rep] = np.arange(percent_range[0], percent_range[1] + 0.01, percent_step)

    return top_set_progression, backoff_set_progression

# Generate a top set backoff program based on a user's max for a certain lift, how many days a week they want to work that lift, 
# and the number of weeks they want the program to take
def generate_program(lift_max, days_a_week=2, num_weeks=4):
    # Set up some variables
    absolute_strength_scheduled = False
    hypertrophy_scheduled = False
    lift_program = {}
    top_set_progression, backoff_set_progression = generate_progressions(num_weeks)

    # Loop for num_weeks-1 to generate a plan for each week
    for week in range(num_weeks - 1):
        lift_program[week] = {}
        # Loop for days_a_week to generate a plan for the number of days a user wants to work their lift a week
        for day in range(days_a_week):
            lift_program[week][day] = {}
            # Schedule absolute strength first because it is the most important rep range for increasing your max
            if not absolute_strength_scheduled:
                # Generate an absolute strength rep range for the top set and have the backoff set be any greater rep range
                reps = random.randint(1, ABSOLUTE_STRENGTH_CUTOFF - 1)
                weight = round_five(lift_max * top_set_progression[reps][week])
                lift_program[week][day][weight] = (NUM_TOP_SETS, reps)

                reps = random.randint(3, 6)
                weight = round_five(lift_max * backoff_set_progression[reps][week])
                lift_program[week][day][weight] = (NUM_BACKOFF_SETS, reps)

                absolute_strength_scheduled = True
            # Schedule hypertrophy second because it should be done in addition to absolute strength work
            elif not hypertrophy_scheduled:
                # Make the absolute strength work the last day of the week
                lift_program[week][day] = lift_program[week][day - 1]
                lift_program[week][day - 1] = {}

                # Generate a hypertrophy rep range for the top set and have the backoff set be any greater rep range
                reps = random.randint(ABSOLUTE_STRENGTH_CUTOFF + 1, 5)
                weight = round_five(lift_max * top_set_progression[reps][week])
                lift_program[week][day - 1][weight] = (NUM_TOP_SETS, reps)

                reps = random.randint(reps, 6)
                weight = round_five(lift_max * backoff_set_progression[reps][week])
                lift_program[week][day - 1][weight] = (NUM_BACKOFF_SETS, reps)

                hypertrophy_scheduled = True
            # Schedule reps of 3 last as a middle ground between absolute strength and hypertrophy
            else:
                # Make the absolute strength work the last day of the week
                lift_program[week][day] = lift_program[week][day - 1]
                lift_program[week][day - 1] = {}

                # Generate a top set of 3 reps and have the backoff set be any greater rep range
                reps = ABSOLUTE_STRENGTH_CUTOFF
                weight = round_five(lift_max * top_set_progression[reps][week])
                lift_program[week][day - 1][weight] = (NUM_TOP_SETS, reps)

                reps = random.randint(reps, 6)
                weight = round_five(lift_max * backoff_set_progression[reps][week])
                lift_program[week][day - 1][weight] = (NUM_BACKOFF_SETS, reps)

        # Reset flags for each week
        absolute_strength_scheduled = False
        hypertrophy_scheduled = False

    # Copy the first week of the program into the last week and slightly alter it for a deload
    lift_program[num_weeks - 1] = copy.deepcopy(lift_program[0])
    for day in range(days_a_week):
        # If it's the last day of the last week, schedule a one rep max
        if day == days_a_week - 1:
            lift_program[num_weeks - 1][day] = { lift_max : (1, 1) }
        # On any other day in the last week just reduce the number of backoff sets by 1
        else: 
            for weight, sets_reps in lift_program[num_weeks - 1][day].items():
                if sets_reps[0] == NUM_BACKOFF_SETS:
                    lift_program[num_weeks - 1][day][weight] = (sets_reps[0] - 1, sets_reps[1])

    return(lift_program)

# Function to print out the program for a single lift
def display_program(program):
    for week, day_map in program.items():
        print(f"Week {week + 1}:")
        for day, lift_map in day_map.items():
            print(f"    Day {day + 1}:")
            for weight, sets_reps in lift_map.items():
                print(f"        {weight} for {sets_reps[0]}x{sets_reps[1]}")
        print("")

# Function to generate a program for increasing vertical jump
def generate_jump_program(squat_max, bench_max, num_weeks, jump_days_on):
    # Ensure that the jump days array is valid
    jump_days_on.sort()
    if len(jump_days_on) != 2:
        sys.exit("You should be hitting two jump days with this specific program.")
    if jump_days_on[0] == jump_days_on[1] or jump_days_on[0] + 1 == jump_days_on[1] or (jump_days_on[0] == 0 and jump_days_on[1] == 6):
        sys.exit("Your jump days should not be right next to each other (or on the same day).")

    # Generate general squat and bench programs using the top set backoff method and current user maxes
    squat_program = generate_program(squat_max, num_weeks=num_weeks)
    bench_program = generate_program(bench_max, num_weeks=num_weeks)
    full_program = { }

    # Keep an array of size 7 to determine what kind of workout should be on each day of the week
    program_days = [WorkoutType.REST] * 7
    program_days[jump_days_on[0]] = WorkoutType.JUMP
    program_days[jump_days_on[1]] = WorkoutType.JUMP

    # Calculate gaps between jump days (gap between Monday and Wednesday would be 1) to determine where lower body days should be placed
    gaps_between_jump_days = [jump_days_on[0]-0, jump_days_on[1]-jump_days_on[0]-1, 6-jump_days_on[1]]
    jump_days_on = [-1] + jump_days_on

    # Loop through the gaps in the week and handle them on a case by case basis
    placed_in_one_day_gap = False
    placed_in_two_day_gap = False
    num_lower_days = 2
    for i in range(len(gaps_between_jump_days)):
        # If there are no more lower days left to schedule, break out of the loop
        if num_lower_days == 0:
            break
        gap = gaps_between_jump_days[i]
        # For a 4 day gap, schedule leg workouts on days 1 and 3 within the gap
        if gap == 4:
            program_days[jump_days_on[i] + 1] = WorkoutType.LOWER
            num_lower_days -= 1
            if num_lower_days == 0:
                break
            program_days[jump_days_on[i] + 3] = WorkoutType.LOWER
        # Handles the edge case where the gaps are [3 1 1]
        elif gap == 3 and gaps_between_jump_days.count(1) == 2 and gaps_between_jump_days[0] == 3:
            program_days[jump_days_on[i] + 1] = WorkoutType.LOWER
            num_lower_days -= 1
            if num_lower_days == 0:
                break
            program_days[jump_days_on[i] + 3] = WorkoutType.LOWER
        # Place leg workout in the middle of a 3 day gap by default
        elif gap == 3:
            program_days[jump_days_on[i] + 2] = WorkoutType.LOWER
        # Handle a 2 day gap so you don't end up with 2 back to back leg/jump days in a week
        elif gap == 2:
            if placed_in_two_day_gap and program_days[0] != WorkoutType.LOWER:
                program_days[jump_days_on[i] + 2] = WorkoutType.LOWER
            else: 
                program_days[jump_days_on[i] + 1] = WorkoutType.LOWER
            placed_in_two_day_gap = True
        # Only place a leg workout into a one day gap if necessary for an edge case (gaps [1 1 3])
        elif gap == 1 and gaps_between_jump_days.count(1) == 2 and not placed_in_one_day_gap:
            program_days[jump_days_on[i] + 1] = WorkoutType.LOWER
            placed_in_one_day_gap = True
        # Offset the automatic decrement of num_lower_days if you don't actually schedule a lower day
        else:
            num_lower_days += 1
        num_lower_days -= 1

    # Simply schedule 2 upper days where there is still room in the week
    num_upper_days = 2
    for i in range(len(program_days)):
        if num_upper_days == 0:
            break
        if program_days[i] == WorkoutType.REST:
            program_days[i] = WorkoutType.UPPER
            num_upper_days -= 1
    
    lower_day = 0
    upper_day = 0
    set_divider = 1
    for week in range(num_weeks):
        if week == num_weeks - 1:
            set_divider = 2
        full_program[week] = {}
        for day in range(len(program_days)):
            workout = program_days[day]
            full_program[week][day] = {}

            match workout:
                case WorkoutType.REST:
                    full_program[week][day]["Rest"] = { 0 : (0, 0) }
                case WorkoutType.JUMP:
                    full_program[week][day]["Jump Session or Volleyball"] = { 0 : (1, (60, 120))}
                case WorkoutType.LOWER:
                    if lower_day == 0:
                        full_program[week][day]["1. Penultimate Jump"] = { 0 : (math.floor(3 / set_divider), 3) }
                        full_program[week][day]["2. Weighted Box Jumps"] = { 40 : (math.floor(3 / set_divider), 3) }
                        full_program[week][day]["3. Squat"] = squat_program[week][lower_day]
                        full_program[week][day]["4. Calf Raises"] = { 265 : (math.floor(3 / set_divider), (8, 10)) }
                        full_program[week][day]["5. Romanian Dead Lift"] = { 195 : (math.floor(3 / set_divider), (5, 7)) }
                        lower_day += 1
                    else:
                        if week == num_weeks - 1:
                            full_program[week][day]["1. Squat"] = squat_program[week][lower_day]
                        else:
                            full_program[week][day]["1. Pogo Jumps"] = { 0 : (math.floor(3 / set_divider), 15) }
                            full_program[week][day]["2. Depth Jumps"] = { 0 : (math.floor(3 / set_divider), 3) }
                            full_program[week][day]["3. Power Cleans"] = { 165 : (math.floor(3 / set_divider), 3) }
                            full_program[week][day]["4. Squat"] = squat_program[week][lower_day]
                            full_program[week][day]["5. Calf Machine"] = { 35 : (math.floor(3 / set_divider), (8, 10)) }
                            full_program[week][day]["6. Hamstring Curls"] = { 100 : (math.floor(3 / set_divider), (6, 8)) }
                            lower_day = 0
                case WorkoutType.UPPER:
                    full_program[week][day]["1. Bench Press"] = bench_program[week][upper_day]
                    if upper_day == 0:
                        full_program[week][day]["2. False Grip Pull-Ups"] = { 0 : (math.floor(4 / set_divider), 5) }
                        full_program[week][day]["2.5. One Legged Wall Sits"] = { 25 : (math.floor(3 / set_divider), 30) }
                        full_program[week][day]["3. Incline Dumbell Press"] = { 100 : (math.floor(3 / set_divider), (8, 10)) }
                        full_program[week][day]["4. Seated Cable Rows"] = { 120 : (math.floor(3 / set_divider), (8, 10))}
                        full_program[week][day]["5. Tricep Push-Downs"] = { 0 : (math.floor(3 / set_divider), (8, 10)) }
                        upper_day += 1
                    else:
                        if week != num_weeks - 1:
                            full_program[week][day]["2. Weighted Pull-Ups"] = { 10 : (math.floor(4 / set_divider), (6, 8)) }
                            full_program[week][day]["2.5. One Legged Wall Sits"] = { 25 : (math.floor(3 / set_divider), 30) }
                            full_program[week][day]["3. Shoulder Press"] = { 95 : (math.floor(3 / set_divider), (6, 8)) }
                            full_program[week][day]["4. Bicep Curls"] = { 60 : (math.floor(3 / set_divider), (6, 8))}
                            full_program[week][day]["5. Dips"] = { 0 : (math.floor(3 / set_divider), (8, 10)) }
                            upper_day = 0
                case _:
                    sys.exit("Was not able to parse workout type from program_days.")

    return full_program

# Function to save a program to a text file
def save_program(program, output_file_path="output_program.txt"):
    with open(output_file_path, "w") as output:
        for week, day_map in program.items():
            output.write(f"Week {week + 1}:\n")
            for day, lift_map in day_map.items():
                output.write(f"\t{DAYS_OF_THE_WEEK[day]}:\n")
                for exercise, weight_map in lift_map.items():
                    output.write(f"\t\t{exercise}: ")
                    for weight, sets_reps in weight_map.items():
                        if is_pair(sets_reps[1]):
                            output.write(f"{weight} lbs for {sets_reps[0]}x{sets_reps[1][0]}-{sets_reps[1][1]}; ")
                        else:
                            output.write(f"{weight} lbs for {sets_reps[0]}x{sets_reps[1]}; ")
                    output.write("\n")
            output.write("\n")

if __name__ == "__main__":
    program = generate_jump_program(255, 255, 4, [2, 5])
    save_program(program)