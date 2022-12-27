import re
import chardet
import sqlite3
from sqlite3 import Error
from flask import request
from flask import Flask, jsonify
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from

app = Flask(__name__)

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info={
        "title": LazyString(lambda: "Text and File Cleansing"),
        "version": LazyString(lambda: "1.0.0"),
        "description": LazyString(
            lambda: "Full API Documentation for Text and File Cleansing with Flask"
        ),
    },
    host=LazyString(lambda: request.host),
)

swagger_config = {
    "headers": [],
    "specs": [{"endpoint": "docs", "route": "/docs.json"}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)


@swag_from("docs/text.yml", methods=["POST"])
@app.route("/text", methods=["POST"])
def text_cleansing():
    text = request.form.get("text")

    conn = create_connection("text_cleansed_data")

    create_table(conn, "text_cleansed_data")

    cursor = conn.cursor()
    cursor.execute("INSERT INTO text_cleansed_data (content) VALUES (?)", (text,))

    conn.commit()
    conn.close()

    res = {
        "status_code": 200,
        "description": "Cleansed Text Result",
        "data": re.sub(r"[^a-zA-Z0-9]", " ", text),
    }

    res_json = jsonify(res)
    return res_json


@swag_from("docs/file.yml", methods=["POST"])
@app.route("/file", methods=["POST"])
def file_cleansing():
    file = request.files.getlist('file')[0]
    file_content = file.read()
    encoding = chardet.detect(file_content)["encoding"]
    file_content = file_content.decode(encoding)
    cleansed_file_content = re.sub(r"[^a-zA-Z0-9]", " ", file_content)

    conn = create_connection("file_cleansed_data")

    create_table(conn, "file_cleansed_data")

    cursor = conn.cursor()
    cursor.execute("INSERT INTO file_cleansed_data (content) VALUES (?)", (cleansed_file_content,))

    conn.commit()
    conn.close()

    cleansed_file_csv = open("file_cleansed_data.csv", "w")
    cleansed_file_csv.write(cleansed_file_content)

    res = {
        "status_code": 200,
        "description": "Cleansed File Result",
        "data": cleansed_file_content,
    }

    res_json = jsonify(res)
    return res_json

def create_connection(path):
    conn = None
    try:
        conn = sqlite3.connect("db/{}.db".format(path))
    except Error as e:
        print(e)

    return conn

def create_table(conn, table):
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS {} (content TEXT NOT NULL)".format(table)
    )



if __name__ == "__main__":
    app.run()
