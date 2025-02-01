from fastapi import APIRouter, status, Query
from typing import Optional, List, Annotated
from database.ORM import ORM
from database.models import RegisteredUser
from database.util import parse_score_filters
from database.userService import get_top_n, get_profile_pp, get_ids_from_tag
from database.leaderboardService import group_leaderboard

router = APIRouter()
orm = ORM()

@router.get('/test')
def get_user(user_id: int):
    """
    Fetches a user from the database from their user_id
    """
    return {"user": orm.session.get(RegisteredUser, user_id)}

@router.get('/top', status_code=status.HTTP_200_OK)
def top_n(user_id: int, mode: str or int = 'osu', filters: Optional[str] = None, metric: str = 'pp', n: int = 100, unique: bool = True):
    filters = parse_score_filters(mode, filters)
    session = orm.sessionmaker()
    n = min(100, n) # 100 is the max number of maps
    a = get_top_n(session, user_id, mode, filters, metric, n, unique)
    session.close()
    return {"scores": a}

@router.get('/profile_pp', status_code=status.HTTP_200_OK)
def profile_pp(user_id: int, mode: str or int = 'osu', filters: Optional[str] = None, n: int = 100, bonus: bool = True, unique: bool = True):
    n = min(100, n)  # 100 is the max number of maps
    scores = top_n(user_id, mode, filters, 'pp', n, unique)['scores']
    total_pp = get_profile_pp(scores, bonus, n)
    return {"total_pp": total_pp, "scores": scores}

@router.get('/group_leaderboard', status_code=status.HTTP_200_OK)
def get_group_leaderboard(beatmap_id: int, users: Annotated[list[int] | None, Query()] = None, group_tag: str = None, mode: str or int = 'osu', filters: Optional[str] = None, metric: str = 'pp', unique: bool = True):
    filters = parse_score_filters(mode, filters)
    session = orm.sessionmaker()
    if users is None:
        users = get_ids_from_tag(session, group_tag)
    scores = group_leaderboard(session, users, beatmap_id, mode, filters, metric, unique)
    session.close()
    return {"Leaderboard for %s" % beatmap_id: scores}