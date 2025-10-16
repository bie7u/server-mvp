# server-mvp

A Django application for managing football league data using the football-data.org API.

## Features

- Integration with football-data.org API
- Models for Leagues, Seasons, Teams, Matches (with rounds support), and Standings
- Management command to fetch and sync league data
- Django admin interface for viewing and managing data

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your football-data.org API key:
```bash
export FOOTBALL_DATA_API_KEY='your_api_key_here'
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

## Usage

### Fetch League Data

Use the `fetch_league_data` management command to fetch data from football-data.org:

```bash
# Fetch current season data for a specific competition (e.g., Premier League - 2021)
python manage.py fetch_league_data 2021

# Fetch multiple competitions
python manage.py fetch_league_data 2021 2014 2015

# Fetch a specific season year
python manage.py fetch_league_data 2021 --season 2023

# Fetch all available seasons for a competition
python manage.py fetch_league_data 2021 --all-seasons
```

### Competition IDs

Common competition IDs:
- 2021: Premier League (England)
- 2014: La Liga (Spain)
- 2015: Ligue 1 (France)
- 2002: Bundesliga (Germany)
- 2019: Serie A (Italy)
- 2001: Champions League

### Django Admin

Access the admin interface at `http://localhost:8000/admin/` to view and manage:
- Leagues
- Seasons
- Teams
- Matches (with round/matchday information)
- Standings

## Models

### League
Represents a football competition/league with API ID, name, code, and area.

### Season
Represents a season of a league with start/end dates and current matchday.

### Team
Represents a football team with name, short name, TLA, and crest URL.

### Match
Represents a match between two teams including:
- Match date and status
- Matchday/round number
- Stage and group (for tournaments)
- Score information

### Standing
Represents a team's position in the league table with:
- Position
- Games played, won, drawn, lost
- Points
- Goals for/against and goal difference

## API Documentation

This project uses the football-data.org API v4. For more information, visit:
https://www.football-data.org/documentation/quickstart