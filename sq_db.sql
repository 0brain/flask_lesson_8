CREATE TABLE IF NOT EXISTS mainmenu (  # Створюємо таблицю mainmenu, якщо вона ще не існує
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);