from pydantic import BaseModel


class StandardBase(BaseModel):
    is_number: str
    title: str
    category: str
    description: str | None = None
    status: str = "Active"


class StandardResponse(StandardBase):
    id: int

    class Config:
        from_attributes = True