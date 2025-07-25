## FastAPI 建置

1. 伺服器資料位於 `config.py`
2. 跑 `sudo chmod +x run.sh`
3. 再跑 `./run.sh`


## HTTP 方法
```http
POST http://192.168.x.x/sms
Content-Type: application/json

{
    <!-- 學號 -->
  "student_id": "string",

    <!-- 對象 -->
  "recipient": "string",

   <!-- 手機 -->
  "phone_number": "string",

   <!-- 內容 -->
  "message_content": "string"
}

###
```
## Curl 方法參考 / 舉例
```bash
curl -X 'POST' \
  'http://localhost:8000/sms' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "student_id": "123445",
  "recipient": "me",
  "phone_number": "0919386126",
  "message_content": "meowmeow6"
}'
```


## Response

```json
"sent"
```


## Add to openssl.cnf
```cnf
[openssl_init]
ssl_conf = ssl_sect

[ssl_sect]
system_default = system_default_sect

[system_default_sect]
CipherString =  DEFAULT@SECLEVEL=0

```