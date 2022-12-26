from datetime import datetime, timedelta


def get_now():
    return datetime.now()


def get_expired_at(base_time: datetime, expire_minutes: int):
    return base_time + timedelta(minutes=expire_minutes)


def check_expired(expired_at: datetime) -> bool:
    if not expired_at or expired_at == None:
        return True

    if get_now() > expired_at:
        return True

    return False
