def mean(cursor, param: str):
    cursor.execute(f"""SELECT AVG({param}) AS avg_{param} FROM cats;""")
    return cursor.fetchone()[0]


def mediana(cursor, param: str):
    cursor.execute(
        f"""SELECT PERCENTILE_CONT(0.5) WITHIN GROUP
    (ORDER BY {param}) AS median_{param} FROM cats; """
    )
    return cursor.fetchone()[0]


def mode(cursor, param: str):
    cursor.execute(
        f"""SELECT {param} FROM(
                        SELECT {param}, COUNT(*) AS count_{param},
                        RANK() OVER(ORDER BY COUNT(*) DESC) AS rank
                        FROM cats GROUP BY {param}) AS ranked_{param}
                        WHERE rank = 1;"""
    )
    return cursor.fetchone()[0]
