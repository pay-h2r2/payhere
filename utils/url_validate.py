from constants.short_url_setting import SHORT_URL_LENGTH


def check_verify_short_url_referer(short_url: str) -> bool:
    if len(short_url) != SHORT_URL_LENGTH:
        return False

    return True


def check_from_redirect(route_url: str) -> bool:
    if route_url == "share":
        return True

    return False
