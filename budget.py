import data


class Player:
    def __init__(self, player_row):
        self.id = player_row['player_id']
        self.name = player_row['player_name']
        self.pos = player_row['pos']
        self.team = player_row['team']
        self.price = player_row['price']
        self.points = player_row['total_points']


def budget_pick(df):
    knapsack = []
    for _ in range(int(4 * data.TOTAL_BUDGET + .1) + 1):
        knapsack.append({})

    for player_index, player_row in df.iterrows():
        print(f'Processing player {player_index}')
        player = Player(player_row)

        new_knapsack = []
        for i in range(len(knapsack)):
            capacity = i / 4
            new_knapsack.append(knapsack[i].copy())
            if player.price < capacity + .1:
                alone_formation = [0] * 4
                alone_formation[['gk', 'd', 'm', 'st'].index(player.pos)] += 1
                alone_formation = ''.join(str(n) for n in alone_formation)
                if(alone_formation not in new_knapsack[i]) or \
                        (player.points > new_knapsack[i][alone_formation][1]):
                    new_knapsack[i][alone_formation] = ([player], player.points)

                for formation, v in knapsack[int(4 * (capacity - player.price) + .1)].items():
                    if (sum(int(c) for c in formation) == 15) or \
                            (player.pos == 'gk' and formation[0] == '2') or \
                            (player.pos == 'd' and formation[1] == '6') or \
                            (player.pos == 'm' and formation[2] == '6') or \
                            (player.pos == 'st' and formation[3] == '4') or \
                            (player.pos in ('m', 'st') and int(formation[2]) + int(formation[3]) == 9) or \
                            (player.pos in ('d', 'm') and int(formation[1]) + int(formation[2]) == 11) or \
                            (player.pos in ('d', 'st') and int(formation[1]) + int(formation[3]) == 9) or \
                            (player.pos != 'gk' and int(formation[1]) + int(formation[2]) + int(formation[3]) == 13):
                        continue

                    same_team_count = 0
                    for selected_player in v[0]:
                        if player.team == selected_player.team:
                            same_team_count += 1
                    if same_team_count == 4:
                        continue

                    new_formation = [int(c) for c in formation]
                    new_formation[['gk', 'd', 'm', 'st'].index(player.pos)] += 1
                    new_formation = ''.join(str(n) for n in new_formation)

                    if (new_formation not in new_knapsack[i]) or \
                            (v[1] + player.points > new_knapsack[i][new_formation][1]):
                        new_knapsack[i][new_formation] = (v[0] + [player], v[1] + player.points)

        knapsack = new_knapsack.copy()

    max_total_pts = 0
    max_formation = 'None'
    for formation, v in knapsack[-1].items():
        if sum(int(c) for c in formation) < 15:
            continue
        if v[1] > max_total_pts:
            max_total_pts = v[1]
            max_formation = formation

    suggested_squad = []
    for player in knapsack[-1][max_formation][0]:
        suggested_squad.append(player)

    suggested_squad.sort(key=lambda x: {'gk': 0, 'd': 1, 'm': 2, 'st': 3}[x.pos])
    return suggested_squad
