from utils.random import random_url_generator
from utils.user_tokens import user_tokens
from utils.url_validate import check_from_redirect, check_verify_short_url_referer
from utils.hash import check_password_hash, create_password_hash, create_random_salt
from utils.email_validate import is_email
from utils.date import check_expired, get_expired_at, get_now


def test_date():
    now = get_now()
    expired_at = get_expired_at(now, 1)

    assert check_expired(expired_at) == False
    expired_at = now
    assert check_expired(expired_at) == True


def test_email_validate():
    assert is_email("test@payhere.in") == True
    assert is_email("test@@payhere.in") == False


def test_hash():
    password = "p4yh2r2#)$"
    wrong_password = "p4yh32r2#)$"
    salt = create_random_salt()
    hashed_password = create_password_hash(password, salt)

    assert check_password_hash(password, hashed_password) == True
    assert check_password_hash(wrong_password, hashed_password) == False


def test_url_validte():
    assert check_from_redirect("share") == True
    assert check_from_redirect("sharw") == False
    assert check_verify_short_url_referer("9r9r9e8w8q") == True
    assert check_verify_short_url_referer("") == False


def test_random_generator():
    random_str = random_url_generator.generate_random_str()

    assert len(random_str) == random_url_generator.url_length

    random_url_generator.url_length = 20
    random_str = random_url_generator.generate_random_str()

    assert len(random_str) == random_url_generator.url_length

    random_url_generator.url_length = 10


def test_user_tokens():
    user_id = 1
    assert user_tokens.get_is_login(user_id) == False
    dummy_token_data = {"access_token": "dummy token",
                        "refresh_token": "dummy_refresh_token"}
    user_tokens.set_user_token(user_id, dummy_token_data)

    assert user_tokens.get_user_access_token(
        user_id) == dummy_token_data["access_token"]
    assert user_tokens.get_user_refresh_token(
        user_id) == dummy_token_data["refresh_token"]

    assert user_tokens.verify_token(
        user_id, dummy_token_data.get("access_token"), True) == True
    assert user_tokens.verify_token(
        user_id, dummy_token_data.get("refresh_token"), False) == True
    assert user_tokens.verify_token(
        user_id, dummy_token_data.get("refresh_token"), True) == False

    user_tokens.delete_user_token(user_id)

    assert user_tokens.get_is_login(user_id) == False
