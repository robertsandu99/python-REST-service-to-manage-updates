class HelloRepo:
    def get_name_by_person_id(self, person_id: int):
        if person_id == 0:
            return "World"

        return "John Doe"
