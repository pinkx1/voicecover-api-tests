1. **Получение количества переводов для администратора с параметром my=false.**  
   Проверка, что администратор получает количество всех переводов при передаче параметра `my=false`.  
   Ожидается, что сервер возвращает статус код `200` и число всех переводов.

2. **Получение количества переводов для администратора с параметром my=true.**  
   Проверка, что администратор получает количество только своих переводов при передаче параметра `my=true`.  
   Ожидается, что сервер возвращает статус код `200` и число переводов, связанных с аккаунтом администратора.

3. **Получение количества переводов для пользователя.**  
   Проверка, что пользователь видит количество только своих переводов, независимо от значения параметра `my`.  
   Ожидается, что сервер возвращает статус код `200` и число переводов, связанных с аккаунтом пользователя.

4. **Проверка, что пользователь не видит общее количество переводов при my=false.**  
   Проверка, что пользователь с ролью `user` не может получить общее количество переводов при передаче `my=false`.  
   Ожидается, что сервер возвращает статус код `403` (Forbidden) или возвращает количество только своих переводов.

5. **Запрос без параметра my.**  
   Проверка, что сервер корректно обрабатывает запрос без указания параметра `my`.  
   Ожидается, что сервер возвращает статус код `200` и количество переводов, соответствующее роли пользователя.

6. **Доступ без авторизации.**  
   Проверка, что сервер запрещает доступ к эндпоинту без авторизации.  
   Ожидается, что сервер возвращает статус код `401` (Unauthorized).

7. **Проверка с некорректным значением параметра my.**  
   Проверка реакции сервера на некорректное значение параметра `my` (например, `my=invalid`).  
   Ожидается, что сервер возвращает статус код `422` (Validation Error), а тело ответа содержит описание ошибки.
