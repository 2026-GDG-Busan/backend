from pydantic import BaseModel

class WakeUpRequest(BaseModel):
    user_id: str
    volume: float
    is_praying: bool
    is_popup_active: bool = False # 민원 팝업이 떠 있는지 여부 추가
