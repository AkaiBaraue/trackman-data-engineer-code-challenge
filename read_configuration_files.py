import tarfile
import json

def load_and_clean_configuration_files():

    # The final loaded data
    loaded_data = {}

    tar = tarfile.open("tables.tar.gz")
    for member in tar.getmembers():
        f = tar.extractfile(member)

        if f is None:
            continue

        table_data = json.loads(f.read())

        schema_table_key = f"""{table_data.get("schema").get("S")}.{table_data.get("table").get("S")}"""

        # The query in most files is structured as follows:                             {"query": {"L": [{"M": {"from": {"S": " ... "}, "select": {"S": " ... "} } } ] }
        # HOWEVER, a few files do not have the "L" entry, and are instead as follows:   {"query": {"M": {"from": {"S": " ... "}, "select": {"S": " ... "} } }
        # In order to treat them the same, load any instances without "L" as a list anyway, so they can be treated the same
        query_data = table_data.get("query").get("L", [table_data.get("query")])

        # Simplify the queries a bit, getting rid of all the "L", "M", and "S" keys
        # NOTE: Every configuration file only has one query, so technical it's not necessary to iterate over the list, but
        # I'm doing it future-proof the process a bit.
        cleaned_up_queries = []
        for query in query_data:
            processed_query = {}

            for k, v in query.get("M").items():
                _value = v.get("L", [v])[0].get("S")
                processed_query[k] = _value
                pass

            cleaned_up_queries.append(processed_query)


        # Save the list of queries to the schema.table key
        loaded_data[schema_table_key] = cleaned_up_queries

    return loaded_data