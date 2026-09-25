import numpy as np
import random
import copy

TOP_SET_INTENSITIES = {
    1 : (0.88, 0.95),
    2 : (0.86, 0.93),
    3 : (0.82, 0.91),
    4 : (0.79, 0.87),
    5 : (0.76, 0.84)
}

BACKOFF_SET_INTENSITIES = {
    3 : (0.80, 0.86),
    4 : (0.76, 0.82),
    5 : (0.72, 0.80),
    6 : (0.68, 0.78)
}

ABSOLUTE_STRENGTH_CUTOFF = 3
NUM_TOP_SETS = 1
NUM_BACKOFF_SETS = 3

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

def round_five(num):
    return 5 * round(num / 5)


def generate_progressions(num_weeks):
    for rep, percent_range in TOP_SET_INTENSITIES.items():
        percent_step = (percent_range[1] - percent_range[0]) / (num_weeks - 2)
        top_set_progression[rep] = np.arange(percent_range[0], percent_range[1] + 0.01, percent_step)

    for rep, percent_range in BACKOFF_SET_INTENSITIES.items():
        percent_step = (percent_range[1] - percent_range[0]) / (num_weeks - 2)
        backoff_set_progression[rep] = np.arange(percent_range[0], percent_range[1] + 0.01, percent_step)


def generate_program(lift_max, days_a_week=2, num_weeks=4):
    absolute_strength_scheduled = False
    hypertrophy_scheduled = False
    generate_progressions(num_weeks)
    lift_program = {}

    for week in range(num_weeks - 1):
        lift_program[week] = {}
        for day in range(days_a_week):
            lift_program[week][day] = {}
            if not absolute_strength_scheduled:
                reps = random.randint(1, ABSOLUTE_STRENGTH_CUTOFF - 1)
                weight = round_five(lift_max * top_set_progression[reps][week])
                lift_program[week][day][weight] = (NUM_TOP_SETS, reps)

                reps = random.randint(3, 6)
                weight = round_five(lift_max * backoff_set_progression[reps][week])
                lift_program[week][day][weight] = (NUM_BACKOFF_SETS, reps)

                absolute_strength_scheduled = True
            elif not hypertrophy_scheduled:
                reps = random.randint(ABSOLUTE_STRENGTH_CUTOFF + 1, 5)
                weight = round_five(lift_max * top_set_progression[reps][week])
                lift_program[week][day][weight] = (NUM_TOP_SETS, reps)

                reps = random.randint(reps, 6)
                weight = round_five(lift_max * backoff_set_progression[reps][week])
                lift_program[week][day][weight] = (NUM_BACKOFF_SETS, reps)

                hypertrophy_scheduled = True
            else:
                reps = ABSOLUTE_STRENGTH_CUTOFF
                weight = round_five(lift_max * top_set_progression[reps][week])
                lift_program[week][day][weight] = (NUM_TOP_SETS, reps)

                reps = random.randint(reps, 6)
                weight = round_five(lift_max * backoff_set_progression[reps][week])
                lift_program[week][day][weight] = (NUM_BACKOFF_SETS, reps)


        absolute_strength_scheduled = False
        hypertrophy_scheduled = False

    lift_program[num_weeks - 1] = copy.deepcopy(lift_program[0])
    for day in range(days_a_week):
        if not absolute_strength_scheduled:
            lift_program[num_weeks - 1][day] = { lift_max : (1, 1) }
            absolute_strength_scheduled = True

        elif not hypertrophy_scheduled:
            for weight, sets_reps in lift_program[num_weeks - 1][day].items():
                if sets_reps[0] == NUM_BACKOFF_SETS:
                    lift_program[num_weeks - 1][day][weight] = (sets_reps[0] - 1, sets_reps[1])
            hypertrophy_scheduled = True
        
        else: 
            for weight, sets_reps in lift_program[num_weeks - 1][day].items():
                if sets_reps[0] == NUM_BACKOFF_SETS:
                    lift_program[num_weeks - 1][day][weight] = (sets_reps[0] - 1, sets_reps[1])

    return(lift_program)


def display_program(program):
    for week, day_map in program.items():
        print(f"Week {week + 1}:")
        for day, lift_map in day_map.items():
            print(f"    Day {day + 1}:")
            for weight, sets_reps in lift_map.items():
                print(f"        {weight} for {sets_reps[0]}x{sets_reps[1]}")
        print("")


if __name__ == "__main__":
    program = generate_program(255)
    display_program(program)