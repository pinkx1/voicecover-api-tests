1. **Успешное создание копии задания с корректным ID.**  
   Проверка, что при передаче существующего ID перевода сервер создает копию задания.  
   Ожидается, что сервер возвращает статус код `200`, а тело ответа содержит информацию о новой копии задания.

2. **Попытка создания копии с несуществующим ID.**  
   Проверка реакции сервера на попытку создать копию перевода с несуществующим ID (например, `id=999999`).  
   Ожидается, что сервер возвращает статус код `404` (Not Found), а тело ответа содержит описание ошибки.

3. **Попытка создания копии чужого задания (для пользователя).**  
   Проверка, что пользователь с ролью `user` не может создать копию задания, принадлежащего другому пользователю.  
   Ожидается, что сервер возвращает статус код `403` (Forbidden).

4. **Попытка создания копии задания с некорректным ID (нечисловое значение).**  
   Проверка, что сервер корректно обрабатывает запрос с некорректным значением ID (например, `id=abc`).  
   Ожидается, что сервер возвращает статус код `422` (Validation Error), а тело ответа содержит описание ошибки.

5. **Запрос без авторизации.**  
   Проверка, что сервер запрещает доступ к эндпоинту без авторизации.  
   Ожидается, что сервер возвращает статус код `401` (Unauthorized).

6. **Проверка структуры ответа при успешном создании копии.**  
   Проверить, что тело ответа при успешном создании копии задания содержит все ключи и значения в соответствии с ожидаемой схемой:  
   - `language` (string),  
   - `save_origin_voice` (boolean),  
   - `has_logo` (boolean),  
   - `notification` (boolean),  
   - и т.д., вплоть до информации о пользователе (`user`).