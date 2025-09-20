from typing import Any, Dict
import requests
import random
import string

from unittest.mock import patch

from app.test_shared.constants import MOCK_TEAM_NAME
from dev_scripts.original_e2e import login

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


def get_team_and_invite_other_users_module(
    exec_user: Dict[str, str], member_users: list[Dict[str, str]]
) -> None:

    def get_team_for_session(session: requests.Session) -> Any:
        response = session.get(f"{BASE_URL}/teams/get-current-user-teams")
        assert response.status_code == 200, f"Get team failed: {response.text}"
        teams = response.json().get("teams")
        assert teams and len(teams) > 0, "No teams found"
        return teams[0]

    def invite_user_to_team(
        session: requests.Session, team_id: str, email: str
    ) -> None:
        response = session.post(
            f"{BASE_URL}/teams/invite-user",
            json={"team_id": team_id, "email": email},
        )
        assert response.status_code == 200, f"Invite user failed: {response.text}"

    exec_session = login_session(exec_user["email"], exec_user["password"])
    team = get_team_for_session(exec_session)
    team_id = team["id"]

    for member in member_users:
        invite_user_to_team(exec_session, team_id, member["email"])


@patch("app.service.user.send_verification_code_email")
def test_end_to_end(mock_send_verification_code_email):

    mock_send_verification_code_email.return_value = None

    print("Beginning end-to-end test...")
    print(f"SESSION_STRING: {SESSION_STRING}")

    users = init_module()
    print("Init module completed successfully")

    register_all_users_module(users)
    print("Register module completed successfully")

    verify_all_users_module(users)
    print("Verify module completed successfully")

    create_team_module(users["exec"])
    print("Create team module completed successfully")

    

    assert 1 == 2

    # get_team_and_invite_other_users_module(
    #     users["exec"], [users["member1"], users["member2"], users["member3"]]
    # )
    # print("Get team and invite other users module completed successfully")
