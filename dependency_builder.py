import datetime
from os import path

from sqlglot import parse_one, exp
from read_configuration_files import load_and_clean_configuration_files


class DependencyBuilder:
    def __init__(self) -> None:
        self._configuration_files = load_and_clean_configuration_files()
        pass

    def process_table_and_save_graph(self, table_name):
        """Runs the entire dependency process and saves the graph to an output file.

        Args:
            table_name (str): The name of the table to build a dependency graph for
        """

        dependency_tree = self._build_dependency_tree_for_table(table_name)

        dependency_graph = self._create_dependency_graph_as_string(table_name, dependency_tree)

        # Print the dependency tree to a .txt file
        self._print_dependency_graph_to_file(table_name, dependency_graph)

    def _create_dependency_graph_as_string(self, table_name, dependency_tree):
        """Creates the string representation of the dependency graph, based on the given dependency tree.

        Args:
            table_name (str): The name of the table to build the graph for
            dependency_tree (dict): A dictionary that represents the dependency tree for the table

        Returns:
            str: A string representation of the dependency graph
        """        
        
        dependency_graph = f"{table_name}"

        # Use the recursive function to build the entire graph
        dependency_graph += self._create_dependency_graph_as_string_recursively(
            dependency_tree.get(table_name)
        )

        return dependency_graph

    def _create_dependency_graph_as_string_recursively(
        self, dependency_tree, curr_depth=1
    ):
        """Recursively builds strings that represent the dependency graph.

        Args:
            dependency_tree (dict): The dependency tree for the current level of the graph
            curr_depth (int, optional): The current depth of the graph. Defaults to 1.

        Returns:
            str: A string representing the dependency graph from the current point and down.
        """

        # Indent the graph based on the current depth
        base_line = "    " * curr_depth
        base_line = f"\n{base_line}|"

        dep_graph = ""
        # Build the string representing the current level, recursively calling this function to get deeper levels
        for dep in dependency_tree:
            for table, dependencies in dep.items():
                dep_graph += base_line
                dep_graph += f"{base_line}+ {table}"

                if dependencies:
                    dep_graph += self._create_dependency_graph_as_string_recursively(
                        dependencies, curr_depth + 1
                    )

        return dep_graph

    def _print_dependency_graph_to_file(self, table_name, dependency_graph):
        """Writes the given dependency graph to a .txt file

        Args:
            table_name (str): The name of the table the graph belongs to.
            dependency_graph (str): A string representing the full dependency graph
        """

        curr_timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = path.join("output_files", f"{table_name}_{curr_timestamp}.txt")

        with open(file_name, "w") as file:
            file.write(dependency_graph)

    def _build_dependency_tree_for_table(self, table_name):
        """Builds the full dependency tree for the given table

        Args:
            table_name (str): The name of the table to build a dependency tree for

        Returns:
            dict: A dictionary representing the full dependency tree.
        """

        # Create the dependency tree for the given table
        full_dependencies = self._build_dependency_recursively(table_name)
        dependency_tree = {table_name: full_dependencies}
        
        return dependency_tree

    def _build_dependency_recursively(self, table_name):
        """Recursively builds the dependency tree from the given table and down

        Args:
            table_name (str): The name of the table to build dependencies for

        Returns:
            list: A list of dictionaries, where each key is a table dependency, and the value is a list of that dependency's dependencies.
        """

        table_dependencies = []

        # Get the configuration data for the given table
        table_data = self._configuration_files.get(table_name)

        # If no data exists, it's the end of the chain, so stop building further
        if not table_data:
            return table_dependencies

        # For every entry, create the basic "SELECT ... FROM ... " query, as that is all SQLGlot needs to
        # extract the dependency tables.
        # The "SELECT" part could really be "SELECT *" for the purpose of this exercise, but might as well use
        # the actual statement from the file as it's been loaded.
        for query_entry in table_data:
            table_query = (
                f"""SELECT {query_entry.get("select")} FROM {query_entry.get("from")}"""
            )
            dependencies = self.extract_dependency_tables_from_query(table_query)

            if not dependencies:
                return table_dependencies

            # For each dependency, recursively call this function to build their dependencies
            for dep in dependencies:
                curr_dependency = {dep: self._build_dependency_recursively(dep)}
                table_dependencies.append(curr_dependency)

        return table_dependencies

    def extract_dependency_tables_from_query(self, query):
        """Extracts the dependency tables from the FROM part of the given query

        Args:
            query (str): The query to process

        Returns:
            list: A list of the dependency tables in the format schema.table
        """

        # Use sqlglot to extract all the tables from the query
        all_tables = parse_one(query).find_all(exp.Table)

        # The tables extracted may contain their alias ("crosscheck.tags t"), so strip it down to just the schema.table part
        dependency_tables = []
        for table_unprocessed in all_tables:
            table = f"{table_unprocessed}"

            # If tables have an alias, slice the string to get rid of the alias.
            where_is_space = table.find(" ")
            if where_is_space:
                table = table[:where_is_space]

            dependency_tables.append(table)

        return dependency_tables
