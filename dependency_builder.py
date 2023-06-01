import datetime
from os import path

from sqlglot import parse_one, exp
from read_configuration_files import load_and_clean_configuration_files

class DependencyBuilder:

    def __init__(self) -> None:
        self._configuration_files = load_and_clean_configuration_files()
        pass

    
    def build_dependency_for_table(self, table_name):

        
        full_dependencies = self._build_dependency_recursively(table_name)
        dependency_tree = {
            table_name: full_dependencies
            }
        
        dependency_graph = f"{table_name}"
        dependency_graph += self._create_dependency_graph_as_string_recursively(dependency_tree.get(table_name))
        print(dependency_graph)
        self._print_dependency_to_file(table_name, dependency_graph)
        return
    

    def _create_dependency_graph_as_string_recursively(self, dependency_tree, curr_depth = 1):

        base_line = "     " * curr_depth
        base_line = f"\n{base_line[:-1]}|"

        dep_graph = ""
        for dep in dependency_tree:
            for table, dependencies in dep.items():
                # table = dep
                dep_graph += base_line
                dep_graph += f"{base_line}+ {table}"

                if dependencies:
                    dep_graph += self._create_dependency_graph_as_string_recursively(dependencies, curr_depth + 1)
        
        return dep_graph
    

    def _print_dependency_to_file(self, table_name, dependency_graph):

        curr_timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = path.join("output_files", f"{table_name}_{curr_timestamp}.txt")

        with open(file_name, "w") as file:
            file.write(dependency_graph)
            # file.writelines(dependency_graph)
    

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

        # For every entry, create the basic "SELECT ... FROM ... " query, as that is all that's needed to
        # extract the dependency tables
        for query_entry in table_data:
            table_query = f"""SELECT {query_entry.get("select")} FROM {query_entry.get("from")}"""
            dependencies = self.extract_dependency_tables_from_query(table_query)

            if not dependencies:
                return table_dependencies
            
            for dep in dependencies:
                curr_dependency = {
                    dep: self._build_dependency_recursively(dep)
                }
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
            where_is_space = table.find(' ')
            if where_is_space:
                table = table[:where_is_space]
            
            dependency_tables.append(table)

        return dependency_tables