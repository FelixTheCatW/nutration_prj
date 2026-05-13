from src.core.Person import Person, random_person

class TestUser:
    """Verify User creation and field correctness"""
    def test_random_person(self):
        user = random_person(1, "ru_RU")
        print(user)
        assert user and user.name and user.gender and user.weight_kg and user.height_cm and user.age and user.goal
        assert user.user_id == 1