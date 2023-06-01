from dependency_builder import DependencyBuilder
from read_configuration_files import load_and_clean_configuration_files


class Test_ConfigurationFiles:
    def test_all_config_files_loaded(self):
        """Verifies that all config files are loaded"""

        configuration_files = load_and_clean_configuration_files()
        assert len(configuration_files) == 37


class Test_DependencyBuilder:
    def test_games_nulls_tree(self):
        """Verifies that the tree returned for "games.nulls" is as expected based on the files."""

        self.db = DependencyBuilder()
        dependency_tree = self.db._build_dependency_tree_for_table("games.nulls")
        assert dependency_tree == {
            "games.nulls": [
                {
                    "crosscheck.tags": [
                        {
                            "scout.tags": [
                                {"base.tags": []},
                                {"dict.player_dedup": []},
                                {"dict.player_dedup": []},
                            ]
                        },
                        {"base.games": []},
                    ]
                }
            ]
        }

    def test_games_nulls_graph(self):
        """Verifies that the dependency graph generated for "games.nulls" contains all the expected lines."""

        self.db = DependencyBuilder()
        table_name = "games.nulls"
        dependency_tree = self.db._build_dependency_tree_for_table(table_name)
        dependency_graph = self.db._create_dependency_graph_as_string(
            table_name, dependency_tree
        )

        # For the graph, these are the lines that are expected ot be generated
        lines_to_find = [
            "games.nulls",
            "    |",
            "    |+ crosscheck.tags",
            "        |",
            "        |+ scout.tags",
            "            |",
            "            |+ base.tags",
            "            |",
            "            |+ dict.player_dedup",
            "            |",
            "            |+ dict.player_dedup",
            "        |",
            "        |+ base.games",
        ]

        # Split the graph into a list and iterate over it, removing one of the expected lines if a match is found.
        dependency_graph_split = dependency_graph.split("\n")
        for line in dependency_graph_split:
            index = lines_to_find.index(line)
            lines_to_find.pop(index)

        # Once all the lines from the generated graph have been processed and matched, there should be 0 lines left to find
        assert len(lines_to_find) == 0

    def test_non_existing_table(self):
        """Verifies that an empty dependency tree is generated for non-existing tables."""

        self.db = DependencyBuilder()
        nonexisting_table = "silly.test"
        dependency_tree = self.db._build_dependency_tree_for_table(nonexisting_table)
        assert dependency_tree.get(nonexisting_table) == []
