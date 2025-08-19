from fastapi import APIRouter, Depends, HTTPException, status
from Backend.utils import getCurrentUser
from Backend.database import journal_collection
from Backend.schema import JournalEntryIn, JournalEntryOut, serializeJournal
from datetime import datetime, timezone
from uuid import uuid4

journal_router = APIRouter(prefix="/journal", tags=["journals"])


@journal_router.get("/history")
async def journal_history(current_user: dict = Depends(getCurrentUser)):
    if journal_collection is None:
        raise HTTPException(status_code=500, detail="DB connection not initialized.")

    user_id = current_user['id']
    cursor = journal_collection.find({'user_id': user_id}).sort('timeStamp', -1)
    journals = await cursor.to_list(length=None)

    return {
        'journal_history': [serializeJournal(j) for j in journals]
    }


@journal_router.post("/", response_model=JournalEntryOut, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(entry: JournalEntryIn, current_user: dict = Depends(getCurrentUser)):
    if journal_collection is None:
        raise HTTPException(status_code=500, detail="DB connection not initialized.")

    timeStamp = datetime.now(timezone.utc).timestamp()
    journal_id = str(uuid4())

    journal_doc = {
        'journal_id': journal_id,
        'user_id': current_user['id'],
        'field1': entry.field1,
        'field2': entry.field2,
        'field3': entry.field3,
        'field4': entry.field4,
        'timeStamp': timeStamp
    }

    result = await journal_collection.insert_one(journal_doc)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create journal entry.")

    return serializeJournal(journal_doc)


@journal_router.get("/{journal_id}", response_model=JournalEntryOut)
async def get_journal_entry(journal_id: str, current_user: dict = Depends(getCurrentUser)):
    if journal_collection is None:
        raise HTTPException(status_code=500, detail="DB connection not initialized.")

    journal = await journal_collection.find_one({
        'journal_id': journal_id,
        'user_id': current_user['id']
    })

    if not journal:
        raise HTTPException(status_code=404, detail="Journal entry not found.")

    return serializeJournal(journal)
