# Leagues App - Football Data Integration

This app provides integration with the [football-data.org API](https://www.football-data.org/) to fetch and store football league data including matches, standings, and team information.

## Features

- Fetch match data for various leagues
- Store and update team standings
- Track match rounds/matchdays
- REST API endpoints for accessing league data
- Django admin interface for managing data

## Configuration

### 1. Get an API Key

1. Sign up at [football-data.org](https://www.football-data.org/)
2. Get your API key from the dashboard
3. Add it to your Django settings:

```python
# In myproject/settings.py
FOOTBALL_DATA_API_KEY = 'your-api-key-here'
```

Or use an environment variable:

```python
import os
FOOTBALL_DATA_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY')
```

## Management Command

### Fetch League Data

Use the `fetch_league_data` management command to fetch and save league data:

```bash
python manage.py fetch_league_data <league_code> [--season YEAR]
```

#### Parameters

- `league_code` (required): The code of the league to fetch
  - `PL` - Premier League (England)
  - `PD` - La Liga (Spain)
  - `BL1` - Bundesliga (Germany)
  - `SA` - Serie A (Italy)
  - `FL1` - Ligue 1 (France)
  - `DED` - Eredivisie (Netherlands)
  - `PPL` - Primeira Liga (Portugal)
  - `CL` - Champions League
  - `EC` - European Championship
  - `WC` - World Cup

- `--season` (optional): The year of the season to fetch (e.g., 2024)
  - If not provided, fetches the current season

#### Examples

```bash
# Fetch current Premier League season
python manage.py fetch_league_data PL

# Fetch Premier League 2024 season
python manage.py fetch_league_data PL --season 2024

# Fetch La Liga current season
python manage.py fetch_league_data PD

# Fetch Champions League 2024
python manage.py fetch_league_data CL --season 2024
```

## Models

### League
Represents a football competition/league
- `api_id`: ID from football-data.org
- `name`: League name
- `code`: League code (e.g., 'PL')
- `area_name`: Country/region

### Season
Represents a season of a league
- `league`: Foreign key to League
- `api_id`: ID from football-data.org
- `start_date`: Season start date
- `end_date`: Season end date
- `current_matchday`: Current round number
- `winner`: Season winner (if completed)

### Team
Represents a football team
- `api_id`: ID from football-data.org
- `name`: Team name
- `short_name`: Abbreviated name
- `tla`: Three-letter abbreviation
- `crest`: Team logo URL

### Match
Represents a match
- `api_id`: ID from football-data.org
- `season`: Foreign key to Season
- `utc_date`: Match date/time (UTC)
- `status`: Match status (SCHEDULED, FINISHED, etc.)
- `matchday`: Round/matchday number
- `home_team`: Foreign key to Team
- `away_team`: Foreign key to Team
- `home_score`: Home team score
- `away_score`: Away team score
- `winner`: Match winner (HOME_TEAM, AWAY_TEAM, or DRAW)

### Standing
Represents a team's position in the league table
- `season`: Foreign key to Season
- `team`: Foreign key to Team
- `position`: League position
- `played_games`: Games played
- `won`: Games won
- `draw`: Games drawn
- `lost`: Games lost
- `points`: Total points
- `goals_for`: Goals scored
- `goals_against`: Goals conceded
- `goal_difference`: Goal difference
- `standing_type`: TOTAL, HOME, or AWAY

## REST API Endpoints

All endpoints support pagination (20 items per page by default).

### Leagues

- `GET /leagues/leagues/` - List all leagues
- `GET /leagues/leagues/{id}/` - Get league details
- Query parameters:
  - `search`: Search by name or code
  - `ordering`: Order by name or created_at

### Seasons

- `GET /leagues/seasons/` - List all seasons
- `GET /leagues/seasons/{id}/` - Get season details
- Query parameters:
  - `league`: Filter by league ID
  - `league__code`: Filter by league code
  - `ordering`: Order by start_date or created_at

### Teams

- `GET /leagues/teams/` - List all teams
- `GET /leagues/teams/{id}/` - Get team details
- Query parameters:
  - `search`: Search by name, short_name, or tla
  - `ordering`: Order by name or created_at

### Matches

- `GET /leagues/matches/` - List all matches
- `GET /leagues/matches/{id}/` - Get match details
- Query parameters:
  - `season`: Filter by season ID
  - `matchday`: Filter by matchday/round number
  - `status`: Filter by match status
  - `home_team`: Filter by home team ID
  - `away_team`: Filter by away team ID
  - `ordering`: Order by utc_date, matchday, or created_at

### Standings

- `GET /leagues/standings/` - List all standings
- `GET /leagues/standings/{id}/` - Get standing details
- Query parameters:
  - `season`: Filter by season ID
  - `team`: Filter by team ID
  - `standing_type`: Filter by type (TOTAL, HOME, AWAY)
  - `group`: Filter by group (for tournaments)
  - `ordering`: Order by position, points, or goal_difference

## Examples

### Fetch and Display Premier League Data

```bash
# Fetch current Premier League data
python manage.py fetch_league_data PL

# View matches in API
curl http://localhost:8000/leagues/matches/?season__league__code=PL

# View standings
curl http://localhost:8000/leagues/standings/?season__league__code=PL&standing_type=TOTAL&ordering=position
```

### Filter Matches by Round/Matchday

```bash
# Get matches for matchday 11
curl http://localhost:8000/leagues/matches/?matchday=11

# Get matches by status
curl http://localhost:8000/leagues/matches/?status=FINISHED

# Get matches by team
curl http://localhost:8000/leagues/matches/?home_team=1
```

### Get Standings

```bash
# Get total standings ordered by position
curl http://localhost:8000/leagues/standings/?standing_type=TOTAL&ordering=position

# Get home standings
curl http://localhost:8000/leagues/standings/?standing_type=HOME&ordering=position

# Get standings for a specific team
curl http://localhost:8000/leagues/standings/?team=1
```

### Search Teams

```bash
# Search teams by name
curl http://localhost:8000/leagues/teams/?search=Arsenal

# Search by TLA (Three Letter Abbreviation)
curl http://localhost:8000/leagues/teams/?search=ARS
```

### Fetch Multiple Leagues

```bash
# Fetch multiple leagues
python manage.py fetch_league_data PL
python manage.py fetch_league_data PD
python manage.py fetch_league_data BL1
python manage.py fetch_league_data SA
python manage.py fetch_league_data FL1
```

## Rate Limits

Note that the free tier of football-data.org has rate limits:
- 10 requests per minute
- Limited competitions available

Consider this when fetching data for multiple leagues.

## Testing

Run the tests:

```bash
python manage.py test leagues
```

## Admin Interface

All models are registered in the Django admin interface at `/admin/`. You can view and manage:
- Leagues
- Seasons
- Teams
- Matches
- Standings
