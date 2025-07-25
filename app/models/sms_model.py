from pydantic import BaseModel, Field


class SMSModel(BaseModel):
    student_id: str = Field(..., description="學生學號")
    recipient: str = Field(..., description="收件人姓名")
    phone_number: str = Field(..., description="手機號碼")
    message_content: str = Field(..., description="簡訊內容")
    send_time: str | None = Field(None, description="預約發送時間")
    model_config = {"from_attributes": True}
