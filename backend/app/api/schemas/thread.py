from pydantic import BaseModel


class ThreadResponse(BaseModel):
    thread_id: str
