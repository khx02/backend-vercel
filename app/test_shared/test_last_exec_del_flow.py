import os
import pytest
from typing import Dict
import requests
import random
import string


from app.test_shared.constants import (
    MOCK_TEAM_NAME,
)

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

BASE_URL = "http://localhost:8000/api"
SESSION_STRING = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


# Common functions
def login_session(email: str, password: str) -> requests.Session:
    session = requests.Session()

    response = session.post(
        f"{BASE_URL}/auth/set-token", data={"username": email, "password": password}
    )

    assert response.status_code == 200, f"Login failed: {response.text}"

    token = response.json().get("access_token")

    session.headers.update({"Authorization": f"Bearer {token}"})

    return session


# End to end modules
def init_module():

    users = {
        "exec": {
            "email": f"exec_user_{SESSION_STRING}@example.com",
            "password": SESSION_STRING,
            "first_name": "Exec",
            "last_name": "User",
        },
        "member1": {
            "email": f"member1_user_{SESSION_STRING}@example.com",
            "password": SESSION_STRING,
            "first_name": "Member",
            "last_name": "One",
        },
        "member2": {
            "email": f"member2_user_{SESSION_STRING}@example.com",
            "password": SESSION_STRING,
            "first_name": "Member",
            "last_name": "Two",
        },
        "member3": {
            "email": f"member3_user_{SESSION_STRING}@example.com",
            "password": SESSION_STRING,
            "first_name": "Member",
            "last_name": "Three",
        },
    }

    return users


def register_all_users_module(users: Dict[str, Dict[str, str]]) -> None:

    def register_user(email: str, password: str, first_name: str, last_name: str):
        session = requests.Session()

        response = session.post(
            f"{BASE_URL}/users/register",
            json={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "send_email": False,
            },
        )

        assert response.status_code == 200, f"Register failed: {response.text}"

    for user in users.values():
        register_user(
            user["email"], user["password"], user["first_name"], user["last_name"]
        )


def verify_all_users_module(users: Dict[str, Dict[str, str]]) -> None:

    def verify_user(email: str):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/users/verify-code",
            json={"email": email, "verification_code": "meow"},
        )

        assert response.status_code == 200, f"Verify failed: {response.text}"

    for user in users.values():
        verify_user(user["email"])


def create_team_module(user: Dict[str, str]) -> None:

    def create_team_for_session(session: requests.Session, name: str) -> None:
        response = session.post(f"{BASE_URL}/teams/create-team", json={"name": name})
        assert response.status_code == 200, f"Create team failed: {response.text}"

    create_team_for_session(
        login_session(user["email"], user["password"]),
        f"{MOCK_TEAM_NAME} {SESSION_STRING}",
    )


def others_join_team_module(users: Dict[str, Dict[str, str]]) -> None:

    def join_team(session: requests.Session, team_short_id: str) -> None:
        response = session.post(
            f"{BASE_URL}/teams/join-team-by-short-id/{team_short_id}"
        )
        assert response.status_code == 200, f"Join team failed: {response.text}"

    # First, the exec will get the team short ID and tell others via other means
    exec_session = login_session(users["exec"]["email"], users["exec"]["password"])
    resp = exec_session.get(f"{BASE_URL}/users/get-current-user-teams")
    assert resp.status_code == 200, f"Get exec teams failed: {resp.text}"

    team_short_id = resp.json()["teams"][0]["short_id"]

    for member in ["member1", "member2", "member3"]:
        member_session = login_session(
            users[member]["email"], users[member]["password"]
        )
        join_team(member_session, team_short_id)


def promote_member_1_to_exec_module(users: Dict[str, Dict[str, str]]) -> None:

    def promote_member(session: requests.Session, team_id: str, user_id: str) -> None:
        response = session.post(
            f"{BASE_URL}/teams/promote-team-member/{team_id}",
            json={"member_id": user_id},
        )
        assert response.status_code == 200, f"Promote member failed: {response.text}"

    # Exec member will log in and get team ID
    exec_session = login_session(users["exec"]["email"], users["exec"]["password"])
    resp = exec_session.get(f"{BASE_URL}/users/get-current-user-teams")
    assert resp.status_code == 200, f"Get exec teams failed: {resp.text}"

    team_id = resp.json()["teams"][0]["id"]

    # Get member1 user ID
    member1_session = login_session(
        users["member1"]["email"], users["member1"]["password"]
    )
    resp = member1_session.get(f"{BASE_URL}/users/get-current-user")
    assert resp.status_code == 200, f"Get member1 info failed: {resp.text}"
    member1_user_id = resp.json()["user"]["id"]

    # Exec member will execute promotion
    promote_member(exec_session, team_id, member1_user_id)


def member_1_exec_leaves_team_module(user: Dict[str, str]) -> None:

    def leave_team(session: requests.Session, team_id: str) -> None:
        response = session.post(f"{BASE_URL}/teams/leave-team/{team_id}")
        assert response.status_code == 200, f"Leave team failed: {response.text}"

    member1_session = login_session(user["email"], user["password"])
    resp = member1_session.get(f"{BASE_URL}/users/get-current-user-teams")
    assert resp.status_code == 200, f"Get member1 teams failed: {resp.text}"

    team_id = resp.json()["teams"][0]["id"]

    leave_team(
        login_session(user["email"], user["password"]),
        team_id,
    )


def users_should_have_team_module(users: Dict[str, Dict[str, str]]) -> None:

    def check_has_team(session: requests.Session) -> None:
        response = session.get(f"{BASE_URL}/users/get-current-user-teams")
        assert response.status_code == 200, f"Get teams failed: {response.text}"
        assert len(response.json().get("teams", [])) == 1, "User does not have a team!"

    for user in users.values():
        check_has_team(
            login_session(user["email"], user["password"]),
        )


def exec_leave_team_module(user: Dict[str, str]) -> None:

    def leave_team(session: requests.Session, team_id: str) -> None:
        response = session.post(f"{BASE_URL}/teams/leave-team/{team_id}")
        assert response.status_code == 200, f"Leave team failed: {response.text}"

    exec_session = login_session(user["email"], user["password"])
    resp = exec_session.get(f"{BASE_URL}/users/get-current-user-teams")
    assert resp.status_code == 200, f"Get exec teams failed: {resp.text}"

    team_id = resp.json()["teams"][0]["id"]

    leave_team(
        login_session(user["email"], user["password"]),
        team_id,
    )


def users_should_have_no_team_module(users: Dict[str, Dict[str, str]]) -> None:

    def check_no_teams(session: requests.Session) -> None:
        response = session.get(f"{BASE_URL}/users/get-current-user-teams")
        assert response.status_code == 200, f"Get teams failed: {response.text}"
        assert len(response.json().get("teams", [])) == 0, "User still has a team!"

    for user in users.values():
        check_no_teams(
            login_session(user["email"], user["password"]),
        )


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_delete_team_via_last_exec_flow():

    print("Beginning delete team via last exec flow test...")
    print(f"SESSION_STRING: {SESSION_STRING}")

    users = init_module()
    print("Init module completed successfully")

    register_all_users_module(users)
    print("Register all users module completed successfully")

    verify_all_users_module(users)
    print("Verify all users module completed successfully")

    create_team_module(users["exec"])
    print("Create team module completed successfully")

    others_join_team_module(users)
    print("Others join team module completed successfully")

    users_should_have_team_module(users)
    print("Users should have team module completed successfully")

    # Promote member 1 to exec
    promote_member_1_to_exec_module(users)
    print("Promote member 1 to exec module completed successfully")

    member_1_exec_leaves_team_module(users["member1"])
    print("Member 1 exec leaves team module completed successfully")

    # All users except member 1 should still have a team
    users_should_have_team_module({k: v for k, v in users.items() if k != "member1"})
    print("Users outside of member 1 should have team module completed successfully")

    # Last exec leaves team
    exec_leave_team_module(users["exec"])

    # Team should be deleted, all users should not have a team
    users_should_have_no_team_module(users)
    print("Users should have no team module completed successfully")

    print("Delete team via last exec flow test completed successfully")
