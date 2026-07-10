# Revenues app

Python-based web app to simulate expected revenues given a number of trips, or the required number of trips to reach a given revenue goal.

- database.py includes functions for connecting to database and retrieving data using a pre-written query.

- cleaning.py includes functions for clenaing a dataframe, removing duplicates and rows with invalid values

- calculations.py hosts the main functions used to run simulations on the retrieved data, in order to provide the estimates for expected revenues or neede number of trips.

- support.py includes a short configuration dictionary, and a function to split a string an validate numbers from the substrings.