from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class UserInfo(BaseModel):
    first_name: str
    last_name: str
    phone_number: Optional[str] 
    username: Optional[str] 
    district: Optional[str]




class OrderItemInfo(BaseModel):
    product_name: str
    count: float

    class Config:
        from_attributes = True


class DmttInfo(BaseModel):
    name: str
    user_id: int
    user:Optional[UserInfo]
    address: str
    stir: str
    child_count: int = 0
    is_active: bool = True


class CompanyInfo(BaseModel):
    """
        Base model for common attributes of a company.
    """
    name: str
    address: str
    phone_number: str
    stir: str
    is_active: Optional[bool]


class OrderResponse(BaseModel):
    id: int
    dmtt: Optional[DmttInfo]
    company: Optional[CompanyInfo]
    order_status: str
    datetime: Optional[datetime]
    items: List[OrderItemInfo]

    class Config:
        from_attributes = True
