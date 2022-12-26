class UserTokens:
    def __init__(self) -> None:
        self.user_tokens_map = {}

    def get_is_login(self, user_id: int):
        return user_id in self.user_tokens_map

    def get_user_access_token(self, user_id: int):
        tokens = self.user_tokens_map.get(user_id)
        if tokens and "access_token" in tokens:
            return tokens["access_token"]

    def get_user_refresh_token(self, user_id: int):
        tokens = self.user_tokens_map.get(user_id)
        if tokens and "refresh_token" in tokens:
            return tokens["refresh_token"]

    def set_user_token(self, user_id: int, tokens: map) -> None:
        if not self.user_tokens_map.get(user_id):
            self.user_tokens_map[user_id] = {}

        if "access_token" in tokens:
            self.user_tokens_map[user_id]["access_token"] = tokens["access_token"]

        if "refresh_token" in tokens:
            self.user_tokens_map[user_id]["refresh_token"] = tokens["refresh_token"]

    def delete_user_token(self, user_id: int) -> None:
        del self.user_tokens_map[user_id]

    def verify_token(self, user_id: int, token: str, is_access_token: bool) -> bool:
        if not token:
            return False

        refresh_token = self.get_user_refresh_token(user_id)
        access_token = self.get_user_access_token(user_id)

        if not refresh_token and not access_token:
            return False

        if is_access_token:
            if access_token != token:
                return False
        else:
            if refresh_token != token:
                return False

        return True


user_tokens = UserTokens()
