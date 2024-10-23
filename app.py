from typing import Any, Tuple, Dict
from src.database import (
    cat_colors_create_data,
    fullfill_cat_options,
    add_info_db,
    get_parsed_data,
)
from flask import Flask, request, jsonify, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import BaseModel, Field, ValidationError

app_name = "Cats Service"
app = Flask(__name__)
limiter = Limiter(
    app=app, key_func=get_remote_address, default_limits=["600 per minute"]
)

class Cat(BaseModel):
    name: str = Field(min_length=1)
    color: str = Field(min_length=1)
    tail_length: int = Field(gt=0)
    whiskers_length: int = Field(gt=0)

@app.route("/ping", methods=["GET"])
def ping() -> Tuple[str, int]:
    return f"{app_name}. Version 0.1", 200


@app.route("/cats", methods=["GET"])
@limiter.limit("600 per minute")
def data_parser() -> tuple[Response, int]:
    attribute = request.args.get("attribute", default="name")
    order = request.args.get("order", default="asc")
    offset = request.args.get("offset", default=0, type=int)
    limit = request.args.get("limit", default=10, type=int)

    result: Tuple[Dict[str, str], int] = get_parsed_data(attribute, order, offset, limit)
    return jsonify(result[0]), result[1]


@app.route("/cat", methods=["POST"])
def add_info() -> tuple[dict[str, str], int] | tuple[Response, int]:
    try:
        data_cats = Cat(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    result: Tuple[Dict[str, Any], int] = add_info_db(data_cats.dict())
    return jsonify(result[0]), result[1]


if __name__ == "__main__":
    cat_colors_create_data()
    fullfill_cat_options()

