import numpy as np
from scipy.stats import linregress
import statistical

# Linear regression model for the calculation of participation points:
x = np.linspace(0, 90)
y = np.piecewise(x, [x < 60, x >= 60], [2, 4])
participation_pts = np.poly1d(np.polyfit(x, y, 1))


def linear_continuation(values):
    """A basic linear regression model to predict the next discrete value in a list of values."""
    if not values:
        return .0
    if len(values) == 1:
        return float(values[0])

    x_axis = list(range(1, len(values) + 1))
    regression = linregress(x_axis, values)
    result = regression.intercept + (len(values) + 1) * regression.slope
    if result < 0:
        return .0
    else:
        return result


def next_value(values, minutes):
    """A function to predict the next value in a list of values."""
    if not values:
        return .0
    if len(values) == 1:
        return float(values[0])

    curr_minute = 0
    x_axis = []
    for m in minutes:
        x_axis.append(curr_minute + m / 2)
        curr_minute += m

    regression = linregress(x_axis, values)
    result = regression.intercept + (curr_minute + 45) * regression.slope

    return max(.0, result)


def universal_points(df):
    df['total_points'] = .0

    # Participation pts (2 pts for every player participating, 4 pts for every player playing for over 60 minutes)
    df['total_points'] += participation_pts(df['next_mins'])

    # -1 point for every yellow card
    df['total_points'] -= df['next_yellows']

    # -4 points for every red card
    df['total_points'] -= df['next_reds'] * 4

    # 1 point for a win, -1 point for a loss
    df['total_points'] = [total_points + statistical.win_points[score_prediction - concede_prediction]
                          if score_prediction >= concede_prediction
                          else total_points - statistical.win_points[concede_prediction - score_prediction]
                          for total_points, score_prediction, concede_prediction
                          in zip(df['total_points'], df['score_prediction'], df['concede_prediction'])]

    # -1 point for every own goal
    df['total_points'] -= df['next_ogs']


def gk_points(df):
    # 10 points for every goal scored
    df['next_nonp_goals'] = [next_nonp_goals * statistical.score_prob[score_prediction] / statistical.AVG_GOALS_PG
                             for next_nonp_goals, score_prediction
                             in zip(df['next_nonp_goals'], df['score_prediction'])]
    df['total_points'] += (df['next_nonp_goals'] + df['next_p_goals']) * 10

    # 8 points for every assist
    df['next_assists'] = [next_assists * statistical.score_prob[score_prediction] / statistical.AVG_GOALS_PG
                          for next_assists, score_prediction
                          in zip(df['next_assists'], df['score_prediction'])]
    df['total_points'] += df['next_assists'] * 8

    # -1 point for every goal conceded
    df['total_points'] = [total_points - statistical.score_prob[concede_prediction] * next_mins / 90
                          for total_points, concede_prediction, next_mins
                          in zip(df['total_points'], df['concede_prediction'], df['next_mins'])]

    # 5 points for clean sheet (if played for over 60 minutes)
    df['total_points'] = [total_points + statistical.cs_prob[concede_prediction] * 5
                          if next_mins >= 60
                          else total_points
                          for total_points, next_mins, concede_prediction
                          in zip(df['total_points'], df['next_mins'], df['concede_prediction'])]

    # 1/3 points for every save
    df['total_points'] += df['next_saves'] / 3


def d_points(df):
    # 8 points for every goal scored
    df['next_nonp_goals'] = [next_nonp_goals * statistical.score_prob[score_prediction] / statistical.AVG_GOALS_PG
                             for next_nonp_goals, score_prediction
                             in zip(df['next_nonp_goals'], df['score_prediction'])]
    df['total_points'] += (df['next_nonp_goals'] + df['next_p_goals']) * 8

    # 4 points for every assist
    df['next_assists'] = [next_assists * statistical.score_prob[score_prediction] / statistical.AVG_GOALS_PG
                          for next_assists, score_prediction
                          in zip(df['next_assists'], df['score_prediction'])]
    df['total_points'] += df['next_assists'] * 4

    # -1 point for every 2 goals conceded
    df['total_points'] = [total_points - (statistical.score_prob[concede_prediction] * next_mins / 90) / 2
                          for total_points, concede_prediction, next_mins
                          in zip(df['total_points'], df['concede_prediction'], df['next_mins'])]

    # 3 points for clean sheet (if played for over 60 minutes)
    df['total_points'] = [total_points + statistical.cs_prob[concede_prediction] * 3
                          if next_mins >= 60
                          else total_points
                          for total_points, next_mins, concede_prediction
                          in zip(df['total_points'], df['next_mins'], df['concede_prediction'])]


def m_points(df):
    # 6 points for every goal scored
    df['next_nonp_goals'] = [next_nonp_goals * statistical.score_prob[score_prediction] / statistical.AVG_GOALS_PG
                             for next_nonp_goals, score_prediction
                             in zip(df['next_nonp_goals'], df['score_prediction'])]
    df['total_points'] += (df['next_nonp_goals'] + df['next_p_goals']) * 6

    # 3 points for every assist
    df['next_assists'] = [next_assists * statistical.score_prob[score_prediction] / statistical.AVG_GOALS_PG
                          for next_assists, score_prediction
                          in zip(df['next_assists'], df['score_prediction'])]
    df['total_points'] += df['next_assists'] * 3


def st_points(df):
    # 5 points for every goal scored
    df['next_nonp_goals'] = [next_nonp_goals * statistical.score_prob[score_prediction] / statistical.AVG_GOALS_PG
                             for next_nonp_goals, score_prediction
                             in zip(df['next_nonp_goals'], df['score_prediction'])]
    df['total_points'] += (df['next_nonp_goals'] + df['next_p_goals']) * 5

    # 3 points for every assist
    df['next_assists'] = [next_assists * statistical.score_prob[score_prediction] / statistical.AVG_GOALS_PG
                          for next_assists, score_prediction
                          in zip(df['next_assists'], df['score_prediction'])]
    df['total_points'] += df['next_assists'] * 3
