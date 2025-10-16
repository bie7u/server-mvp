# Implementation Details

## Overview

This project implements a complete integration with the football-data.org API v4 to manage football league data including matches, standings, and team information.

## Architecture

### Models (`leagues/models.py`)

**League**
- Stores football competitions/leagues
- Fields: api_id, name, code, area_name
- Unique constraint on api_id

**Season**
- Represents a season within a league
- Links to League via ForeignKey
- Tracks start/end dates and current matchday
- Unique constraint on (league, api_id)

**Team**
- Stores team information
- Fields: api_id, name, short_name, tla, crest
- Unique constraint on api_id

**Match**
- Stores match information with round/matchday support
- Links to Season, home_team, and away_team
- Fields include: utc_date, status, matchday, stage, group
- Score tracking: home_score, away_score, winner
- Ordered by utc_date

**Standing**
- Stores league table positions
- Links to Season and Team
- Tracks: position, games played, wins, draws, losses
- Statistics: points, goals for/against, goal difference
- Unique constraint on (season, team)

### API Client (`leagues/services.py`)

**FootballDataAPIClient**
- Handles all HTTP communication with football-data.org API
- Methods:
  - `get_competition(competition_id)`: Fetch competition details
  - `get_matches(competition_id, season)`: Fetch matches
  - `get_standings(competition_id, season)`: Fetch standings
  - `get_teams(competition_id, season)`: Fetch teams
- Authentication via X-Auth-Token header
- Configurable via FOOTBALL_DATA_API_KEY setting

### Data Importer (`leagues/importers.py`)

**FootballDataImporter**
- Processes API responses and saves to database
- Main method: `import_competition_data(competition_id, season_year)`
- Helper methods:
  - `_save_league(data)`: Create/update league
  - `_save_season(league, data)`: Create/update season
  - `_save_team(data)`: Create/update team
  - `_import_matches(competition_id, season)`: Import all matches
  - `_import_standings(competition_id, season)`: Import standings
- Uses update_or_create for idempotent operations
- Handles missing data gracefully

### Management Command (`leagues/management/commands/fetch_league_data.py`)

**fetch_league_data**
- Django management command for data import
- Arguments:
  - `competition_ids`: One or more competition IDs (required)
  - `--season`: Specific season year to fetch (optional)
  - `--all-seasons`: Fetch all available seasons (flag)
- Usage examples:
  ```bash
  python manage.py fetch_league_data 2021
  python manage.py fetch_league_data 2021 --season 2023
  python manage.py fetch_league_data 2021 --all-seasons
  python manage.py fetch_league_data 2021 2014 2015
  ```

### Admin Interface (`leagues/admin.py`)

All models registered with customized admin classes:
- **LeagueAdmin**: List display, search by name/code
- **SeasonAdmin**: List display, filter by league
- **TeamAdmin**: List display, search by name/short_name/tla
- **MatchAdmin**: List display with scores, filter by season/status/matchday
- **StandingAdmin**: List display with statistics, filter by season

## Configuration

### Environment Variables

**FOOTBALL_DATA_API_KEY** (required)
- Set in environment or .env file
- Used for API authentication
- Get free key at: https://www.football-data.org/client/register

### Django Settings

Added to `server_mvp/settings.py`:
- `leagues` app in INSTALLED_APPS
- FOOTBALL_DATA_API_KEY configuration

## Data Flow

1. User runs `fetch_league_data` command with competition ID
2. Command creates FootballDataImporter instance
3. Importer fetches competition data from API
4. League and Season models are created/updated
5. Matches are fetched and imported
   - Teams are created/updated as needed
   - Match records include matchday/round information
6. Standings are fetched and imported
   - Existing standings are cleared for the season
   - New standings are created with full statistics
7. Success message displayed

## Round/Matchday Support

The Match model includes a `matchday` field that represents the round number:
- Premier League: 1-38 (each team plays 38 matches)
- Champions League: Group stage matchdays (1-6), knockout rounds
- Other competitions: Varies by competition structure

Matches can be filtered by matchday:
```python
Match.objects.filter(matchday=10)  # Get all round 10 matches
```

## Testing

Unit tests in `leagues/tests.py` cover:
- League model creation
- Season model creation and relationships
- Team model creation
- Match model creation with all fields
- Standing model creation with statistics

Run tests:
```bash
python manage.py test leagues
```

## Security

- API key stored in environment variable (not in code)
- No sensitive data committed to repository
- db.sqlite3 excluded via .gitignore
- All dependencies checked for vulnerabilities
- CodeQL analysis passed with 0 alerts

## API Rate Limits

Football-data.org free tier:
- 10 requests per minute
- 100 requests per day

The importer makes approximately:
- 1 request for competition details
- 1 request for matches
- 1 request for standings
- Total: ~3 requests per season

Be mindful when using `--all-seasons` flag.

## Future Enhancements

Possible improvements:
- Caching layer to reduce API calls
- Celery tasks for background data fetching
- Webhook support for real-time updates
- REST API endpoints to expose data
- Frontend dashboard for viewing data
- Support for more granular data (player statistics, etc.)
