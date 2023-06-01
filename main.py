import sys

if __name__ == "__main__":

    from dependency_builder import DependencyBuilder

    dep_builder = DependencyBuilder()

    arguments = sys.argv[1:]
    # If arguments have been provided in the command line, create graphs for only the given tables
    if arguments:
        for table_name in arguments:
            dep_builder.process_table_and_save_graph(table_name)

    # Otherwise create graphs for all the configuration files
    else:
        for table_key in dep_builder._configuration_files.keys():
            dep_builder.process_table_and_save_graph(table_key)
