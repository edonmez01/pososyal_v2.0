import data
import mathematical
import pandas as pd

# Setting pandas options for console display
pd.set_option('display.max_columns', 25)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)

# Initializing dataframes
df_columns = ['player_id', 'player_name', 'pos', 'team', 'next_mins', 'next_nonp_goals', 'next_p_goals', 'next_assists',
              'next_yellows', 'next_reds', 'next_ogs', 'score_prediction', 'concede_prediction']

gk_df = pd.DataFrame(columns=df_columns)
d_df = pd.DataFrame(columns=df_columns)
m_df = pd.DataFrame(columns=df_columns)
st_df = pd.DataFrame(columns=df_columns)

for player_id, player_data in data.players_dict.items():
    player_name = player_data[0]
    pos = player_data[1]
    started = [int(i) for i in player_data[2].split(',')]
    mins = [int(i) for i in player_data[3].split(',')]
    starting_lineup_minutes = [mins[i] for i in range(len(mins)) if started[i] == 1]
    nonp_goals = [int(i) for i in player_data[4].split(',')]
    assists = [int(i) for i in player_data[5].split(',')]
    yellows = [int(i) for i in player_data[6].split(',')]
    reds = [int(i) for i in player_data[7].split(',')]
    ogs = [int(i) for i in player_data[8].split(',')]
    p_goals = [int(i) for i in player_data[9].split(',')]
    team = player_data[10]

    if team in data.BYE_TEAMS or (data.teams[team][0] is None and data.teams[team][1] is None):
        # If the team is having a bye week or if its match prediction does not exist yet
        continue

    # This condition checks if there is a faulty row in the players database.
    if not len(started) == len(mins) == len(nonp_goals) == len(assists) == len(yellows) == len(reds) == len(ogs) == len(p_goals):
        print(f'Error: number of matches played, {player_id}, {player_name}')

    nonp_goals_pm = mathematical.per_match_stats(nonp_goals, mins)
    p_goals_pm = mathematical.per_match_stats(p_goals, mins)
    assists_pm = mathematical.per_match_stats(assists, mins)
    yellows_pm = mathematical.per_match_stats(yellows, mins)
    reds_pm = mathematical.per_match_stats(reds, mins)
    ogs_pm = mathematical.per_match_stats(ogs, mins)

    # Predictions of the stats in the player's next match.
    next_mins = min(mathematical.linear_continuation(starting_lineup_minutes), 90.)
    next_nonp_goals = mathematical.linear_continuation(nonp_goals_pm) * next_mins / 90
    next_p_goals = mathematical.linear_continuation(p_goals_pm) * next_mins / 90
    next_assists = mathematical.linear_continuation(assists_pm) * next_mins / 90
    next_yellows = min(mathematical.linear_continuation(yellows_pm) * next_mins / 90, 1.)
    next_reds = min(mathematical.linear_continuation(reds_pm) * next_mins / 90, 1.)
    next_ogs = mathematical.linear_continuation(ogs_pm) * next_mins / 90
    score_prediction, concede_prediction = data.teams[team]

    df_columns_dict = {
        'player_id': player_id,
        'player_name': player_name,
        'pos': pos,
        'team': team,
        'next_mins': next_mins,
        'next_nonp_goals': next_nonp_goals,
        'next_p_goals': next_p_goals,
        'next_assists': next_assists,
        'next_yellows': next_yellows,
        'next_reds': next_reds,
        'next_ogs': next_ogs,
        'score_prediction': score_prediction,
        'concede_prediction': concede_prediction
    }

    # Adding the newly created player to the appropriate dataframe as a new row.
    if pos == 'gk':
        gk_df = gk_df.append(df_columns_dict, ignore_index=True)
    elif pos == 'd':
        d_df = d_df.append(df_columns_dict, ignore_index=True)
    elif pos == 'm':
        m_df = m_df.append(df_columns_dict, ignore_index=True)
    elif pos == 'st':
        st_df = st_df.append(df_columns_dict, ignore_index=True)

# Calculation of points that are universal for all positions.
for df in (gk_df, d_df, m_df, st_df):
    mathematical.universal_points(df)

# Calculation of position-specific points.
mathematical.gk_points(gk_df)
mathematical.d_points(d_df)
mathematical.m_points(m_df)
mathematical.st_points(st_df)

# Concatenating all 4 dataframes for final output.
all_players_df = pd.concat((gk_df, d_df, m_df, st_df))

# Sorting the dataframe by total points.
all_players_df = all_players_df.sort_values(['total_points'], ascending=False).reset_index(drop=True)

# Final output to out.html with background gradients.
with open('out.html', 'w') as out_file:
    out_file.write(all_players_df.style.background_gradient().render())
