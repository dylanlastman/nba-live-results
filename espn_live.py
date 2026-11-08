#!/usr/bin/env python3
"""Fetch tonight's NBA box scores from ESPN and write them in the NBA Plays board's live/stats shape.

Same format the Google Apps Script writes to Drive:
{v:1, at, day:'YYYYMMDD', games:[{id, a, h, s:'pre'|'in'|'post', d, at, p:[[name, team, dnp, pts, reb, ast, 3pm, stl, blk, to, min]]}]}
plus checkedAt / by / cleared so the board treats it as a fresh check.

Usage: python3 espn_live.py out.json
"""
import json, os, sys, urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

API = 'https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/'


def get(url):
    req = urllib.request.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'nba-plays-board'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def num(keys, vals, name):
    if name not in keys:
        return 0
    i = keys.index(name)
    v = vals[i] if i < len(vals) else None
    if v in (None, ''):
        return 0
    try:
        return int(str(v).split('-')[0])
    except ValueError:
        return 0


def main(out):
    # The betting night runs 6 AM to 6 AM New York time.
    day = (datetime.now(ZoneInfo('America/New_York')) - timedelta(hours=6)).strftime('%Y%m%d')
    sb = get(API + 'scoreboard?dates=' + day)
    games = []
    for ev in sb.get('events', []):
        c = ev['competitions'][0]
        st = c['status']['type']
        team = lambda ha: next((x for x in c['competitors'] if x.get('homeAway') == ha), {}).get('team', {})
        g = {'id': ev['id'], 'a': team('away').get('abbreviation'), 'h': team('home').get('abbreviation'),
             's': st['state'], 'd': st.get('shortDetail'), 'at': ev.get('date'), 'p': []}
        if st['state'] != 'pre':
            box = (get(API + 'summary?event=' + ev['id']).get('boxscore') or {}).get('players') or []
            for t in box:
                for blk in t.get('statistics') or []:
                    k = blk.get('keys') or []
                    for a in blk.get('athletes') or []:
                        v = a.get('stats') or []
                        dnp = 1 if (a.get('didNotPlay') or not v) else 0
                        g['p'].append([a['athlete']['displayName'], t['team']['abbreviation'], dnp,
                                       num(k, v, 'points'), num(k, v, 'rebounds'), num(k, v, 'assists'),
                                       num(k, v, 'threePointFieldGoalsMade-threePointFieldGoalsAttempted'),
                                       num(k, v, 'steals'), num(k, v, 'blocks'), num(k, v, 'turnovers'),
                                       num(k, v, 'minutes')])
        games.append(g)
    # Only save while something is happening: a game in progress, or one that tipped in the last 4.5 hours
    # (so finals land). Otherwise write nothing and the workflow skips the save. FORCE=1 always saves.
    nowdt = datetime.now(timezone.utc)
    def recent(g):
        try:
            return nowdt - datetime.fromisoformat(g['at'].replace('Z', '+00:00')) < timedelta(hours=4.5)
        except Exception:
            return False
    active = any(g['s'] == 'in' or (g['s'] == 'post' and recent(g)) for g in games)
    if not active and os.environ.get('FORCE') != '1':
        print(f'{day}: {len(games)} games, none live or just finished; nothing to save')
        return
    now = nowdt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    body = {'v': 1, 'at': now, 'day': day, 'games': games, 'checkedAt': now, 'by': 'auto', 'cleared': False}
    with open(out, 'w') as f:
        json.dump(body, f, separators=(',', ':'))
    print(f'{day}: {len(games)} games, {sum(len(g["p"]) for g in games)} player rows -> {out}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'live.json')
