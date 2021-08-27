# The values in the following dictionaries are calculated by applying appropriately-degreed polynomial regressions
# over last season's prediction statistics.
cs_prob = {  # Prediction of conceded goals: clean sheet probability
    0: .334935165,
    1: .280833305,
    2: .217453647,
    3: .144796193,
    4: .062860941,
    5: .0
}

score_prob = {  # Prediction of scored goals: realized prediction
    0: .560281400,
    1: 1.172131800,
    2: 1.783982200,
    3: 2.395832600,
    4: 3.007682999,
    5: 3.619533399
}

win_points = {  # Predicted score difference: win point
    # (0 for completely even matchups, 1 for completely 1-sided matchups)
    0: .0,
    1: .045016685,
    2: .197597330,
    3: .350177975,
    4: .502758621,
    5: .655339266
}

# This is last season's average goals scored per team per game.
AVG_GOALS_PG = 1.352380952
