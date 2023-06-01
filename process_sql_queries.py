from sqlglot import parse_one, exp

def extract_dependency_tables_from_query(query):

    # test_query = """
    # SELECT
    #     t.game_id, measurement_id, measurement_time, result_ball_flight, result_batter_dexterity, result_batter_walk_or_strikeout, result_hit_result, result_outs, result_pitch_result, result_pitch_type_auto, result_pitcher_dexterity, result_runs, situation_balls, situation_batter, situation_batting_team, situation_fielding_team, situation_inning, situation_outs, situation_pitcher, situation_strikes, tag_id, getdate() as date_processed
    # FROM
    #     scout.tags t inner join base.games g on t.game_id = g.game_id"""

    all_tables = parse_one(query).find_all(exp.Table)

    for table in all_tables:
        print(table)
        table_as_str = f"{table}"
        where_is_space = table_as_str.find(' ')
        if where_is_space:
            print(f"|{table_as_str[:where_is_space]}|")

    pass