"""
Bot API - A small API for managing course notes.
"""

from datetime import datetime
import os

from pymongo.collection import Collection, ReturnDocument

import flask
from flask import Flask, request, url_for, jsonify
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError

from .model.course_note import CourseNote
from .classes.object_id import PydanticObjectId

from dotenv import load_dotenv
ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(ENV_PATH)

# Configure Flask & Flask-PyMongo:
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
pymongo = PyMongo(app)

# Get a reference to the recipes collection.
# Uses a type-hint, so that your IDE knows what's happening!
notes: Collection = pymongo.db.coursenotes
users: Collection = pymongo.db.users
usernotes: Collection = pymongo.db.usernotes


@app.errorhandler(404)
def resource_not_found(e):
    """
    An error-handler to ensure that 404 errors are returned as JSON.
    """
    return jsonify(error=str(e)), 404


@app.errorhandler(DuplicateKeyError)
def resource_not_found(e):
    """
    An error-handler to ensure that MongoDB duplicate key errors are returned as JSON.
    """
    return jsonify(error=f"Duplicate key error."), 400


@app.route("/notes/")
def list_notes():
    """
    GET a list of course notes.

    The results are paginated using the `page` parameter.
    """

    page = int(request.args.get("page", 1))
    per_page = 10  # A const value.

    # For pagination, it's necessary to sort by name,
    # then skip the number of docs that earlier pages would have displayed,
    # and then to limit to the fixed page size, ``per_page``.
    cursor = notes.find().sort("title").skip(per_page * (page - 1)).limit(per_page)

    notes_count = notes.count_documents({})

    links = {
        "self": {"href": url_for(".list_notes", page=page, _external=True)},
        "last": {
            "href": url_for(
                ".list_notes", page=(notes_count // per_page) + 1, _external=True
            )
        },
    }
    # Add a 'prev' link if it's not on the first page:
    if page > 1:
        links["prev"] = {
            "href": url_for(".list_notes", page=page - 1, _external=True)
        }
    # Add a 'next' link if it's not on the last page:
    if page - 1 < notes_count // per_page:
        links["next"] = {
            "href": url_for(".list_notes", page=page + 1, _external=True)
        }

    return {
        "recipes": [CourseNote(**doc).to_json() for doc in cursor],
        "_links": links,
    }


@app.route("/notes/", methods=["POST"])
def new_notes():
    raw_note = request.get_json()
    raw_note["added_dt"] = datetime.utcnow()

    note = CourseNote(**raw_note)
    insert_result = notes.insert_one(note.to_bson())
    note.id = PydanticObjectId(str(insert_result.inserted_id))
    #print(note)

    return note.to_json()


@app.route("/notes/<string:slug>", methods=["GET"])
def get_note(slug):
    note = notes.find_one_or_404({"slug": slug})
    return CourseNote(**note).to_json()


@app.route("/notes/<string:slug>", methods=["PUT"])
def update_note(slug):
    note = CourseNote(**request.get_json())
    note.date_updated = datetime.utcnow()
    updated_doc = note.find_one_and_update(
        {"slug": slug},
        {"$set": note.to_bson()},
        return_document=ReturnDocument.AFTER,
    )
    if updated_doc:
        return CourseNote(**updated_doc).to_json()
    else:
        flask.abort(404, "note not found")


@app.route("/notes/<string:slug>", methods=["DELETE"])
def delete_note(slug):
    deleted_note = notes.find_one_and_delete(
        {"slug": slug},
    )
    if deleted_note:
        return CourseNote(**deleted_note).to_json()
    else:
        flask.abort(404, "note not found")

if __name__ == "__main__":
    app.run(port=8000, debug=True)