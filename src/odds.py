import os
import re
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException

import collections

import data


def convert_odds_to_prob(odds_dict, prob_dict):
    sigma = 0
    for odds in odds_dict.values():
        sigma += 1 / odds
    for score, odds in odds_dict.items():
        prob_dict[score] = 1 / (odds * sigma)


def merge_odds(odds_lst):
    curr_sum = 0
    for odds in odds_lst:
        curr_sum += 1 / odds
    return 1 / curr_sum


class Match:
    def __init__(self, raw_name, odds_dict):
        self.name_map = {
            'Galatasaray': 'Galatasaray',
            'Konyaspor': 'Konya',
            'Hatayspor': 'Hatay',
            'Kayserispor': 'Kayseri',
            'Ümraniyespor': 'Umraniye',
            'Kasımpaşa': 'Kasimpasa',
            'İstanbulspor': 'Istanbul',
            'Beşiktaş': 'Besiktas',
            'Antalyaspor': 'Antalya',
            'Adana Demir': 'Adana Demir',
            'Başakşehir': 'Basaksehir',
            'F. Karagümrük': 'Karagumruk',
            'Trabzonspor': 'Trabzon',
            'Gaziantep': 'Gaziantep',
            'Ankaragücü': 'Ankaragucu',
            'Sivasspor': 'Sivas',
            'Fenerbahçe': 'Fenerbahce',
            'Alanyaspor': 'Alanya',
            'Giresunspor': 'Giresun',
            'Pendikspor': 'Pendik',
            'Samsunspor': 'Samsun',
            'Rizespor': 'Rize'
        }
        self.raw_home_team, self.raw_away_team = raw_name.split(' - ')
        self.home_team = self.name_map[self.raw_home_team]
        self.away_team = self.name_map[self.raw_away_team]

        self.odds_dict = odds_dict

        self.home_score_odds_lists = collections.defaultdict(lambda: [])
        self.away_score_odds_lists = collections.defaultdict(lambda: [])
        self.home_score_odds = {}
        self.away_score_odds = {}
        self.home_score_prob_dict = {}
        self.away_score_prob_dict = {}
        self.home_xg = 0
        self.away_xg = 0
        self.home_cs_odds_list = []
        self.away_cs_odds_list = []
        self.home_ncs_odds_list = []
        self.away_ncs_odds_list = []
        self.home_cs_odds = 0
        self.away_cs_odds = 0
        self.home_ncs_odds = 0
        self.away_ncs_odds = 0
        self.home_cs_prob = 0
        self.away_cs_prob = 0
        self.home_w_odds_list = []
        self.away_w_odds_list = []
        self.home_nw_odds_list = []
        self.away_nw_odds_list = []
        self.home_w_odds = 0
        self.away_w_odds = 0
        self.home_nw_odds = 0
        self.away_nw_odds = 0
        self.home_w_prob = 0
        self.away_w_prob = 0

        self.calculate_xg()
        self.calculate_cs_prob()
        self.calculate_w_prob()

    def calculate_xg(self):
        for score, odds in self.odds_dict.items():
            self.home_score_odds_lists[int(score[0])].append(odds)
            self.away_score_odds_lists[int(score[2])].append(odds)

        for score, odds_lst in self.home_score_odds_lists.items():
            self.home_score_odds[score] = merge_odds(odds_lst)

        for score, odds_lst in self.away_score_odds_lists.items():
            self.away_score_odds[score] = merge_odds(odds_lst)

        convert_odds_to_prob(self.home_score_odds, self.home_score_prob_dict)
        convert_odds_to_prob(self.away_score_odds, self.away_score_prob_dict)

        for score, prob in self.home_score_prob_dict.items():
            self.home_xg += score * prob
        for score, prob in self.away_score_prob_dict.items():
            self.away_xg += score * prob

    def calculate_cs_prob(self):
        for score, odds in self.odds_dict.items():
            if score[2] == '0':
                self.home_cs_odds_list.append(odds)
            else:
                self.home_ncs_odds_list.append(odds)

            if score[0] == '0':
                self.away_cs_odds_list.append(odds)
            else:
                self.away_ncs_odds_list.append(odds)

        self.home_cs_odds = merge_odds(self.home_cs_odds_list)
        self.away_cs_odds = merge_odds(self.away_cs_odds_list)
        self.home_ncs_odds = merge_odds(self.home_ncs_odds_list)
        self.away_ncs_odds = merge_odds(self.away_ncs_odds_list)

        self.home_cs_prob = self.home_ncs_odds / (self.home_cs_odds + self.home_ncs_odds)
        self.away_cs_prob = self.away_ncs_odds / (self.away_cs_odds + self.away_ncs_odds)

    def calculate_w_prob(self):
        for score, odds in self.odds_dict.items():
            if int(score[0]) > int(score[2]):
                self.home_w_odds_list.append(odds)
                self.away_nw_odds_list.append(odds)
            elif int(score[0]) == int(score[2]):
                self.home_nw_odds_list.append(odds)
                self.away_nw_odds_list.append(odds)
            else:
                self.home_nw_odds_list.append(odds)
                self.away_w_odds_list.append(odds)

        self.home_w_odds = merge_odds(self.home_w_odds_list)
        self.away_w_odds = merge_odds(self.away_w_odds_list)
        self.home_nw_odds = merge_odds(self.home_nw_odds_list)
        self.away_nw_odds = merge_odds(self.away_nw_odds_list)

        self.home_w_prob = self.home_nw_odds / (self.home_w_odds + self.home_nw_odds)
        self.away_w_prob = self.away_nw_odds / (self.away_w_odds + self.away_nw_odds)


if os.name != 'posix':
    os.environ["Path"] += os.pathsep + r'C:\Program Files\gecko'

driver = webdriver.Firefox()
driver.get('https://www.nesine.com/iddaa?et=1&lc=584&le=3&ocg=MS-2%2C5&gt=Pop%C3%BCler')
driver.implicitly_wait(10)

driver.maximize_window()
while True:
    try:
        driver.find_element(By.ID, 'c-p-bn').click()
        time.sleep(1)
        break
    except:
        pass

# wtf is this bug, I still don't understand
# when clicking a list of buttons in the page sequentially, selenium sometimes clicks the first button twice
if os.name != 'posix':
    driver.find_element(By.CLASS_NAME, 'more-btn').click()
    time.sleep(1)

for more_button in driver.find_elements(By.CLASS_NAME, 'more-btn'):
    more_button.click()
    time.sleep(1)

match_names = []
for match_row in driver.find_elements(By.CLASS_NAME, 'code-time-name'):
    match_name = match_row.find_element(By.CLASS_NAME, 'name').find_element(By.TAG_NAME, 'a').text.strip()
    if '-' in match_name:
        match_names.append(match_name)

# for _ in range(4):
#     match_names.pop()

odds_lst = []
for panel in driver.find_elements(By.CLASS_NAME, 'panel-default'):
    if panel.find_element(By.CLASS_NAME, 'panel-title').find_element(By.TAG_NAME, 'a').text.strip().lower() == 'maç skoru':
        labels = [label.text for label in panel.find_elements(By.CLASS_NAME, 'lbl')]
        odds = [odd.text for odd in panel.find_elements(By.CLASS_NAME, 'odd')]
        odds_dict = {}
        for i in range(len(labels)):
            if re.match(r'^\d-\d$', labels[i]):
                odds_dict[labels[i]] = float(odds[i])
        odds_lst.append(odds_dict.copy())

driver.quit()

if len(match_names) != len(odds_lst):
    print('Scraping error: array length mismatch')
    sys.exit(1)

matches = []
for i in range(len(match_names)):
    matches.append(Match(match_names[i], odds_lst[i]))

print(f'Odds of {len(matches)} match(es) scraped from nesine')

teams = {}
match_predictions_string = ''
for match in matches:
    match_predictions_string += f'{match.home_team} - {match.away_team}:<br>'
    match_predictions_string += f'xG: {match.home_xg} - {match.away_xg}<br>'
    match_predictions_string += f'CS prob: {match.home_cs_prob} - {match.away_cs_prob}<br>'
    match_predictions_string += f'win prob: {match.home_w_prob} - {match.away_w_prob}<br>'
    match_predictions_string += '<br>'

    home_coach_points = match.home_w_prob - 2 * match.away_w_prob
    away_coach_points = -home_coach_points

    teams[match.home_team] = {'xg': match.home_xg, 'xga': match.away_xg, 'cs_prob': match.home_cs_prob,
                              'w_prob': match.home_w_prob, 'l_prob': match.away_w_prob,
                              'coach_points': home_coach_points}
    teams[match.away_team] = {'xg': match.away_xg, 'xga': match.home_xg, 'cs_prob': match.away_cs_prob,
                              'w_prob': match.away_w_prob, 'l_prob': match.home_w_prob,
                              'coach_points': away_coach_points}

    if match.home_team in data.managers_dict:
        data.managers_dict[match.home_team] = (data.managers_dict[match.home_team][0], home_coach_points)
    if match.away_team in data.managers_dict:
        data.managers_dict[match.away_team] = (data.managers_dict[match.away_team][0], away_coach_points)


max_coach_points = 0
max_coach_points_team = ''
for team_name, v in teams.items():
    if v['coach_points'] > max_coach_points:
        max_coach_points = v['coach_points']
        max_coach_points_team = team_name
