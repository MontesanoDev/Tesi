"""Durable at-most-once dispatch of one UI submission; never replay uncertain effects."""

import json

from fastapi import HTTPException

from app.db import connection


def lookup(project_id, request_id):
    with connection() as db:
        row = db.execute("SELECT state, response_json, payload_json FROM chat_submissions "
                         "WHERE project_id=? AND request_id=?", (project_id, request_id)).fetchone()
    if row is None:
        raise HTTPException(404, "Invio non ricevuto")
    return {"state": row["state"], "response": json.loads(row["response_json"] or "null"),
            "request": json.loads(row["payload_json"])}


def claim(project_id, payload):
    original = json.dumps(payload.model_dump(), sort_keys=True, ensure_ascii=False)
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        if not db.execute("SELECT 1 FROM projects WHERE id=?", (project_id,)).fetchone():
            raise HTTPException(404, "Progetto non trovato")
        row = db.execute("SELECT * FROM chat_submissions WHERE project_id=? AND request_id=?",
                         (project_id, payload.request_id)).fetchone()
        if row:
            if row["payload_json"] != original:
                raise HTTPException(409, "Identificativo di invio già usato per un altro messaggio")
            if row["state"] == "completed":
                return json.loads(row["response_json"])
            raise HTTPException(409, "Messaggio già ricevuto; verifica lo stato "
                                "della conversazione. L'invio non verrà applicato di nuovo.")
        db.execute("INSERT INTO chat_submissions(project_id,request_id,payload_json,state) "
                   "VALUES(?,?,?,'pending')", (project_id, payload.request_id, original))
    return None


def complete(db, project_id, request_id, response):
    if request_id:
        db.execute("UPDATE chat_submissions SET state='completed',response_json=?,turn_id=? "
                   "WHERE project_id=? AND request_id=? AND state='pending'",
                   (json.dumps(response, ensure_ascii=False), response["turn_id"],
                    project_id, request_id))


def interrupted(project_id, request_id):
    # A crash can occur after a session write and before its chat response. Keep
    # the original USER payload, never infer that the mutation can be repeated.
    with connection() as db:
        db.execute("UPDATE chat_submissions SET state='interrupted' "
                   "WHERE project_id=? AND request_id=? AND state='pending'",
                   (project_id, request_id))
