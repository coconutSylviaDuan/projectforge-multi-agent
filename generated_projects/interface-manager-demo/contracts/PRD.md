# æ¥å£ç®¡çå¹³å° PRD

Version: v0.1

## Background
å¨å¾®æå¡æ¶æä¸ï¼ååç«¯å¯¹æ¥è¿ç¨ä¸­æ¥å£æ°éæ¿å¢ï¼ç¼ºä¹ç»ä¸çæ¥å£ç®¡çå·¥å·å¯¼è´ä¿¡æ¯æ£è½ãMock éç½®å°é¾ãèè°è¿åº¦ä¸æãæ¬å¹³å°æ¨å¨æä¾è½»éçº§çæ¥å£ç®å½ãMock éç½®ãåæ´è®°å½åèè°ç¶æç®¡çåè½ï¼æåå¢éåä½æçã

## Goals
- å»ºç«ç»ä¸çæ¥å£ç®å½ï¼è®©å¢éæåè½å¿«éæ¥æ¾åçè§£æ¥å£
- æä¾ Mock éç½®è½åï¼å¸®å©åç«¯è±ç¦»åç«¯ç¬ç«å¼å
- è®°å½æ¥å£åæ´åå²ï¼è¿½è¸ªæ¯æ¬¡ä¿®æ¹
- è·è¸ªèè°è¿åº¦ï¼æç¡®å½åé»å¡ç¹

## User Roles
- åç«¯å¼åè
- åç«¯å¼åè
- æµè¯å·¥ç¨å¸
- ææ¯ç®¡çè

## Business Modules
- æ¥å£ç®å½ç®¡çï¼å±ç¤ºæææ¥å£åè¡¨ï¼æ¯æç­éååé¡µ
- æ¥å£è¯¦æç®¡çï¼å±ç¤ºåä¸ªæ¥å£çå®æ´å®ä¹
- Mock éç½®ç®¡çï¼ä¸ºæ¥å£éç½®æ¨¡æååº
- åæ´è®°å½ç®¡çï¼è®°å½æ¥å£ä¿¡æ¯åæ´åå²
- èè°ç¶æç®¡çï¼è®°å½åç®¡çæ¥å£çèè°è¿åº¦

## Page Requirements
### æ¥å£ç®å½é¡µ
- Route: `/interfaces`
- Purpose: å±ç¤ºæææ¥å£çåè¡¨ï¼æ¯æåé¡µåå¿«éæç´¢
- Primary actions: æµè§æ¥å£åè¡¨, ç¹å»æ¥å£åç§°è¿å¥è¯¦æé¡µ, ææ¹æ³ç­éï¼GET/POST ç­ï¼

### æ¥å£è¯¦æé¡µ
- Route: `/interfaces/{id}`
- Purpose: å±ç¤ºåä¸ªæ¥å£çå®æ´ä¿¡æ¯ï¼åæ¬åºç¡ä¿¡æ¯ãè¯·æ±/ååºåæ°ãåæ´è®°å½ãMock éç½®åèè°ç¶æ
- Primary actions: æ¥çæ¥å£åºæ¬ä¿¡æ¯, åæ¢å° Mock éç½®æ ç­¾é¡µ, åæ¢å°åæ´è®°å½æ ç­¾é¡µ, åæ¢å°èè°ç¶ææ ç­¾é¡µ

### Mock éç½®é¡µ
- Route: `/interfaces/{id}/mock`
- Purpose: éç½®æ¥å£ç Mock ååºï¼åæ¬å¯ç¨/ç¦ç¨ãç¶æç ãååºå¤´ãååºä½åå»¶è¿
- Primary actions: å¯ç¨/ç¦ç¨ Mock, ç¼è¾ååºç¶æç , ç¼è¾ååºå¤´ï¼JSONï¼, ç¼è¾ååºä½ï¼JSONï¼, è®¾ç½®å»¶è¿, ä¿å­éç½®

### åæ´è®°å½é¡µ
- Route: `/interfaces/{id}/changes`
- Purpose: ææ¶é´ååºååºæ¥å£çææåæ´è®°å½
- Primary actions: æ¥çåæ´åå²åè¡¨, æ¥çæ¯æ¬¡åæ´çå·ä½å­æ®µåååå¼

### èè°ç¶æé¡µ
- Route: `/interfaces/{id}/integration`
- Purpose: æ¥çåæ´æ°æ¥å£çèè°è¿åº¦ç¶æ
- Primary actions: æ¥çå½åèè°ç¶æ, æ´æ°ç¶æï¼æªå¼å§->èè°ä¸­->å·²å®æï¼, æ·»å å¤æ³¨

## Interface Management

### æ¥å£ç®å½ / è·åæ¥å£åè¡¨
- Method: `GET`
- Path: `/api/interfaces`
- Description: åé¡µè¿åæ¥å£åè¡¨ï¼æ¯æææ¹æ³ç­é
- Frontend usage: æ¥å£ç®å½é¡µå è½½æ¶è°ç¨ï¼æ¸²æåè¡¨
- Backend notes: ä½¿ç¨ SQLite LIMIT/OFFSET åé¡µï¼æ¯æ method ç­é
- Request fields:
  - `page` (integer): é¡µç ï¼é»è®¤1
  - `page_size` (integer): æ¯é¡µæ¡æ°ï¼é»è®¤20
  - `method` (string): ç­éæ¹æ³ï¼å¯é
- Response fields:
  - `total` (integer): æ»æ°
  - `items` (array): æ¥å£å¯¹è±¡åè¡¨
  - `page` (integer): å½åé¡µç 
  - `page_size` (integer): æ¯é¡µæ¡æ°

### æ¥å£ç®å½ / è·ååä¸ªæ¥å£è¯¦æ
- Method: `GET`
- Path: `/api/interfaces/{id}`
- Description: æ ¹æ® ID è¿åæ¥å£çå®æ´ä¿¡æ¯
- Frontend usage: æ¥å£è¯¦æé¡µå è½½æ¶è°ç¨
- Backend notes: è¿å JSON å¯¹è±¡ï¼request_params å response_schema ä¸º JSON å­ç¬¦ä¸²
- Request fields:
- Response fields:
  - `id` (integer): 
  - `name` (string): 
  - `method` (string): 
  - `path` (string): 
  - `description` (string): 
  - `request_params` (string): 
  - `response_schema` (string): 
  - `created_at` (string): 
  - `updated_at` (string): 

### Mock éç½® / è·åæ¥å£ç Mock éç½®
- Method: `GET`
- Path: `/api/interfaces/{id}/mock`
- Description: è¿åæå®æ¥å£ç Mock éç½®ï¼è¥ä¸å­å¨åè¿åé»è®¤å¼
- Frontend usage: Mock éç½®é¡µå è½½æ¶è·åå½åéç½®
- Backend notes: è¥æ²¡æ MockConfig è®°å½ï¼è¿åé»è®¤æªå¯ç¨ãç¶æç 200ãç©ºå¤´åç©ºä½
- Request fields:
- Response fields:
  - `enabled` (boolean): 
  - `status_code` (integer): 
  - `headers` (string): 
  - `body` (string): 
  - `delay_ms` (integer): 

### Mock éç½® / æ´æ°/åå»º Mock éç½®
- Method: `PUT`
- Path: `/api/interfaces/{id}/mock`
- Description: æ´æ°æåå»ºæ¥å£ç Mock éç½®
- Frontend usage: ä¿å­ Mock éç½®æ¶è°ç¨
- Backend notes: ä½¿ç¨ upsert é»è¾ï¼è¥å­å¨åæ´æ°ï¼å¦ååå»º
- Request fields:
  - `enabled` (boolean): 
  - `status_code` (integer): 
  - `headers` (string): 
  - `body` (string): 
  - `delay_ms` (integer): 
- Response fields:
  - `success` (boolean): 

### åæ´è®°å½ / è·åæ¥å£çåæ´è®°å½
- Method: `GET`
- Path: `/api/interfaces/{id}/changes`
- Description: ææ¶é´ååºè¿ååæ´è®°å½åè¡¨
- Frontend usage: åæ´è®°å½é¡µå è½½æ¶è°ç¨
- Backend notes: ä» change_logs è¡¨æ¥è¯¢ï¼æåº changed_at DESC
- Request fields:
  - `limit` (integer): è¿åæ¡æ°éå¶ï¼é»è®¤20
- Response fields:
  - `items` (array): æ¯æ¡è®°å½åå« id, field, old_value, new_value, changed_at

### èè°ç¶æ / è·åæ¥å£çèè°ç¶æ
- Method: `GET`
- Path: `/api/interfaces/{id}/integration`
- Description: è¿åæå®æ¥å£çèè°ç¶æå¯¹è±¡
- Frontend usage: èè°ç¶æé¡µå è½½æ¶è·åå½åç¶æ
- Backend notes: è¥æ²¡æ IntegrationStatus è®°å½ï¼è¿åé»è®¤æªå¼å§
- Request fields:
- Response fields:
  - `status` (string): æªå¼å§/èè°ä¸­/å·²å®æ
  - `notes` (string): 
  - `updated_at` (string): 

### èè°ç¶æ / æ´æ°èè°ç¶æ
- Method: `PUT`
- Path: `/api/interfaces/{id}/integration`
- Description: æ´æ°èè°ç¶æåå¤æ³¨
- Frontend usage: ç¨æ·ç¹å»æ´æ°æé®æ¶è°ç¨
- Backend notes: ä½¿ç¨ upsert é»è¾ï¼æ´æ° updated_at
- Request fields:
  - `status` (string): 
  - `notes` (string): 
- Response fields:
  - `success` (boolean): 

## Data Requirements
- SQLite æ°æ®åºï¼åå«åå¼ è¡¨ï¼interfaces, mock_configs, change_logs, integration_statuses
- interfaces è¡¨å­æ®µï¼id, name, method, path, description, request_params, response_schema, created_at, updated_at
- mock_configs è¡¨å­æ®µï¼id, interface_id, enabled, status_code, headers, body, delay_ms, updated_at
- change_logs è¡¨å­æ®µï¼id, interface_id, field, old_value, new_value, changed_at
- integration_statuses è¡¨å­æ®µï¼id, interface_id, status, notes, updated_at
- ç§å­æ°æ®ï¼é¢ç½® 3-5 ä¸ªç¤ºä¾æ¥å£ï¼å¹¶ä¸ºæ¯ä¸ªæ¥å£çæç¸åºç Mock éç½®ãåæ´è®°å½ï¼æ¨¡æï¼åèè°ç¶æ

## Acceptance Criteria
- æ¥å£ç®å½é¡µå¯æ­£ç¡®åé¡µæ¾ç¤ºæ¥å£åè¡¨ï¼æ¯æææ¹æ³ç­é
- ç¹å»æ¥å£å¯è·³è½¬å°è¯¦æé¡µï¼å±ç¤ºå¨é¨å­æ®µä¿¡æ¯
- Mock éç½®é¡µå¯æ­£å¸¸ç¼è¾å¹¶ä¿å­ï¼ä¿å­åéæ°å è½½æ¾ç¤ºæ´æ°åå®¹
- åæ´è®°å½é¡µææ¶é´ååºæ¾ç¤ºåè¡¨ï¼åå«å­æ®µåæ´ç»è
- èè°ç¶æé¡µå¯æ¥çå½åç¶æï¼å¹¶è½æåæ´æ°ä¸ºå¶ä»ç¶æ
- æææä½æåççéè¯¯æç¤ºï¼å¦ç½ç»éè¯¯ï¼

## Frontend Handoff
- ä½¿ç¨ Hash è·¯ç±ï¼å¦ #/interfacesï¼å®ç°åé¡µåºç¨
- æ ·å¼åºäº Bootstrap 5 CDNï¼ä¹å¯èªå®ä¹å°é CSS
- ææé¡µé¢å¨ç§»å¨ç«¯å PC ç«¯åºæ¬å¯ç¨ï¼ååºå¼ï¼
- åç«¯è¿åæ¶é´å­æ®µä¸º ISO 8601 æ ¼å¼å­ç¬¦ä¸²
- è¯·æ±ä¸­ä¼ å¥ JSON å­ç¬¦ä¸²çå­æ®µï¼å¦ request_paramsï¼å¨åç«¯ç¨ textarea å±ç¤ºåç¼è¾

## Backend Handoff
- FastAPI åºç¨ï¼ä½¿ç¨ uvicorn è¿è¡
- æ°æ®åºä½¿ç¨ SQLiteï¼éè¿ SQLAlchemy æç´æ¥ sqlite3 æ¨¡åæä½
- REST API è®¾è®¡éµå¾ªä¸è¿°æ¥å£ç®¡çè¡¨æ ¼
- å¯å¨æ¶èªå¨åå»ºè¡¨ç»æå¹¶æå¥ç§å­æ°æ®ï¼å¯å¨åºç¨çå½å¨æäºä»¶ä¸­å®ç°ï¼
- æææ¥å£è¿åç»ä¸ç JSON æ ¼å¼ï¼æåæ¶åå« data å­æ®µï¼å¤±è´¥æ¶åå« error å­æ®µ
