# README

## Описание проекта

Этот проект содержит автотесты, которые проверяют функциональность API. Все тесты разработаны с использованием Python версии **3.11.9**.

## Подготовка к запуску

### Установка зависимостей

1. Убедитесь, что у вас установлен Python версии 3.11.9.
2. Установите зависимости из файла `requirements.txt`:
   ```bash
   pip install -r requirements.txt
## Настройка окружения
### Настройка MAILSAC_API_KEY
Для получения API-ключа перейдите [по этой ссылке](https://mailsac.com/v2/credentials) и создайте новый ключ.
Если бесплатного месячного лимита не хватает для тестирования, создайте новый аккаунт и сгенерируйте новый ключ.
### Аккаунт EMPTY_BALANCE_USER_EMAIL
На аккаунте **EMPTY_BALANCE_USER_EMAIL** должно быть настроено **два перевода**:

1. С ID, указанным в переменной `TRANSLATION_ID`.
2. С ID, указанным в переменной `TRANSLATION_ID_NO_EDIT`.
Оба перевода должны быть успешно загружены и корректно настроены. 

## Настройка GitHub Actions
Для запуска тестов в GitHub Actions добавьте в репозитории секреты. Сделать это можно по ссылке: https://github.com/юзернейм/репозиторий/settings/secrets/actions  
Добавьте следующие переменные из `.env`:

* MAILSAC_API_KEY
* ADMIN_EMAIL
* ADMIN_PASSWORD
* EMPTY_BALANCE_USER_EMAIL
* EMPTY_BALANCE_USER_PASSWORD
* SOME_BALANCE_USER_EMAIL
* SOME_BALANCE_USER_PASSWORD
* TRANSLATION_ID
* TRANSLATION_ID_NO_EDIT
* URL  

## Запуск тестов
### Локально
Для запуска всех тестов и генерации HTML-отчета выполните:

`pytest --html=report.html --self-contained-html`

Для запуска тестов из конкретного файла:

`pytest path/to/test_file.py --html=report.html --self-contained-html`

Отчет `report.html` будет создан в текущем каталоге. 

### В GitHub Actions

1. Перейдите на вкладку Actions в вашем репозитории. 
2. Найдите Workflow с именем Run API Tests и нажмите на него. 
3. Нажмите кнопку Run workflow. 
4. В появившемся окне:
   1. Если хотите запустить все тесты, оставьте поле test_file пустым. 
   2. Если хотите запустить тесты из конкретного файла, укажите только имя файла, например: `test_example.py`
   3. Путь до файла (tests/test_example.py) будет добавлен автоматически. 
   4. Нажмите Run workflow, чтобы запустить процесс.
5. После завершения выполнения Workflow:
6. Перейдите в раздел Artifacts на странице выполнения. 
7. Скачайте артефакт pytest-html-report. 
8. Распакуйте архив и откройте файл report.html в любом браузере для просмотра результатов.