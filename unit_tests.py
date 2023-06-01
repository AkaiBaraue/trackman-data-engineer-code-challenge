from dependency_builder import DependencyBuilder
from read_configuration_files import load_and_clean_configuration_files

class Test_ConfigurationFiles:
    def test_all_config_files_loaded(self):
        configuration_files = load_and_clean_configuration_files()
        assert len(configuration_files) == 37

class Test_DependencyBuilder:

    def test_games_nulls_tree(self):
        self.db = DependencyBuilder()
        dependency_tree = self.db._build_dependency_tree_for_table("games.nulls")
        assert dependency_tree == {"games.nulls": [{"crosscheck.tags": [{"scout.tags": [{"base.tags": []}, {"dict.player_dedup": []}, {"dict.player_dedup": []}]}, {"base.games": []}]}]}

    def test_non_existing_table(self):
        self.db = DependencyBuilder()
        nonexisting_table = "silly.test"
        dependency_tree = self.db._build_dependency_tree_for_table(nonexisting_table)
        assert dependency_tree.get(nonexisting_table) == []