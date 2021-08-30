# pososyal_v2.0
A script that helps creating POSosyal fantasy football lineups, using statistics.

The statistical data of all players in the Turkish Super Lig is contained in a database. The data needed for this script to run for each player are:
* Minutes played
* Goals scored
* Penalty goals scored
* Assists made
* Yellow cards
* Red cards
* Own goals

This data is structured in a Pandas dataframe. Dynamic models are used to predict how many points each player will score in the next gameweek. Of course, as the predicted points are purely statistical, they usually aren't precisely correct.

After the data is processed and the predicted points for each player are calculated, this data is rendered in an HTML table with background gradients in order to detect stats that stand out among others.
