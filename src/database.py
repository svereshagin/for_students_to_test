import psycopg2
from psycopg2 import pool
from typing import Optional, Any, List, Tuple, Dict
from src.database_math import mean, mediana, mode
from src.config import DB_CONFIG


valid_attributes: List[str] = ["name", "color", "tail_length", "whiskers_length"]

POOL = psycopg2.pool.SimpleConnectionPool(1,10,  database=DB_CONFIG["dbname"],
                                          user=DB_CONFIG["user"], password=DB_CONFIG["password"],
                                          port=DB_CONFIG["port"], host=DB_CONFIG["host"])

def save_stats(
    cursor,
    stats: Tuple[float, float, List[float], float, float, List[float]]
) -> None:
    with cursor:
        cursor.execute(
            """
        INSERT INTO cats_stat(
            tail_length_mean, tail_length_median, tail_length_mode,
            whiskers_length_mean, whiskers_length_median, whiskers_length_mode
        ) VALUES (
            %s, %s, %s, %s, %s, %s
        )
        """,
        stats,
        )


def table_exists(table_name: str) -> bool:
    conn = POOL.getconn()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_name = %s
                    );
                    """,
                    (table_name,),
                )
    finally:
        POOL.putconn(conn)
    return cursor.fetchone()[0]


def cat_colors_create_data() -> None:
    conn = POOL.getconn()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                cursor.execute("DELETE FROM cat_colors_info")
                cursor.execute(
                    """
                    INSERT INTO cat_colors_info (color, count)
                    SELECT color, COUNT(*)
                    FROM cats
                    GROUP BY color
                """
                )
    finally:
        POOL.putconn(conn)


def fullfill_cat_options() -> None:
    conn = POOL.getconn()
    try:
        with conn:
            with conn.cursor() as cursor:
                tail_length_mean: float = mean(cursor, "tail_length")
                tail_length_median: float = mediana(cursor, "tail_length")
                tail_length_mode: float = mode(cursor, "tail_length")

                whiskers_length_mean: float = mean(cursor, "whiskers_length")
                whiskers_length_median: float = mediana(cursor, "whiskers_length")
                whiskers_length_mode: float = mode(cursor, "whiskers_length")

                cursor.execute("DELETE FROM cats_stat")

                save_stats(
                    cursor,
                    (
                        tail_length_mean,
                        tail_length_median,
                        [tail_length_mode],
                        whiskers_length_mean,
                        whiskers_length_median,
                        [whiskers_length_mode],
                    ),
                )
    finally:
        POOL.putconn(conn)


def add_info_db(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    conn = POOL.getconn()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM cats WHERE name = %s", (data["name"],))
                existing_cat: Optional[Tuple[str]] = cursor.fetchone()

                if existing_cat:
                    return ({"error": "Cat already exists"}, 409)

                cursor.execute(
                    """
                        INSERT INTO cats (name, color, tail_length, whiskers_length)
                        VALUES (%s, %s, %s, %s)
                    """,
                    (
                        data["name"],
                        data["color"],
                        data["tail_length"],
                        data["whiskers_length"],
                    ),
                )
                return ({"message": "Cat added successfully"}, 201)

    except Exception as e:
        return ({"error": str(e)}, 500)

    finally:
        POOL.putconn(conn)


def get_parsed_data(attribute: str, order: str, offset: int, limit: int) -> tuple[dict[str, str], int] | tuple[
    dict[str, str], int] | tuple[dict[str, str], int] | tuple[list[dict[str, Any]], int] | tuple[dict[str, str], int]:
    if attribute not in valid_attributes:
        return ({"error": "Invalid attribute"}, 400)
    if order not in ["asc", "desc"]:
        return ({"error": "Invalid order"}, 400)
    conn = POOL.getconn()
    db_request: str = f"""
                SELECT name, color, tail_length, whiskers_length
                FROM cats
                ORDER BY {attribute} {order}
                OFFSET %s LIMIT %s
                """
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(db_request, (offset, limit))
                cats: List[Tuple[str, str, float, float]] = cursor.fetchall()
                if not cats:
                    return ({"error": "No cats found"}, 404)

                data: List[Dict[str, Any]] = [
                    {
                        "name": cat[0],
                        "color": cat[1],
                        "tail_length": cat[2],
                        "whiskers_length": cat[3],
                    }
                    for cat in cats
                ]
                return (data, 200)
    except Exception as e:
        return ({"error": str(e)}, 500)
    finally:
        POOL.putconn(conn)
