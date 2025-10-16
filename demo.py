#!/usr/bin/env python
"""
Demo script to show how to use the football-data.org integration.
This is for demonstration purposes only.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_mvp.settings')
django.setup()

from leagues.models import League, Season, Team, Match, Standing
from django.db.models import Q


def print_section(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)


def demo_queries():
    """Demonstrate various database queries."""
    
    print_section("LEAGUES")
    leagues = League.objects.all()
    if leagues.exists():
        for league in leagues:
            print(f"- {league.name} ({league.code}) - Area: {league.area_name}")
    else:
        print("No leagues found. Run: python manage.py fetch_league_data 2021")
    
    print_section("SEASONS")
    seasons = Season.objects.all()
    if seasons.exists():
        for season in seasons:
            print(f"- {season}")
            print(f"  Current Matchday: {season.current_matchday}")
    else:
        print("No seasons found.")
    
    print_section("TEAMS")
    teams = Team.objects.all()[:10]  # Show first 10 teams
    if teams.exists():
        for team in teams:
            print(f"- {team.name} ({team.tla})")
    else:
        print("No teams found.")
    
    print_section("RECENT MATCHES")
    matches = Match.objects.all().order_by('-utc_date')[:10]
    if matches.exists():
        for match in matches:
            score = f"{match.home_score or '-'}:{match.away_score or '-'}" if match.status == 'FINISHED' else "vs"
            print(f"- Round {match.matchday}: {match.home_team.name} {score} {match.away_team.name}")
            print(f"  Date: {match.utc_date.strftime('%Y-%m-%d %H:%M')} - Status: {match.status}")
    else:
        print("No matches found.")
    
    print_section("STANDINGS")
    if Season.objects.exists():
        season = Season.objects.first()
        standings = Standing.objects.filter(season=season).order_by('position')[:5]
        if standings.exists():
            print(f"Top 5 in {season}:")
            print(f"{'Pos':<4} {'Team':<30} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'GD':<5} {'Pts':<4}")
            print("-" * 60)
            for standing in standings:
                print(f"{standing.position:<4} {standing.team.name:<30} "
                      f"{standing.played_games:<4} {standing.won:<4} {standing.draw:<4} "
                      f"{standing.lost:<4} {standing.goal_difference:>4} {standing.points:<4}")
        else:
            print(f"No standings found for {season}")
    else:
        print("No seasons found.")
    
    print_section("STATISTICS")
    print(f"Total Leagues: {League.objects.count()}")
    print(f"Total Seasons: {Season.objects.count()}")
    print(f"Total Teams: {Team.objects.count()}")
    print(f"Total Matches: {Match.objects.count()}")
    print(f"Total Standings: {Standing.objects.count()}")
    print(f"Finished Matches: {Match.objects.filter(status='FINISHED').count()}")
    print(f"Scheduled Matches: {Match.objects.filter(status__in=['SCHEDULED', 'TIMED']).count()}")


if __name__ == '__main__':
    demo_queries()
