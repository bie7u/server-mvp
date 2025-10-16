# Football Data Integration Demo

This demo shows how to use the football-data.org API integration.

## Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your API key:
```bash
export FOOTBALL_DATA_API_KEY="your-api-key-here"
```

Or add it to `myproject/settings.py`:
```python
FOOTBALL_DATA_API_KEY = "your-api-key-here"
```

## Step 1: Run Migrations

```bash
python manage.py migrate
```

## Step 2: Fetch League Data

### Fetch Premier League (Current Season)
```bash
python manage.py fetch_league_data PL
```

Expected output:
```
Fetching data for league: PL
Season: Current
Successfully fetched and saved league data:
  League: Premier League
  Season: Premier League 2024/2025
  Matches: 380
  Standings: 20
```

### Fetch La Liga (Specific Season)
```bash
python manage.py fetch_league_data PD --season 2024
```

### Fetch Multiple Leagues
```bash
python manage.py fetch_league_data PL
python manage.py fetch_league_data PD
python manage.py fetch_league_data BL1
python manage.py fetch_league_data SA
python manage.py fetch_league_data FL1
```

## Step 3: Start the Development Server

```bash
python manage.py runserver
```

## Step 4: Access the API

### View All Leagues
```bash
curl http://localhost:8000/leagues/leagues/
```

### View Standings (Ordered by Position)
```bash
curl http://localhost:8000/leagues/standings/?standing_type=TOTAL&ordering=position
```

### View Matches for a Specific Matchday
```bash
curl http://localhost:8000/leagues/matches/?matchday=10
```

### Search for a Team
```bash
curl http://localhost:8000/leagues/teams/?search=Arsenal
```

### Filter Matches by Status
```bash
# Upcoming matches
curl http://localhost:8000/leagues/matches/?status=SCHEDULED

# Finished matches
curl http://localhost:8000/leagues/matches/?status=FINISHED
```

### Get Matches for a Specific Team
```bash
# Get team ID first
curl http://localhost:8000/leagues/teams/?search=Manchester

# Then get their matches (replace 1 with actual team ID)
curl http://localhost:8000/leagues/matches/?home_team=1
```

## Step 5: Access Django Admin

1. Create a superuser:
```bash
python manage.py createsuperuser
```

2. Visit http://localhost:8000/admin/ and log in

3. You can now manage:
   - Leagues
   - Seasons
   - Teams
   - Matches
   - Standings

## Available League Codes

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

## Data Model Overview

```
League
  ├── Season(s)
  │   ├── Match(es)
  │   │   ├── Home Team
  │   │   └── Away Team
  │   └── Standing(s)
  │       └── Team
  └── Team(s)
```

## API Response Format

All endpoints return paginated results:

```json
{
  "count": 380,
  "next": "http://localhost:8000/leagues/matches/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "home_team": {
        "name": "Manchester City",
        "tla": "MCI"
      },
      "away_team": {
        "name": "Arsenal",
        "tla": "ARS"
      },
      "matchday": 10,
      "status": "SCHEDULED",
      "utc_date": "2024-10-23T14:00:00Z"
    }
  ]
}
```

## Updating Data

To update existing data, simply run the fetch command again:

```bash
python manage.py fetch_league_data PL
```

The system will:
- Update existing leagues, teams, and matches
- Add new matches that weren't in the database
- Update scores for completed matches
- Update standings

## Error Handling

If you see an error about missing API key:
```
CommandError: Configuration error: Football Data API key is required
```

Make sure you've set `FOOTBALL_DATA_API_KEY` in your environment or settings.

## Rate Limits

The free tier has limitations:
- 10 requests per minute
- Limited number of competitions

Plan your data fetches accordingly to avoid rate limit errors.
