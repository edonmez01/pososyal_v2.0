import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress
import statistical
import odds

# Linear regression model for the calculation of participation points:
participation_x = np.linspace(0, 90)
participation_y = np.piecewise(participation_x, [participation_x < 60, participation_x >= 60], [2, 4])
participation_pts = np.poly1d(np.polyfit(participation_x, participation_y, 1))


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


def next_value(values, minutes, next_mins):
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

    # Weighted least squares fit
    opt_a, opt_b = curve_fit(f=lambda x, a, b: a * x + b,
                             xdata=x_axis,
                             ydata=[90 * values[i] / minutes[i] for i in range(len(values))],
                             sigma=[1 / m for m in minutes])[0]

    result = (opt_a * (curr_minute + next_mins / 2) + opt_b) * next_mins / 90
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
    df['total_points'] = [total_points + odds.teams[team]['w_prob'] - odds.teams[team]['l_prob']
                          for total_points, team
                          in zip(df['total_points'], df['team'])]

    # -1 point for every own goal
    df['total_points'] -= df['next_ogs']


def gk_points(df):
    # 10 points for every goal scored
    df['next_nonp_goals'] = [next_nonp_goals * odds.teams[team]['xg'] / statistical.AVG_GOALS_PG
                             for next_nonp_goals, team
                             in zip(df['next_nonp_goals'], df['team'])]
    df['total_points'] += (df['next_nonp_goals'] + df['next_p_goals']) * 10

    # 8 points for every assist
    df['next_assists'] = [next_assists * odds.teams[team]['xg'] / statistical.AVG_GOALS_PG
                          for next_assists, team
                          in zip(df['next_assists'], df['team'])]
    df['total_points'] += df['next_assists'] * 8

    # -1 point for every goal conceded
    df['total_points'] = [total_points - odds.teams[team]['xga'] * next_mins / 90
                          for total_points, team, next_mins
                          in zip(df['total_points'], df['team'], df['next_mins'])]

    # 5 points for clean sheet (if played for over 60 minutes)
    df['total_points'] = [total_points + odds.teams[team]['cs_prob'] * 5
                          if next_mins >= 60
                          else total_points
                          for total_points, next_mins, team
                          in zip(df['total_points'], df['next_mins'], df['team'])]

    # 1/3 points for every save
    df['total_points'] += df['next_saves'] / 3


def d_points(df):
    # 8 points for every goal scored
    df['next_nonp_goals'] = [next_nonp_goals * odds.teams[team]['xg'] / statistical.AVG_GOALS_PG
                             for next_nonp_goals, team
                             in zip(df['next_nonp_goals'], df['team'])]
    df['total_points'] += (df['next_nonp_goals'] + df['next_p_goals']) * 8

    # 4 points for every assist
    df['next_assists'] = [next_assists * odds.teams[team]['xg'] / statistical.AVG_GOALS_PG
                          for next_assists, team
                          in zip(df['next_assists'], df['team'])]
    df['total_points'] += df['next_assists'] * 4

    # -1 point for every 2 goals conceded
    df['total_points'] = [total_points - (odds.teams[team]['xga'] * next_mins / 90) / 2
                          for total_points, team, next_mins
                          in zip(df['total_points'], df['team'], df['next_mins'])]

    # 3 points for clean sheet (if played for over 60 minutes)
    df['total_points'] = [total_points + odds.teams[team]['cs_prob'] * 3
                          if next_mins >= 60
                          else total_points
                          for total_points, next_mins, team
                          in zip(df['total_points'], df['next_mins'], df['team'])]


def m_points(df):
    # 6 points for every goal scored
    df['next_nonp_goals'] = [next_nonp_goals * odds.teams[team]['xg'] / statistical.AVG_GOALS_PG
                             for next_nonp_goals, team
                             in zip(df['next_nonp_goals'], df['team'])]
    df['total_points'] += (df['next_nonp_goals'] + df['next_p_goals']) * 6

    # 3 points for every assist
    df['next_assists'] = [next_assists * odds.teams[team]['xg'] / statistical.AVG_GOALS_PG
                          for next_assists, team
                          in zip(df['next_assists'], df['team'])]
    df['total_points'] += df['next_assists'] * 3


def st_points(df):
    # 5 points for every goal scored
    df['next_nonp_goals'] = [next_nonp_goals * odds.teams[team]['xg'] / statistical.AVG_GOALS_PG
                             for next_nonp_goals, team
                             in zip(df['next_nonp_goals'], df['team'])]
    df['total_points'] += (df['next_nonp_goals'] + df['next_p_goals']) * 5

    # 3 points for every assist
    df['next_assists'] = [next_assists * odds.teams[team]['xg'] / statistical.AVG_GOALS_PG
                          for next_assists, team
                          in zip(df['next_assists'], df['team'])]
    df['total_points'] += df['next_assists'] * 3
