# Impor library yang diperlukan
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import numpy as np
from scipy.optimize import linear_sum_assignment
import locale

# Inisialisasi aplikasi Flask
app = Flask(__name__)
app.secret_key = 'secret_key_rahasia'

# --- Konfigurasi Format Rupiah ---

# Atur locale ke Indonesia agar pemisah ribuan menggunakan titik (.).
# Blok try-except ini untuk mencegah error jika locale 'id_ID' tidak terinstall di sistem.
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except locale.Error:
    print("Peringatan: Locale 'id_ID.UTF-8' tidak ditemukan. Menggunakan format default.")

def format_rupiah(value):
    """
    Custom filter untuk Jinja2 yang memformat angka menjadi string Rupiah.
    Fungsi ini akan memperlakukan nilai input sebagai ribuan.
    Contoh: nilai 10 akan diformat menjadi 'Rp 10.000'.
    """
    if value is None:
        return "Rp 0"
    
    # Kalikan nilai input dengan 1000 untuk mengubahnya menjadi format ribuan
    value_in_thousands = value * 1000
    
    # Format angka yang sudah dikalikan tersebut dengan pemisah ribuan (titik) dan tanpa desimal
    return locale.format_string("Rp %.0f", value_in_thousands, grouping=True)

# Daftarkan fungsi di atas sebagai filter Jinja2 dengan nama 'rupiah'
app.jinja_env.filters['rupiah'] = format_rupiah

# --- Akhir Konfigurasi Format Rupiah ---


# Inisialisasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Data in-memory (simulasi database)
users = {'admin': {'password': '1234'}}
employees = [
    {'id': 1, 'nama': 'Budi Santoso'},
    {'id': 2, 'nama': 'Siti Rahayu'},
    {'id': 3, 'nama': 'Ahmad Wijaya'},
    {'id': 4, 'nama': 'Vicky Ardiansyah'}
]
tasks = [
    {'id': 1, 'nama': 'Desain UI/UX'},
    {'id': 2, 'nama': 'Pengembangan Backend'},
    {'id': 3, 'nama': 'Testing Aplikasi'},
    {'id': 4, 'nama': 'Pengembangan Frontend'}
]
assignments = []

# Model User untuk Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# Rute-rute aplikasi
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', 
                           employee_count=len(employees),
                           task_count=len(tasks))

@app.route('/karyawan', methods=['GET', 'POST'])
@login_required
def manage_employees():
    if request.method == 'POST':
        nama = request.form.get('nama')
        if nama:
            new_id = max(emp['id'] for emp in employees) + 1 if employees else 1
            employees.append({'id': new_id, 'nama': nama})
            flash('Karyawan berhasil ditambahkan!', 'success')
    return render_template('kelola_karyawan.html', employees=employees)

@app.route('/tugas', methods=['GET', 'POST'])
@login_required
def manage_tasks():
    if request.method == 'POST':
        nama = request.form.get('nama')
        if nama:
            new_id = max(task['id'] for task in tasks) + 1 if tasks else 1
            tasks.append({'id': new_id, 'nama': nama})
            flash('Tugas berhasil ditambahkan!', 'success')
    return render_template('kelola_tugas.html', tasks=tasks)

@app.route('/penugasan/baru')
@login_required
def new_assignment():
    return render_template('buat_penugasan.html', 
                           employees=employees, 
                           tasks=tasks)

@app.route('/penugasan/hasil', methods=['POST'])
@login_required
def assignment_result():
    # Bangun matriks biaya dari form input
    cost_matrix = []
    for emp in employees:
        row = []
        for task in tasks:
            cost_key = f"cost_{emp['id']}_{task['id']}"
            cost_value = float(request.form.get(cost_key, 0))
            row.append(cost_value)
        cost_matrix.append(row)
    
    # Konversi ke numpy array untuk diproses
    cost_matrix = np.array(cost_matrix)
    
    # Jalankan algoritma Hungarian untuk optimasi
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    total_cost = cost_matrix[row_ind, col_ind].sum()
    
    # Siapkan hasil penugasan untuk ditampilkan di template
    hasil_penugasan = []
    for i in range(len(row_ind)):
        karyawan = employees[row_ind[i]]
        tugas = tasks[col_ind[i]]
        biaya = cost_matrix[row_ind[i], col_ind[i]]
        hasil_penugasan.append({
            'karyawan': karyawan['nama'],
            'tugas': tugas['nama'],
            'biaya': biaya
        })
    
    # Simpan histori penugasan (opsional)
    assignments.append({
        'matrix': cost_matrix.tolist(),
        'hasil': hasil_penugasan,
        'total_biaya': total_cost
    })
    
    # Render halaman hasil dengan data yang sudah dihitung
    return render_template('hasil_penugasan.html', 
                           hasil=hasil_penugasan,
                           total_cost=total_cost)

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(debug=True)
else: 
    # untuk production 
    application = app