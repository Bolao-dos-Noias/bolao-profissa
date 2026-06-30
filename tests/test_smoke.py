import re
from datetime import datetime, timezone

from sqlmodel import Session, select

from app import db as app_db
from app.models import BetGroup, BetThirdsOrder, BetTieBreak, Match, Team, User
from app.services.palpites import build_bet_context

CSRF_RE = re.compile(r'name="csrf"\s+value="([^"]+)"')
TEST_CODE = "code-abc-123"
TEST_SENHA = "Abcd1234!"


async def _csrf(client, path: str) -> str:
    response = await client.get(path)
    match = CSRF_RE.search(response.text)
    assert match, f"sem token CSRF em {path}"
    return match.group(1)


def _create_pending_user() -> None:
    with Session(app_db.engine) as session:
        session.add(User(nickname="tester", nome_completo="Tester", invite_code=TEST_CODE, password_hash=""))
        session.commit()


async def _complete_and_login(client) -> None:
    _create_pending_user()
    csrf = await _csrf(client, "/login/codigo")
    response = await client.post(
        "/login/codigo",
        data={"csrf": csrf, "code": TEST_CODE},
        follow_redirects=False,
    )
    assert response.status_code == 303
    csrf_profile = await _csrf(client, "/complete-profile")
    response = await client.post(
        "/complete-profile",
        data={"csrf": csrf_profile, "nickname": "tester", "nome_completo": "Tester", "senha": TEST_SENHA},
        follow_redirects=False,
    )
    assert response.status_code == 303
    csrf_login = await _csrf(client, "/login")
    response = await client.post(
        "/login",
        data={"csrf": csrf_login, "nickname": "tester", "senha": TEST_SENHA},
        follow_redirects=False,
    )
    assert response.status_code == 303


async def _make_active(client) -> None:
    await _complete_and_login(client)
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


def _add_group_candidates() -> None:
    with Session(app_db.engine) as session:
        user = session.exec(select(User).where(User.nickname == "tester")).first()
        mexico = Team(name_pt="Mexico", fifa_code="MEX", iso2="mx", group_letter="A")
        usa = Team(name_pt="Estados Unidos", fifa_code="USA", iso2="us", group_letter="A")
        session.add(mexico)
        session.add(usa)
        session.commit()
        session.refresh(mexico)
        session.refresh(usa)
        match = Match(
            stage="GROUP",
            group_letter="A",
            match_no=2,
            home_team_id=mexico.id,
            away_team_id=usa.id,
            kickoff_utc=datetime(2026, 6, 12, 19, tzinfo=timezone.utc),
        )
        session.add(match)
        session.commit()
        session.refresh(match)
        session.add(BetGroup(user_id=user.id, match_id=match.id, pick="DRAW"))
        session.commit()


async def test_healthz(client):
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


async def test_home_public(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "Bolao Profissa" in response.text


async def test_login_invalid_code(client):
    _create_pending_user()
    csrf = await _csrf(client, "/login/codigo")
    response = await client.post("/login/codigo", data={"csrf": csrf, "code": "nao-existe"})
    assert response.status_code == 401
    assert "Codigo invalido" in response.text


async def test_first_access_complete_profile_and_login(client):
    await _complete_and_login(client)
    response = await client.get("/")
    assert response.status_code == 200
    assert "tester" in response.text


async def test_no_profile_redirects_to_complete(client):
    _create_pending_user()
    csrf = await _csrf(client, "/login/codigo")
    await client.post(
        "/login/codigo",
        data={"csrf": csrf, "code": TEST_CODE},
        follow_redirects=False,
    )
    response = await client.get("/leaderboard", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/complete-profile"


async def test_no_bet_redirects_to_aposta(client):
    await _complete_and_login(client)
    response = await client.get("/leaderboard", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/aposta"


async def test_aposta_redirect_sem_login(client):
    response = await client.get("/aposta", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


async def test_leaderboard_active(client):
    await _make_active(client)
    response = await client.get("/leaderboard")
    assert response.status_code == 200
    assert "Ranking" in response.text


async def test_regulamento_active(client):
    await _make_active(client)
    response = await client.get("/regulamento")
    assert response.status_code == 200
    assert "Regulamento" in response.text


async def test_404_template_active(client):
    await _make_active(client)
    response = await client.get("/rota-inexistente-do-bolao")
    assert response.status_code == 404
    assert "404" in response.text


async def test_perfil_nome_update(client):
    await _complete_and_login(client)
    csrf = await _csrf(client, "/perfil/nome")
    response = await client.post(
        "/perfil/nome",
        data={"csrf": csrf, "nome_completo": "Tester Atualizado", "senha_atual": TEST_SENHA},
        follow_redirects=False,
    )
    assert response.status_code == 303
    with Session(app_db.engine) as session:
        user = session.exec(select(User).where(User.nickname == "tester")).first()
        assert user.nome_completo == "Tester Atualizado"


async def test_palpite_csv_active(client):
    await _make_active(client)
    response = await client.get("/minha-aposta/completa.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "grupo,GROUP,A,1" in response.text


async def test_aposta_salva_desempate_e_terceiros(client):
    await _make_active(client)
    _add_group_candidates()
    with Session(app_db.engine) as session:
        user = session.exec(select(User).where(User.nickname == "tester")).first()
        context = build_bet_context(session, user)
        tied_row = next(row for row in context["standings"]["A"] if row.team_name == "Mexico")

    csrf = await _csrf(client, "/aposta")
    response = await client.post(
        "/aposta/grupo/A/tiebreak",
        data={"csrf": csrf, "team_id": str(tied_row.team_id), "direction": "up"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    with Session(app_db.engine) as session:
        user = session.exec(select(User).where(User.nickname == "tester")).first()
        context = build_bet_context(session, user)
        third_id = context["thirds_candidates"][0]["team_id"]

    response = await client.post(
        "/aposta/terceiros",
        data={"csrf": csrf, "team_ids": str(third_id)},
        follow_redirects=False,
    )
    assert response.status_code == 303

    with Session(app_db.engine) as session:
        user = session.exec(select(User).where(User.nickname == "tester")).first()
        assert session.exec(select(BetTieBreak).where(BetTieBreak.user_id == user.id)).first()
        thirds = session.get(BetThirdsOrder, user.id)
        assert thirds and thirds.ordered_team_ids == str(third_id)


async def test_live_palpites_do_jogo(client):
    await _make_active(client)
    with Session(app_db.engine) as session:
        match = session.exec(select(Match).where(Match.stage == "GROUP")).first()
    response = await client.get(f"/ao-vivo/jogo/{match.id}/palpites")
    assert response.status_code == 200
    assert "tester" in response.text
    assert "Mandante" in response.text
