from read_configuration_files import load_and_clean_configuration_files
from process_sql_queries import extract_dependency_tables_from_query

config_data = load_and_clean_configuration_files()

test_table = "games.nulls"
