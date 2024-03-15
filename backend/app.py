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
from .model.user import User
from .classes.object_id import PydanticObjectId

from bot.alia import find

from dotenv import load_dotenv
ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(ENV_PATH)

# Configure Flask & Flask-PyMongo:
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_BACK_URI")
pymongo = PyMongo(app)

# Get a reference to the recipes collection.
# Uses a type-hint, so that your IDE knows what's happening!
notes: Collection = pymongo.db.coursenotes
users: Collection = pymongo.db.users


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
        "notes": [CourseNote(**doc).to_json() for doc in cursor],
        "_links": links,
    }


@app.route("/notes/", methods=["POST"])
def new_notes():
    raw_note = request.get_json()
    # check if the note already exists
    fileHash = raw_note.get("file_hash")
    note_count = notes.count_documents({"file_hash": fileHash})
    if note_count > 0:
        note_doc = notes.find_one({"file_hash": fileHash})
        note = CourseNote(**note_doc)
        userid = f"{note.userid}, {raw_note.get("userid")}"
        note.userid = userid
        notes.update_one({"file_hash": fileHash}, {'$inc': {
            'userid': userid
        }})
        return note.to_json()

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

# Users section 
        
@app.route("/users/", methods=["POST"])
def new_user():
    raw_user = request.get_json()
    raw_user["added_dt"] = datetime.utcnow()

    note = User(**raw_user)
    insert_result = notes.insert_one(note.to_bson())
    note.id = PydanticObjectId(str(insert_result.inserted_id))
    #print(note)

    return note.to_json()

@app.route("/users/<string:phone>/notes", methods=["GET"])
def user_notes(phone):
    user = users.find_one_or_404({"phone": phone})
    
    parsedId = str(user.get('_id'))
    parsedId = parsedId.replace("'","").replace("ObjectId(", "").replace(")","")
    print("User Found: ", parsedId)
    regex = f'{parsedId}'
    print("User regex: ", regex)
    cursor = notes.find({"userid": {'$regex': regex}})

    return {
        "notes": [CourseNote(**doc).to_json() for doc in cursor],
    }


@app.route("/users/<string:phone>", methods=["GET"])
def get_user(phone):
    user = users.find_one_or_404({"phone": phone})
    return User(**user).to_json()


@app.route("/users/<string:phone>", methods=["PUT"])
def update_user(phone):
    user = User(**request.get_json())
    user.date_updated = datetime.utcnow()
    updated_doc = users.find_one_and_update(
        {"phone": phone},
        {"$set": user.to_bson()},
        return_document=ReturnDocument.AFTER,
    )
    if updated_doc:
        return User(**updated_doc).to_json()
    else:
        flask.abort(404, "note not found")


@app.route("/users/<string:phone>", methods=["DELETE"])
def delete_user(phone):
    deleted_note = users.find_one_and_delete(
        {"phone": phone},
    )
    if deleted_note:
        return User(**deleted_note).to_json()
    else:
        flask.abort(404, "note not found")

# ask url
@app.route("/ask", methods=["POST"])
def askbot():
    req = request.get_json()
    question = req.get("question")
    promotion = req.get("promotion")
    course = req.get("course")
    source = req.get("source")
    subject = req.get("subject")
    response  = find(query=question, promotion=promotion, course=course, source=source, subject=subject)
    # print("Response: ", response)
    return {
        "answer": str(response)
    }
    

if __name__ == "__main__":
    app.run(port=8000)