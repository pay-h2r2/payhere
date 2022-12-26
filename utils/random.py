import string
import random


class RandomUrlGenerator:
    def __init__(self) -> None:
        self.letters = string.ascii_letters + string.digits
        self.__url_length = 10

    def generate_random_str(self):
        return ''.join(random.sample(self.letters, self.__url_length))

    @property
    def url_length(self) -> int:
        return self.__url_length

    @url_length.setter
    def url_length(self, value: int) -> None:
        self.__url_length = value


random_url_generator = RandomUrlGenerator()
