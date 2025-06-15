from flask import Flask, render_template, request, jsonify
import numpy as np # type: ignore
from scipy.optimize import linear_sum_assignment # type: ignore
import json
import os

app = Flask(__name__)

class HungarianScheduler:
    def __init__(self):
        self.employees = []
        self.tasks = []
        self.cost_matrix = []
    
    def set_employees(self, employees):
        """Set daftar karyawan"""
        self.employees = employees
    
    def set_tasks(self, tasks):
        """Set daftar tugas"""
        self.tasks = tasks
    
    def set_cost_matrix(self, cost_matrix):
        """Set matriks biaya/preferensi"""
        self.cost_matrix = np.array(cost_matrix)
    
    def solve(self):
        """Menyelesaikan masalah penugasan menggunakan Hungarian Algorithm"""
        if len(self.cost_matrix) == 0:
            return None, None, 0
        
        # Menggunakan scipy untuk Hungarian Algorithm
        row_indices, col_indices = linear_sum_assignment(self.cost_matrix)
        
        # Menghitung total biaya
        total_cost = self.cost_matrix[row_indices, col_indices].sum()
        
        # Membuat hasil assignment
        assignments = []
        for i, j in zip(row_indices, col_indices):
            assignments.append({
                'employee': self.employees[i],
                'task': self.tasks[j],
                'cost': int(self.cost_matrix[i, j])
            })
        
        return assignments, total_cost

# Instance global scheduler
scheduler = HungarianScheduler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/set_data', methods=['POST'])
def set_data():
    """API untuk mengatur data karyawan, tugas, dan matriks biaya"""
    try:
        data = request.get_json()
        
        employees = data.get('employees', [])
        tasks = data.get('tasks', [])
        cost_matrix = data.get('cost_matrix', [])
        
        if len(employees) == 0 or len(tasks) == 0:
            return jsonify({'error': 'Karyawan dan tugas tidak boleh kosong'}), 400
        
        if len(employees) != len(cost_matrix) or len(tasks) != len(cost_matrix[0]):
            return jsonify({'error': 'Dimensi matriks biaya tidak sesuai'}), 400
        
        scheduler.set_employees(employees)
        scheduler.set_tasks(tasks)
        scheduler.set_cost_matrix(cost_matrix)
        
        return jsonify({'message': 'Data berhasil diatur'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/solve', methods=['POST'])
def solve_assignment():
    """API untuk menyelesaikan masalah penugasan"""
    try:
        assignments, total_cost = scheduler.solve()
        
        if assignments is None:
            return jsonify({'error': 'Tidak ada data untuk diproses'}), 400
        
        return jsonify({
            'assignments': assignments,
            'total_cost': int(total_cost),
            'success': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/example_data', methods=['GET'])
def get_example_data():
    """API untuk mendapatkan contoh data"""
    example_data = {
        'employees': ['Andi', 'Budi', 'Citra', 'Dani'],
        'tasks': ['Task A', 'Task B', 'Task C', 'Task D'],
        'cost_matrix': [
            [9, 2, 7, 8],
            [6, 4, 3, 7],
            [5, 8, 1, 8],
            [7, 6, 9, 4]
        ]
    }
    return jsonify(example_data)

if __name__ == '__main__':
    # untuk development
    app.run(debug=True)
else:
    # untuk production 
    application = app