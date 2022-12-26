from datetime import datetime


def get_short_url_return_data(short_url: str, expired_at: datetime):
    return {
        "entry_url": f"/share/{short_url}",
        "expired_at": expired_at
    }
