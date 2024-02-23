import beautify
import budget
import data
import mathematical
import pandas as pd
import odds

ONLY_GUARANTEED = False

# Setting pandas options for console display
pd.set_option('display.max_columns', 25)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)

# Initializing dataframes
df_columns = ['player_id', 'player_name', 'pos', 'team', 'price', 'next_mins', 'next_nonp_goals', 'next_p_goals',
              'next_assists',
              'next_yellows', 'next_reds', 'next_ogs', 'score_prediction', 'concede_prediction']

gk_df = pd.DataFrame(columns=df_columns)
d_df = pd.DataFrame(columns=df_columns)
m_df = pd.DataFrame(columns=df_columns)
st_df = pd.DataFrame(columns=df_columns)

total_num_of_players = 0
total_matches_played = 0
total_minutes = 0
total_uncertainty = 0

for player_id, player_data in data.players_dict.items():
    if ONLY_GUARANTEED:
        if player_id not in data.GUARANTEED:
            continue

    if player_data[11] < .1 or (player_id not in data.GUARANTEED and player_id in data.MISSING_PLAYERS):
        continue

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
    price = player_data[11]
    saves = [int(i) for i in player_data[12].split(',')]
    ninety_min_saves = [saves[i] for i in range(len(saves)) if mins[i] == 90]

    if player_id not in data.GUARANTEED and started[-1] == 0 and pos != 'gk':
        continue

    if team not in odds.teams:
        # If the team is having a bye week
        continue

    # This condition checks if there is a faulty row in the players database.
    if not len(started) == len(mins) == len(nonp_goals) == len(assists) == len(yellows) == len(reds) == len(ogs) == len(
            p_goals):
        print(f'Error: number of matches played, {player_id}, {player_name}')
        continue

    matches_played = len(started)
    total_num_of_players += 1
    total_matches_played += len(started)
    total_mins_player = sum(mins)
    total_minutes += total_mins_player
    uncertainty = 90 / total_mins_player
    total_uncertainty += uncertainty

    # Predictions of the stats in the player's next match.
    next_mins = min(mathematical.linear_continuation(starting_lineup_minutes), 90.)
    next_nonp_goals = mathematical.next_value(nonp_goals, mins, next_mins)
    if sum(1 for n in nonp_goals if n == 0) == len(nonp_goals) - 1:
        next_nonp_goals = (sum(nonp_goals) / len(nonp_goals))
    next_p_goals = mathematical.next_value(p_goals, mins, next_mins)
    if sum(1 for n in p_goals if n == 0) == len(p_goals) - 1:
        next_p_goals = (sum(p_goals) / len(p_goals))
    next_assists = mathematical.next_value(assists, mins, next_mins)
    if sum(1 for n in assists if n == 0) == len(assists) - 1:
        next_assists = (sum(assists) / len(assists))
    next_yellows = min(mathematical.next_value(yellows, mins, next_mins), 1.)
    if sum(1 for n in yellows if n == 0) == len(yellows) - 1:
        next_yellows = (sum(yellows) / len(yellows))
    next_reds = min(mathematical.next_value(reds, mins, next_mins), 1.)
    if sum(1 for n in reds if n == 0) == len(reds) - 1:
        next_reds = (sum(reds) / len(reds))
    next_ogs = mathematical.next_value(ogs, mins, next_mins)
    if sum(1 for n in ogs if n == 0) == len(ogs) - 1:
        next_ogs = (sum(ogs) / len(ogs))
    score_prediction = odds.teams[team]['xg']
    concede_prediction = odds.teams[team]['xga']
    next_saves = mathematical.linear_continuation(ninety_min_saves) * next_mins / 90

    df_columns_dict = {
        'player_id': player_id,
        'player_name': player_name,
        'pos': pos,
        'team': team,
        'price': price,
        'matches_played': matches_played,
        'next_mins': next_mins,
        'next_nonp_goals': next_nonp_goals,
        'next_p_goals': next_p_goals,
        'next_assists': next_assists,
        'next_yellows': next_yellows,
        'next_reds': next_reds,
        'next_ogs': next_ogs,
        'next_saves': next_saves,
        'score_prediction': score_prediction,
        'concede_prediction': concede_prediction,
        'total_mins': total_mins_player,
        'uncertainty': uncertainty
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

# Calculation of the average number of matches played.
avg_num_of_matches = total_matches_played / total_num_of_players
avg_minutes_played = total_minutes / total_num_of_players
avg_uncertainty = total_uncertainty / total_num_of_players

print(f'Average minutes played: {avg_minutes_played}')

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

# Sorting the dataframes by total points.
all_players_df = all_players_df.sort_values(['total_points'], ascending=False).reset_index(drop=True)

# Picking the suggested squad using a knapsack algorithm.
suggested_squad, suggested_manager = budget.budget_pick(all_players_df, avg_uncertainty)

# Final output to out.html with background gradients.
with open('out.html', 'w') as out_file:
    out_file.write('<html>')
    out_file.write('<h3 style="margin: 0">Suggested Squad:</h3>')
    for player in suggested_squad[:-1]:
        out_file.write(player.name + ', ')
    out_file.write(suggested_squad[-1].name)
    out_file.write('<br>')
    out_file.write('Coach: ' + suggested_manager)
    out_file.write('<br>')
    out_file.write('<br>')
    out_file.write(all_players_df.style.background_gradient().render())
    out_file.write(odds.match_predictions_string)
    out_file.write('</html>')

beautify.run()
