from fastapi import Depends

from ..repositories.hello_repo import HelloRepo


class HelloSrv:

    _repo: HelloRepo

    def __init__(self, repo: HelloRepo = Depends(HelloRepo)):
        self._repo = repo

    def say_hello(self, person_id: int):
        return f"Hello, {self._repo.get_name_by_person_id(person_id)}!"
