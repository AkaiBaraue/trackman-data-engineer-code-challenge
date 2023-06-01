# TrackMan Data Enigneer Code Challenge

This is my solution for the [TrackMan Data Engineering Code Challenge](http://codechallenge.trackmandata.com/). In this README file, I'll discuss the following things:

1. My [solution approach](#solution-approach)
2. The [output of the code](#output-of-the-code)
2. Some [extra thoughts](#extra-thoughts) I had while working on the challenge
3. How to [execute the code](#executing-the-code)

## Solution Approach

For my approach to this challenge, I identified the following steps that needed to be done:

1. Extract the configuration table files and understand how they're structured
2. Decide how to read and process the configuration files in code and verify that all the files are correctly read and processed
3. Figure out how to extract `schema.table` from the FROM part of the queries
4. Write the code to create the full dependency tree (as a data structure), given a `schema.table` as a starting point
5. Use the dependency tree to create a string representation of the dependency graph and save that to an output file

#### 1. Understanding the configuration files

The configuration files are fairly straight-forward to understand: There's a `schema` entry, a `table` entry, and a `query` entry.

The `schema` and `table` entry each contain the key `S`, with the value being the schema/table. The key is not relevant for the challenge and can be safely ignored.

The `query` entry contains the individual parts of the SQL query that make up the table. However, there's a slight difference in structure in the files. For some files, `query` entry contains a list (`L`) of dicts that represent the query (`M`). Other files (`rundown.location_history.json`) completely skip the `L` entry and go directly to the `M` entry. On top of that, some files (`games.metadata.json`) have an `aggregate` entry in the query, which also contains the `L` structure. The rest of the query parts do not have this `L` entry, they simply skip straight to the `S` mentioned for schema/table. These two things need to be kept in mind when reading and processing the files.

#### 2. Reading and processing configuration files

For the program itself, I decided to read the configuration files directly from the `tables.tar.gz` file. This way, if a new set of configuration files is provided, it's just one file that need to be replaced, which reduces the maintenance and cleanup load.

From the configuration files, I wanted to create a dictionary of the following format to make it easier to work with the data:

    {
        "games.nulls": {
            "select": " ... ",
            "from": " ... ",
            "where": " ... ",
        },
        "schema.table": ...
    }

For this challenge it is technically not necessary to extract anything other than the `FROM` part, but the additional time it took to get all the query parts was minimal, so I deemed it worth the time.

#### 3. Extract `schema.table` from the `FROM` parts

In order to build the dependencies, it's necessary to figure out which tables are referenced in the `FROM` part of a query. I decided to use the [SQLGlot](https://github.com/tobymao/sqlglot) package for this purpose, as it is a well-maintained package that provides tools for parsing and analyzing SQL queries. I could have developed the functionality to extract `table.schema` myself using Python's `.split()` function and some parsing, but it would have taken more time and at best provide the same reliability as SQLGlot.

With SQLGlot all I need to do it provide the query, which is easy to construct from the configuration files. If I had extracted just the `FROM` part of the configuration files, the query could have been a simple `SELECT * FROM <configuration_file_content>`, as the `SELECT` part is irrelevant for this challenge.

    for table in parse_one("SELECT * FROM x JOIN y JOIN z").find_all(exp.Table):
        print(table.name)

#### 4. Create the dependency tree

Once the configuration files and `schema.table` extraction were in place, creating the dependency tree was a simple process: Start with a table and find all its dependencies. For each of those dependencies, find any further dependencies recursively. Whenever an end is reached (a table that has no configuration files, and therefore no dependencies, is considered an end), start returning the data, structuring it as we go.

I could have built this without recursion, but the code would have been more complicated to read and understand.

#### 5. Creating the dependency graph

Once the dependency tree exists, the string representation of the graph can be created. Start from the top of the tree and recursively construct a string that represents the full dependency graph, indenting the dependency tables based on their depth in the tree. This graph is then written to a .txt file.

## Output of the code

All the output graphs can be found in the [output_files](/output_files/) folder.

## Extra Thoughts

#### Reading of the configuration files

When it comes to reading the configuration files, I thought about a couple of points:

1. Should I extract the configuration files to a folder and read them from there, or simply read directly from the `.tar.gz` file?

As mentioned [above](#2-reading-and-processing-configuration-files), I decided to read directly from the `.tar.gz` file, as I felt this is easier to maintain. It means fewer files that have to be structured in folders, which I prefer for this challenge.

However, this also means replacing the entire `.tar.gz` file every time a change is made to a configuration file. For this challenge that is not an issue, but for a live environment, it might be easier to have the configuration files extracted, so only the changed files can be replaced.

2. Should all configuration files be read on initialization, or should they be read only when needed?

For this challenge, it honestly doesn't matter much. I decided to read and process all configuration files at once, as I wanted to verify that all the files were handled properly. However, with enough configuration files and if sytem memory is a limitation, it would make more sense to only read the configuration files as they're needed. This reduces the total files to hold in memory (unless _all_ graphs have to be generated), but also introduces a slightly longer run-time when requesting a graph, as files have to be read and processed regularly.

#### Testing

Since the scope of this challenge is narrow, I have done a lot of manual testing and verification during development. I have written a few unit tests, which can be found in [unittests.py](unit_tests.py), but for a production implementation, more test cases should be covered by unit tests.

## Executing the code

1. Make sure to use Python 3.9 or higher
2. Create a virtual environment and activate it
3. Install the required packages (`pip install -r requirements.txt`)
4. In the terminal, execute `main.py "schema.table"`, replacing `schema.table` with the schema/table you want to build a graph for. Multiple `schema.table` can be provided after each other (`main.py "schema1.table1" "schema2.table2" "schema3.table3"`). The output is saved to a .txt file in `output_files/`
    * Alternatively: Simply execute `main.py` and dependency graphs will be generated for all configuration files.