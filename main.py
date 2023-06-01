import json
from dependency_builder import DependencyBuilder

dep_builder = DependencyBuilder()

test_table = "games.nulls"
tree = dep_builder.build_dependency_for_table(test_table)

print(json.dumps(tree, indent=4))