import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

# Возможные варианты тестов:

# Тест добавления пользователя с существующим логином.
# Тест успешной аутентификации пользователя.
# Тест аутентификации несуществующего пользователя.
# Тест аутентификации пользователя с неправильным паролем.
# Тест отображения списка пользователей.

def test_add_duplicate_user(setup_database, connection):
    """Тест добавления пользователя с существующим логином."""
    add_user('dupuser', 'dup@example.com', 'pass123')
    result = add_user('dupuser', 'other@example.com', 'pass456')
    assert result is False, "Добавление пользователя с существующим логином должно возвращать False."

def test_authenticate_success(setup_database, connection):
    """Тест успешной аутентификации пользователя."""
    add_user('authuser', 'auth@example.com', 'secret')
    assert authenticate_user('authuser', 'secret') is True, "Аутентификация с верными данными должна проходить."

def test_authenticate_nonexistent_user(setup_database, connection):
    """Тест аутентификации несуществующего пользователя."""
    assert authenticate_user('nobody', 'password') is False, "Аутентификация несуществующего пользователя должна возвращать False."

def test_authenticate_wrong_password(setup_database, connection):
    """Тест аутентификации пользователя с неправильным паролем."""
    add_user('passuser', 'pass@example.com', 'correct')
    assert authenticate_user('passuser', 'wrong') is False, "Аутентификация с неправильным паролем должна возвращать False."

def test_display_users(setup_database, connection, capsys):
    """Тест отображения списка пользователей."""
    add_user('user1', 'user1@example.com', 'pass1')
    add_user('user2', 'user2@example.com', 'pass2')
    display_users()
    captured = capsys.readouterr()
    assert 'user1' in captured.out, "Вывод должен содержать логин user1."
    assert 'user2' in captured.out, "Вывод должен содержать логин user2."
    assert 'user1@example.com' in captured.out, "Вывод должен содержать email user1."
    assert 'user2@example.com' in captured.out, "Вывод должен содержать email user2."
