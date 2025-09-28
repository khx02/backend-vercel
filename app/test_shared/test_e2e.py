import os
import pytest
from typing import Dict
import requests
import random
import string


from app.test_shared.constants import (
    MOCK_PROJECT_DESCRIPTION,
    MOCK_PROJECT_NAME,
    MOCK_TEAM_NAME,
    MOCK_TODO_DESCRIPTION,
    MOCK_TODO_NAME,
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


def create_team_project_and_todos_module(user: Dict[str, str]) -> None:

    def add_todo_item(
        session: requests.Session, project_id: str, todo_data: Dict[str, str]
    ) -> None:
        response = session.post(
            f"{BASE_URL}/projects/add-todo/{project_id}",
            json=todo_data,
        )
        assert response.status_code == 200, f"Add todo failed: {response.text}"

    # Get the user's team
    session = login_session(user["email"], user["password"])
    resp = session.get(f"{BASE_URL}/users/get-current-user-teams")
    assert resp.status_code == 200, f"Get user teams failed: {resp.text}"
    team_id = resp.json()["teams"][0]["id"]

    # Create a project for the team
    response = session.post(
        f"{BASE_URL}/teams/create-project/{team_id}",
        json={
            "name": f"{MOCK_PROJECT_NAME} {SESSION_STRING}",
            "description": f"{MOCK_PROJECT_DESCRIPTION} {SESSION_STRING}",
        },
    )
    assert response.status_code == 200, f"Create project failed: {response.text}"
    project_id = response.json()["project"]["id"]

    # Create three todo items
    todos = [
        {
            "name": f"1 {MOCK_TODO_NAME}",
            "description": f"1 {MOCK_TODO_DESCRIPTION} {SESSION_STRING}",
        },
        {
            "name": f"2 {MOCK_TODO_NAME}",
            "description": f"2 {MOCK_TODO_DESCRIPTION} {SESSION_STRING}",
        },
        {
            "name": f"3 {MOCK_TODO_NAME}",
            "description": f"3 {MOCK_TODO_DESCRIPTION} {SESSION_STRING}",
        },
    ]

    for todo in todos:
        add_todo_item(session, project_id, todo)


def assign_todos_to_members_module(users: Dict[str, Dict[str, str]]) -> None:

    # Assign todo 1 to member1 and so on
    def assign_todo_to_member(
        session: requests.Session, project_id: str, todo_id: str, assignee_id: str
    ) -> None:
        response = session.post(
            f"{BASE_URL}/projects/assign-todo/{project_id}",
            json={"todo_id": todo_id, "assignee_id": assignee_id},
        )
        assert response.status_code == 200, f"Assign todo failed: {response.text}"

    # Get the exec user's team
    exec_session = login_session(users["exec"]["email"], users["exec"]["password"])
    resp = exec_session.get(f"{BASE_URL}/users/get-current-user-teams")
    assert resp.status_code == 200, f"Get exec teams failed: {resp.text}"

    team_id = resp.json()["teams"][0]["id"]

    # Get the team's project
    resp = exec_session.get(f"{BASE_URL}/teams/get-team/{team_id}")
    assert resp.status_code == 200, f"Get team failed: {resp.text}"

    project_id = resp.json()["team"]["project_ids"][0]

    # Get the project's todo items
    resp = exec_session.get(f"{BASE_URL}/projects/get-todo-items/{project_id}")
    assert resp.status_code == 200, f"Get project todos failed: {resp.text}"
    todos = resp.json()["todos"]

    # Get member user IDs
    member_user_ids = {}
    for member in ["member1", "member2", "member3"]:
        member_session = login_session(
            users[member]["email"], users[member]["password"]
        )
        resp = member_session.get(f"{BASE_URL}/users/get-current-user")
        assert resp.status_code == 200, f"Get {member} info failed: {resp.text}"
        member_user_ids[member] = resp.json()["user"]["id"]

    # Assign todos to members
    assign_todo_to_member(
        exec_session, project_id, todos[0]["id"], member_user_ids["member1"]
    )
    assign_todo_to_member(
        exec_session, project_id, todos[1]["id"], member_user_ids["member2"]
    )
    assign_todo_to_member(
        exec_session, project_id, todos[2]["id"], member_user_ids["member3"]
    )


def non_exec_members_create_todos_and_approval(
    users: Dict[str, Dict[str, str]],
) -> None:

    def add_todo_item(
        session: requests.Session, project_id: str, todo_data: Dict[str, str]
    ) -> None:
        response = session.post(
            f"{BASE_URL}/projects/add-todo/{project_id}",
            json=todo_data,
        )
        assert response.status_code == 200, f"Add todo failed: {response.text}"

    for member in ["member1", "member2", "member3"]:
        member_session = login_session(
            users[member]["email"], users[member]["password"]
        )

        # Get the user's team
        resp = member_session.get(f"{BASE_URL}/users/get-current-user-teams")
        assert resp.status_code == 200, f"Get user teams failed: {resp.text}"
        team_id = resp.json()["teams"][0]["id"]

        # Get the team's project
        resp = member_session.get(f"{BASE_URL}/teams/get-team/{team_id}")
        assert resp.status_code == 200, f"Get team failed: {resp.text}"

        project_id = resp.json()["team"]["project_ids"][0]

        # Create a todo item that will need approval by exec
        todo_data = {
            "name": f"{member} additional {MOCK_TODO_NAME}",
            "description": f"{member} additional {MOCK_TODO_DESCRIPTION} {SESSION_STRING}",
        }
        add_todo_item(member_session, project_id, todo_data)

    # Log into exec and check how many pending todos there are, should be 3
    exec_session = login_session(users["exec"]["email"], users["exec"]["password"])

    # Get team, get project id
    resp = exec_session.get(f"{BASE_URL}/users/get-current-user-teams")
    assert resp.status_code == 200, f"Get exec teams failed: {resp.text}"
    team_id = resp.json()["teams"][0]["id"]

    resp = exec_session.get(f"{BASE_URL}/teams/get-team/{team_id}")
    assert resp.status_code == 200, f"Get team failed: {resp.text}"

    project_id = resp.json()["team"]["project_ids"][0]

    resp = exec_session.get(f"{BASE_URL}/projects/get-proposed-todos/{project_id}")
    assert resp.status_code == 200, f"Get proposed todos failed: {resp.text}"
    assert (
        len(resp.json()["proposed_todos"]) == 2
    ), f"Expected 2 proposed todos, got {len(resp.json()['proposed_todos'])}"

    # Approve all proposed todos
    for todo in resp.json()["proposed_todos"]:
        resp_approve = exec_session.post(
            f"{BASE_URL}/projects/approve-todo/{project_id}/{todo['id']}",
        )
        assert (
            resp_approve.status_code == 200
        ), f"Approve todo failed: {resp_approve.text}"

    # Check again, should be 0 pending todos
    resp = exec_session.get(f"{BASE_URL}/projects/get-proposed-todos/{project_id}")
    assert resp.status_code == 200, f"Get proposed todos failed: {resp.text}"
    assert (
        len(resp.json()["proposed_todos"]) == 0
    ), f"Expected 0 proposed todos, got {len(resp.json()['proposed_todos'])}"

    # Get all todo ids for project, should be 6 now
    resp = exec_session.get(f"{BASE_URL}/projects/get-project/{project_id}")
    assert resp.status_code == 200, f"Get project failed: {resp.text}"
    assert (
        len(resp.json()["project"]["todo_ids"]) == 6
    ), f"Expected 6 todos in project, got {len(resp.json()['project']['todo_ids'])}"


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_end_to_end():

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

    others_join_team_module(users)
    print("Other users join team module completed successfully")

    promote_member_1_to_exec_module(users)
    print("Promote member 1 to exec module completed successfully")

    create_team_project_and_todos_module(users["exec"])
    print("Create team project and todos module completed successfully")

    assign_todos_to_members_module(users)
    print("Assign todos to members module completed successfully")

    non_exec_members_create_todos_and_approval(users)
    print(
        "Non-exec members create todos and exec approves module completed successfully"
    )

    print("End-to-end test completed successfully")
