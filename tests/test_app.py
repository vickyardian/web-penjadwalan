import pytest

from app import app, format_rupiah

# ----------- Unit Test untuk Fungsi Utility -----------
def test_format_rupiah():
    assert format_rupiah(10) == "Rp 10.000"
    assert format_rupiah(0) == "Rp 0"
    assert format_rupiah(None) == "Rp 0"
    assert format_rupiah(123456) == "Rp 123.456.000"

# ----------- Integration Test untuk Routes -----------

def login(client):
    return client.post('/login', data={
        'username': 'admin',
        'password': '1234'
    }, follow_redirects=True)

def test_login_logout():
    with app.test_client() as client:
        # Login gagal
        response = client.post('/login', data={'username': 'admin', 'password': 'salah'}, follow_redirects=True)
        assert b'Username atau password salah!' in response.data

        # Login berhasil
        response = login(client)
        assert b'Dashboard' in response.data

        # Logout
        response = client.get('/logout', follow_redirects=True)
        assert b'Login' in response.data

def test_dashboard():
    with app.test_client() as client:
        login(client)
        response = client.get('/')
        assert b'Dashboard' in response.data

def test_manage_employees_get_post():
    with app.test_client() as client:
        login(client)
        
        # GET request
        response = client.get('/karyawan')
        assert response.status_code == 200
        
        # POST valid
        response = client.post('/karyawan', data={'nama': 'Test User'}, follow_redirects=True)
        assert b'Karyawan berhasil ditambahkan!' in response.data

        # POST kosong
        response = client.post('/karyawan', data={'nama': ''}, follow_redirects=True)
        assert b'Karyawan berhasil ditambahkan!' not in response.data

def test_manage_tasks_get_post():
    with app.test_client() as client:
        login(client)

        # GET request
        response = client.get('/tugas')
        assert response.status_code == 200

        # POST valid
        response = client.post('/tugas', data={'nama': 'Test Tugas'}, follow_redirects=True)
        assert b'Tugas berhasil ditambahkan!' in response.data

        # POST kosong
        response = client.post('/tugas', data={'nama': ''}, follow_redirects=True)
        assert b'Tugas berhasil ditambahkan!' not in response.data

def test_new_assignment():
    with app.test_client() as client:
        login(client)
        response = client.get('/penugasan/baru')
        assert b'Buat Penugasan' in response.data or response.status_code == 200

def test_assignment_result():
    with app.test_client() as client:
        login(client)

        # Siapkan data cost matrix
        form_data = {
            'cost_1_1': '4', 'cost_1_2': '2', 'cost_1_3': '3', 'cost_1_4': '2',
            'cost_2_1': '2', 'cost_2_2': '3', 'cost_2_3': '4', 'cost_2_4': '1',
            'cost_3_1': '3', 'cost_3_2': '4', 'cost_3_3': '2', 'cost_3_4': '3',
            'cost_4_1': '2', 'cost_4_2': '1', 'cost_4_3': '3', 'cost_4_4': '4'
        }

        response = client.post('/penugasan/hasil', data=form_data, follow_redirects=True)
        assert b'Hasil' in response.data or b'Rp' in response.data
