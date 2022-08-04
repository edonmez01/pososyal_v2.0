# The values in the following dictionaries are calculated by applying appropriately-degreed polynomial regressions
# over the previous seasons' prediction statistics.

cs_prob = {  # Prediction of conceded goals: clean sheet probability
    0: .317168181,
    1: .282372488,
    2: .19493372,
    3: .135778378,
    4: .031430471,
    5: .0
}

score_prob = {  # Prediction of scored goals: realized prediction
    0: .84002094,
    1: 1.240640033,
    2: 1.704798982,
    3: 2.113409258,
    4: 2.7538415,
    5: 3.619533399,

}

win_points = {  # Predicted score difference: win point
    # (0 for completely even matchups, 1 for completely 1-sided matchups)
    0: .0,
    1: .532258065,
    2: .593406593,
    3: .6875,
    4: .7596301543333333,
    5: .8372511218333332
}

# This is the expected average goals scored per team per game.
AVG_GOALS_PG = 1.455513785
