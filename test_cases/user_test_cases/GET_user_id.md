1. **Успешный запрос с корректным ID пользователя.**  
   Проверка, что администратор может получить данные пользователя по корректному ID.  
   Ожидается, что сервер возвращает статус код `200`, а тело ответа содержит полные данные пользователя:
   - `lastname` (string),  
   - `firstname` (string),  
   - `avatar` (string),  
   - `email` (string),  
   - `phone` (string),  
   - `telegram` (string),  
   - `telegram_chatid` (integer),  
   - `balance` (integer),  
   - `is_active` (boolean),  
   - `id` (integer),  
   - `created_at` (ISO 8601),  
   - `last_login` (ISO 8601 или `null`),  
   - `utm` (string).

2. **Запрос с несуществующим ID пользователя.**  
   Проверка, что сервер корректно обрабатывает запрос с ID, которого нет в базе данных.  
   Ожидается, что сервер возвращает статус код `404`, а тело ответа содержит сообщение об ошибке.

3. **Запрос с некорректным ID (строка вместо числа).**  
   Проверка, что сервер корректно отклоняет запрос с некорректным значением ID (например, `id="abc"`).  
   Ожидается, что сервер возвращает статус код `422` (Validation Error).

4. **Запрос без авторизации.**  
   Проверка, что сервер отклоняет запрос, если администратор не авторизован.  
   Ожидается, что сервер возвращает статус код `401` (Unauthorized).

5. **Запрос от пользователя с ролью `user`.**  
   Проверка, что обычный пользователь не может получить данные  пользователя.  
   Ожидается, что сервер возвращает статус код `403` (Forbidden).

6. **Запрос с ID удаленного пользователя.**  
   Проверка, что сервер корректно обрабатывает запрос, если пользователь был деактивирован (`is_active=false`).  
   Ожидается, что сервер возвращает статус код `200`, а тело ответа содержит данные пользователя.
