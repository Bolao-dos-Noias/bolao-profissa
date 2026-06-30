import re
from datetime import datetime, timezone

from sqlmodel import Session, select

from app import db as app_db
from app.models import BetGroup, Match, Team, User

CSRF_RE = re.compile(r'name="csrf"\s+value="([^"]+)"')
TEST_CODE = "code-abc-123"
TEST_SENHA = "Abcd1234!"


def _csrf(client, path: str) -> str:
    response = client.get(path)
    match = CSRF_RE.search(response.text)
    assert match, f"sem token CSRF em {path}"
    return match.group(1)


def _create_pending_user() -> None:
    with Session(app_db.engine) as session:
        session.add(User(nickname="tester", nome_completo="Tester", invite_code=TEST_CODE, password_hash=""))
        session.commit()


def _complete_and_login(client) -> None:
    _create_pending_user()
    csrf = _csrf(client, "/login/codigo")
    response = client.post("/login/codigo", data={"csrf": csrf, "code": TEST_CODE}, follow_redirects=False)
    assert response.status_code == 303
    csrf_profile = _csrf(client, "/complete-profile")
    response = client.post(
        "/complete-profile",
        data={"csrf": csrf_profile, "nickname": "tester", "nome_completo": "Tester", "senha": TEST_SENHA},
        follow_redirects=False,
    )
    assert response.status_code == 303
    csrf_login = _csrf(client, "/login")
    response = client.post(
        "/login",
        data={"csrf": csrf_login, "nickname": "tester", "senha": TEST_SENHA},
        follow_redirects=False,
    )
    assert response.status_code == 303


def _make_active(client) -> None:
    _complete_and_login(client)
    with Session(app_db.engine) as session:
        user = session.exec(select(User).where(User.nickname == "tester")).first()
        team_a = Team(name_pt="Brasil", fifa_code="BRA", iso2="br", group_letter="A")
        team_b = Team(name_pt="Canada", fifa_code="CAN", iso2="ca", group_letter="A")
        session.add(team_a)
        session.add(team_b)
        session.commit()
        session.refresh(team_a)
        session.refresh(team_b)
        match = Match(
            stage="GROUP",
            group_letter="A",
            match_no=1,
            home_team_id=team_a.id,
            away_team_id=team_b.id,
            kickoff_utc=datetime(2026, 6, 11, 19, tzinfo=timezone.utc),
        )
        session.add(match)
        session.commit()
        session.refresh(match)
        session.add(BetGroup(user_id=user.id, match_id=match.id, pick="HOME"))
        session.commit()


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_home_public(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Bolao Profissa" in response.text


def test_login_invalid_code(client):
    _create_pending_user()
    csrf = _csrf(client, "/login/codigo")
    response = client.post("/login/codigo", data={"csrf": csrf, "code": "nao-existe"})
    assert response.status_code == 401
    assert "Codigo invalido" in response.text


def test_first_access_complete_profile_and_login(client):
    _complete_and_login(client)
    response = client.get("/")
    assert response.status_code == 200
    assert "tester" in response.text


def test_no_profile_redirects_to_complete(client):
    _create_pending_user()
    csrf = _csrf(client, "/login/codigo")
    client.post("/login/codigo", data={"csrf": csrf, "code": TEST_CODE}, follow_redirects=False)
    response = client.get("/leaderboard", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/complete-profile"


def test_no_bet_redirects_to_aposta(client):
    _complete_and_login(client)
    response = client.get("/leaderboard", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/aposta"


def test_aposta_redirect_sem_login(client):
    response = client.get("/aposta", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_leaderboard_active(client):
    _make_active(client)
    response = client.get("/leaderboard")
    assert response.status_code == 200
    assert "Ranking" in response.text


def test_regulamento_active(client):
    _make_active(client)
    response = client.get("/regulamento")
    assert response.status_code == 200
    assert "Regulamento" in response.text


def test_404_template_active(client):
    _make_active(client)
    response = client.get("/rota-inexistente-do-bolao")
    assert response.status_code == 404
    assert "404" in response.text

