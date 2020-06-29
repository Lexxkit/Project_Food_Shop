### Проект "Магазин Еды"

В проекте используются миграции модуля Flask-Migrate.
При первом запуске проекта, для создания таблиц базы данных в терминале необходимо ввести:
1. `flask db upgrade` - для непосредственного создания всех таблиц, используемых в проекте.

Если в проекте отсутствует папка migrations:
1. `flask db init` - для первичной инициализации базы.
2. `flask db migrate` - для создания необходимых команд миграции.
3. `flask db upgrade` - для непосредственного создания всех таблиц, используемых в проекте.

После создания БД (файл 'test.db', название можно изменить в файле config.py):
1. Выполнить `flask add_data data` - для заполнения БД исходными данными. Исходные данные для проекта находятся в файлах 'delivery_categories.csv' и 'delivery_items.csv'.
(Кроме того, вместо flask команды, можно запустить файл 'csv_to_db.py')

Для запуска проекта:
1. Выполнить `flask run` или запустить файл 'app.py'. При необходимости, номер локального порта можно изменить.