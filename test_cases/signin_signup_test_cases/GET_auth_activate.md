1. **Успешная активация пользователя.**  
   Проверка активации пользователя с корректным значением параметра `activate_code`.  
   Ожидается, что сервер возвращает статус код `200`, а тело ответа содержит `{"success": true}`.

2. **Активация с некорректным кодом активации.**  
   Проверка реакции сервера на использование неверного значения в параметре `activate_code`.  
   Ожидается, что сервер возвращает статус код `422`, а тело ответа содержит описание ошибки в формате:  
   ```json
   {
     "detail": [
       {
         "loc": ["query", "activate_code"],
         "msg": "Invalid activation code",
         "type": "value_error"
       }
     ]
   }
3. **Отсутствие параметра activate_code.**
Проверка реакции сервера, если параметр `activate_code` отсутствует в запросе.
Ожидается, что сервер возвращает статус код `422`, а тело ответа содержит описание ошибки, указывающее на отсутствие обязательного параметра.
4. **Пустое значение параметра activate_code**.
Проверка реакции сервера на запрос с пустым значением параметра `activate_code` (например, `/auth/activate?activate_code=`).
Ожидается, что сервер возвращает статус код `422`, а тело ответа содержит описание ошибки.
5. **Попытка повторной активации**.
Проверка реакции сервера на повторную активацию ранее активированного кода.
Ожидается, что сервер возвращает статус код `400` или `422`, а тело ответа содержит описание ошибки.