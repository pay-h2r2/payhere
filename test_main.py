import random
import string
import pytest

from constants.http_response_detail import *
from fastapi.testclient import TestClient
from fastapi import status
from main import app
from time import sleep

client = TestClient(app)

letters_set = string.ascii_letters
email = ''.join(random.sample(letters_set, 10)) + "@payhere.in"
other_email = ''.join(random.sample(letters_set, 10)) + "@payhere.in"
password = "p4yh2r2@"


def get_return_detail_format(message: str):
    return {"detail": message}


def get_jwt_header(token: str):
    return {'Authorization': 'Bearer {}'.format(token)}


def test_register_wrong_email_format():
    response = client.post(
        "/api/auth", json={"email": "wrongemail@@@eee.c", "password": password})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_NOT_AN_EMAIL_FORMAT)


def test_register_wrong_password_length():
    response = client.post(
        "/api/auth", json={"email": email, "password": "1"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_PASSWORD_MIN_LENGTH)


def test_register_success():
    response = client.post(
        "/api/auth", json={"email": email, "password": password})

    assert response.status_code == status.HTTP_201_CREATED

    response = client.post(
        "/api/auth", json={"email": other_email, "password": password})

    assert response.status_code == status.HTTP_201_CREATED


def test_register_integrity():
    response = client.post(
        "/api/auth", json={"email": email, "password": password})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_INTEGRITY)


def test_login_empty_body():
    response = client.post(
        "/api/auth/login")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_not_exist_account():
    response = client.post(
        "/api/auth/login", json={"email": "not_exist@payhere.in", "password": "wrongpassword"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_NOT_EXIST_ACCOUNT)


def test_login_wrong_password():
    response = client.post(
        "/api/auth/login", json={"email": email, "password": "wrongpassword"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_WRONG_PASSWORD)


def test_login_success():
    response = client.post(
        "/api/auth/login", json={"email": email, "password": password})

    assert response.status_code == status.HTTP_200_OK

    response_json_data = response.json()

    pytest.access_token = response_json_data["access_token"]
    pytest.refresh_token = response_json_data["refresh_token"]


def test_token_refresh():
    pytest.old_refresh_token = pytest.refresh_token
    # 바로 리프레시, 로그인 할 경우 토큰 겹칠 우려
    sleep(1)
    response = client.post(
        "/api/auth/refresh", headers=get_jwt_header(pytest.refresh_token))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_ACCESS_TOKEN_NOT_EXPIRED)

    response = client.post(
        "/api/auth/login", json={"email": email, "password": password})

    assert response.status_code == status.HTTP_200_OK

    response_json_data = response.json()

    pytest.access_token = response_json_data["access_token"]
    pytest.refresh_token = response_json_data["refresh_token"]


def test_token_refresh_old_token():
    response = client.post(
        "/api/auth/refresh", headers=get_jwt_header(pytest.old_refresh_token))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == get_return_detail_format(ERROR_OLD_TOKEN)


pytest.spent_amount = 100_000
pytest.memo = "Taxi"


def test_write_account_book_empty_body():
    response = client.post(
        "/api/account-books", headers=get_jwt_header(pytest.access_token))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_write_account_book_success():
    input_json_data = {
        "spent_amount": pytest.spent_amount,
        "memo": pytest.memo
    }

    response = client.post(
        "/api/account-books", json=input_json_data, headers=get_jwt_header(pytest.access_token))

    response_json_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert ("account_book_id" in response_json_data) == True

    pytest.account_book_id = response_json_data["account_book_id"]


def test_get_account_book_verify():
    response = client.post(
        "/api/auth/login", json={"email": other_email, "password": password})

    response_json_data = response.json()

    pytest.other_access_token = response_json_data["access_token"]
    pytest.other_refresh_token = response_json_data["refresh_token"]

    response = client.get(
        f"/api/account-books/{pytest.account_book_id}", headers=get_jwt_header(pytest.other_access_token))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_NOT_YOUR_DATA)


def test_get_account_book():
    response = client.get(
        f"/api/account-books/{pytest.account_book_id}", headers=get_jwt_header(pytest.access_token))

    response_json_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_json_data["memo"] == pytest.memo
    assert response_json_data["spent_amount"] == pytest.spent_amount


def test_duplicate_account_book_history():
    input_data = {
        "target_account_book_id": pytest.account_book_id
    }
    response = client.post(
        f"/api/account-books/duplicate", json=input_data, headers=get_jwt_header(pytest.access_token))

    assert response.status_code == status.HTTP_201_CREATED

    duplicated_account_book_id = response.json()["account_book_id"]

    response_duplicate = client.get(
        f"/api/account-books/{duplicated_account_book_id}", headers=get_jwt_header(pytest.access_token))

    response = client.get(
        f"/api/account-books/{pytest.account_book_id}", headers=get_jwt_header(pytest.access_token))

    response_json_data = response.json()
    response_duplicate_json_data = response_duplicate.json()

    assert response_duplicate_json_data["memo"] == response_json_data["memo"]
    assert response_duplicate_json_data["spent_amount"] == response_json_data["spent_amount"]


def test_update_account_book_history_verify():
    memo = "Black Taxi"

    response = client.patch(
        f"/api/account-books/{pytest.account_book_id}",  json={"memo": memo}, headers=get_jwt_header(pytest.other_access_token))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_NOT_YOUR_DATA)


def test_update_account_book_history():
    memo = "Black Taxi"

    response = client.patch(
        f"/api/account-books/{pytest.account_book_id}",  json={"memo": memo}, headers=get_jwt_header(pytest.access_token))

    assert response.status_code == status.HTTP_200_OK

    response = client.get(
        f"/api/account-books/{pytest.account_book_id}", headers=get_jwt_header(pytest.access_token))

    response_json_data = response.json()

    assert response_json_data["memo"] == memo
    assert response_json_data["spent_amount"] == pytest.spent_amount
    assert response_json_data["updated_at"] is not None


def test_delete_account_book_history_verify():
    response = client.delete(
        f"/api/account-books/{pytest.account_book_id}", headers=get_jwt_header(pytest.other_access_token))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_NOT_YOUR_DATA)


def test_delete_account_book_history():
    response = client.delete(
        f"/api/account-books/{pytest.account_book_id}", headers=get_jwt_header(pytest.access_token))

    assert response.status_code == status.HTTP_200_OK

    response = client.get(
        f"/api/account-books/{pytest.account_book_id}", headers=get_jwt_header(pytest.access_token))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_NOT_EXIST_DATA)


def test_get_account_book_all_histories():
    input_json_data = {
        "spent_amount": pytest.spent_amount,
        "memo": pytest.memo
    }

    for _ in range(5):
        client.post(
            "/api/account-books", json=input_json_data, headers=get_jwt_header(pytest.access_token))

    response = client.get(
        "/api/account-books", headers=get_jwt_header(pytest.access_token))

    response_json_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(response_json_data) == 6  # 5 +duplicate data(1)

    pytest.account_book_id = response_json_data[0]["id"]


def test_share_account_book_verify():
    input_data = {
        "account_book_id": pytest.account_book_id
    }
    response = client.post(
        f"/api/share", json=input_data, headers=get_jwt_header(pytest.other_access_token))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_NOT_YOUR_DATA)


def test_share_account_book():
    input_data = {
        "account_book_id": pytest.account_book_id,
    }
    response = client.post(
        f"/api/share", json=input_data, headers=get_jwt_header(pytest.access_token))

    response_json_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert ("entry_url" in response_json_data) == True
    assert ("expired_at" in response_json_data) == True

    pytest.entry_url = response_json_data["entry_url"]


def test_share_account_book_expired():
    input_data = {
        "account_book_id": pytest.account_book_id + 1,
        "expire_minutes": 10
    }
    response = client.post(
        f"/api/share", json=input_data, headers=get_jwt_header(pytest.access_token))

    response_json_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert ("entry_url" in response_json_data) == True
    assert ("expired_at" in response_json_data) == True


def test_enter_shared_account_book_url():
    # 다른 계정의 토큰으로 조회
    response = client.get(
        f"/api/account-books/{pytest.account_book_id}", headers=get_jwt_header(pytest.other_access_token))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_NOT_YOUR_DATA)

    # 공유한 계정의 토큰으로 조회
    response = client.get(
        f"/api/account-books/{pytest.account_book_id}", headers=get_jwt_header(pytest.access_token))

    assert response.status_code == status.HTTP_200_OK

    # 이후에 공유된 게시물과 비교하기위해
    # 공유자의 토큰으로 조회한 데이터를 저장
    origin_response_json_data = response.json()

    # 공유된 URL을 다른 계정으로 접속
    response = client.get(
        f"/api{pytest.entry_url}", headers=get_jwt_header(pytest.other_access_token), follow_redirects=False)

    assert response.status_code == status.HTTP_303_SEE_OTHER

    # referer 헤더로 공유된 게시물인지 비교.
    headers = get_jwt_header(pytest.other_access_token)
    headers["referer"] = f"http://localhost:8000/api{pytest.entry_url}"

    # 공유된 URL은 소유자의 인증을 거치지않음. (로그인은 필히 하여야함.)
    response = client.get(
        response.headers["Location"], headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == origin_response_json_data


# 조작된 referer 값으로 가계부 접속. (short_url 은 10자리의 대소문자 알파뱃 + 숫자로 조합되어있음.)
def test_access_account_book_with_manipulated_referer():
    headers = get_jwt_header(pytest.other_access_token)
    headers["referer"] = "http://localhost:8000/api/share/o3ie8vn3je"

    response = client.get(
        f"/api/account-books/{pytest.account_book_id}", headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_NOT_EXIST_DATA)

    input_json_data = {
        "spent_amount": pytest.spent_amount,
        "memo": pytest.memo
    }

    response = client.post(
        "/api/account-books", json=input_json_data, headers=get_jwt_header(pytest.other_access_token))

    assert response.status_code == status.HTTP_201_CREATED

    input_data = {
        "account_book_id": response.json()["account_book_id"],
    }
    response = client.post(
        f"/api/share", json=input_data, headers=get_jwt_header(pytest.other_access_token))

    assert response.status_code == status.HTTP_201_CREATED

    entry_url = response.json()["entry_url"]
    referer_link = f"http://localhost:8000/api{entry_url}"

    headers = get_jwt_header(pytest.other_access_token)
    headers["referer"] = referer_link

    response = client.get(
        f"/api/account-books/{pytest.account_book_id}", headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_ACCESS_DENIED)


def test_logout():
    response = client.post(
        "/api/auth/logout", headers=get_jwt_header(pytest.access_token))

    assert response.status_code == status.HTTP_200_OK

    response = client.post(
        "/api/auth/logout", headers=get_jwt_header(pytest.access_token))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == get_return_detail_format(ERROR_ALREADY_LOGOUT)

    response = client.get(
        f"/api/account-books/{pytest.account_book_id}", headers=get_jwt_header(pytest.access_token))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
