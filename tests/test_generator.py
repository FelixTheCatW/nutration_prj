from pprint import pprint

from src.cli.data_generator import generate_data
from src.core.registries import COUNTRIES_MEALS_BY_TYPE, GLOBAL_MEALS_BY_TYPE


class TestGenerator:

    def test_registry(self):
        # print("COUNTRIES_MEALS_BY_TYPE")
        # pprint(COUNTRIES_MEALS_BY_TYPE, width=40, sort_dicts=False)
        # print("*" * 40)
        # print("GLOBAL_MEALS_BY_TYPE")
        # pprint(GLOBAL_MEALS_BY_TYPE, width=40, sort_dicts=False)
        pass

    def test_data_generation(self):
        items = generate_data()
        for i, p in enumerate(items):
            print("-" * 40)
            print(p[0])
            for index, pr in enumerate(p[1]):
                pprint(pr, width=180)
