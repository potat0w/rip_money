from test.test_main import client
from main import app
from fastapi import status
from router.auth import get_current_user
from database import SessionLocal
from models import Transaction, User
from datetime import date
from types import SimpleNamespace
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def override_get_current_user():
    return SimpleNamespace(id=1, username='testuser')

def create_test_transaction():
    db = SessionLocal()
    if db.query(User).filter(User.id == 1).first() is None:
        user = User(
            id=1,
            username='testuser',
            email='testuser@example.com',
            hashed_password=bcrypt_context.hash('test1234'),
        )
        db.add(user)
        db.commit()
    db.query(Transaction).filter(Transaction.id == 99).delete()
    transaction = Transaction(
        id=99,
        title='Testing',
        amount=500,
        type='expense',
        category='Test',
        date=date(2026, 9, 28),
        owner_id=1
    )
    db.add(transaction)
    db.commit()

app.dependency_overrides[get_current_user] = override_get_current_user

create_test_transaction()

def test_read_transactions():
    response = client.get('/transactions')
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_read_specific_transaction():
    create_test_transaction()
    response = client.get('/transactions/99')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == 99

def test_create_transaction():
    db = SessionLocal()
    db.query(Transaction).filter(Transaction.id == 0).delete()
    db.commit()
    request_data = {
        "title": "Test Expense",
        "amount": 500,
        "type": "expense",
        "category": "Test",
        "date": "2026-09-28"
    }
    response = client.post('/transactions', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['title'] == 'Test Expense'
    assert response.json()['amount'] == 500
    assert response.json()['type'] == 'expense'
    assert response.json()['category'] == 'Test'
    assert response.json()['owner_id'] == 1

def test_update_transaction():
    create_test_transaction()
    request_data = {
        "title": "Updated"
    }
    response = client.put('/transactions/99', json=request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == 99
    assert response.json()['title'] == 'Updated'

def test_delete_transaction():
    create_test_transaction()
    response = client.delete('/transactions/99')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Transaction deleted successfully'}
