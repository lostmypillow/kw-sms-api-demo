INSERT INTO
    簡訊資料 (
        學號,
        對象,
        手機,
        簡訊編號,
        發送日期,
        發送時間,
        內容,
        簡訊發送商
    )
VALUES
    (
        :student_id,
        :recipient,
        :phone_number,
        :sms_id,
        CAST(GETDATE() AS DATE),
        CAST(GETDATE() AS TIME),
        :message_content,
        :vendor_id
    );