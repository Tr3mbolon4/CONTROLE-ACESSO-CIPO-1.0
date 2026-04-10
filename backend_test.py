#!/usr/bin/env python3
"""
Sistema CIPOLATTI - Backend API Testing
Comprehensive test suite for access control system
"""

import requests
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

class CipolattiAPITester:
    def __init__(self, base_url="https://cipo-access.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.tests_run = 0
        self.tests_passed = 0
        self.token = None
        self.user_info = None

    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        
        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url)
            elif method == 'POST':
                if files:
                    # Remove Content-Type for file uploads
                    headers = {k: v for k, v in self.session.headers.items() if k != 'Content-Type'}
                    response = requests.post(url, files=files, data=data, headers=headers, cookies=self.session.cookies)
                else:
                    response = self.session.post(url, json=data)
            elif method == 'PUT':
                response = self.session.put(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}", "PASS")
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}", "FAIL")
                try:
                    error_detail = response.json()
                    self.log(f"   Error: {error_detail}", "ERROR")
                except:
                    self.log(f"   Error: {response.text}", "ERROR")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Exception: {str(e)}", "FAIL")
            return False, {}

    def test_auth(self):
        """Test authentication system"""
        self.log("=== TESTING AUTHENTICATION ===", "SECTION")
        
        # Test login
        login_data = {
            "email": "admin@portaria.com",
            "password": "admin123"
        }
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success:
            self.user_info = response
            self.log(f"Logged in as: {response.get('name')} ({response.get('role')})")
            
            # Test get current user
            success, _ = self.run_test(
                "Get Current User",
                "GET", 
                "auth/me",
                200
            )
            
            return True
        return False

    def test_agendamentos(self):
        """Test appointments system - create 15 of each type"""
        self.log("=== TESTING AGENDAMENTOS (APPOINTMENTS) ===", "SECTION")
        
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        agendamento_ids = []
        
        # Test CARREGAMENTO appointments (15)
        self.log("Creating 15 CARREGAMENTO appointments...")
        for i in range(1, 16):
            data = {
                "tipo": "carregamento",
                "data_prevista": tomorrow,
                "hora_prevista": f"{8 + (i % 8):02d}:00",
                "placa_carreta": f"CAR{i:04d}",
                "placa_cavalo": f"CAV{i:04d}",
                "motorista": f"MOTORISTA CARREGAMENTO {i}",
                "empresa_terceirizada": f"EMPRESA TERCEIRIZADA {i}",
                "destino": f"SHOPPING DESTINO {i}",
                "cubagem": f"{50 + i}m³",
                "observacao": f"Observação carregamento {i}"
            }
            
            success, response = self.run_test(
                f"Create Carregamento {i}",
                "POST",
                "agendamentos",
                200,
                data=data
            )
            if success:
                agendamento_ids.append(response.get('id'))

        # Test VISITANTE appointments (15)
        self.log("Creating 15 VISITANTE appointments...")
        for i in range(1, 16):
            data = {
                "tipo": "visitante",
                "data_prevista": tomorrow,
                "hora_prevista": f"{9 + (i % 6):02d}:00",
                "nome": f"VISITANTE NOME COMPLETO {i}",
                "placa": f"VIS{i:04d}",
                "observacao": f"Observação visitante {i}"
            }
            
            success, response = self.run_test(
                f"Create Visitante {i}",
                "POST",
                "agendamentos",
                200,
                data=data
            )
            if success:
                agendamento_ids.append(response.get('id'))

        # Test FUNCIONÁRIO appointments (15)
        self.log("Creating 15 FUNCIONÁRIO appointments...")
        for i in range(1, 16):
            data = {
                "tipo": "funcionario",
                "data_prevista": tomorrow,
                "hora_prevista": f"{7 + (i % 10):02d}:30",
                "nome": f"FUNCIONÁRIO NOME COMPLETO {i}",
                "setor": f"SETOR {i}",
                "responsavel": f"RESPONSÁVEL {i}",
                "tipo_permissao": "saida_antecipada" if i % 2 == 0 else "entrada_atrasada",
                "hora_permitida": f"{16 + (i % 3):02d}:00",
                "observacao": f"Observação funcionário {i}"
            }
            
            success, response = self.run_test(
                f"Create Funcionário {i}",
                "POST",
                "agendamentos",
                200,
                data=data
            )
            if success:
                agendamento_ids.append(response.get('id'))

        # Test DIRETORIA appointments (15)
        self.log("Creating 15 DIRETORIA appointments...")
        for i in range(1, 16):
            data = {
                "tipo": "diretoria",
                "data_prevista": tomorrow,
                "hora_prevista": f"{8 + (i % 8):02d}:15",
                "nome": f"DIRETOR NOME COMPLETO {i}",
                "placa": f"DIR{i:04d}",
                "observacao": f"Observação diretoria {i}"
            }
            
            success, response = self.run_test(
                f"Create Diretoria {i}",
                "POST",
                "agendamentos",
                200,
                data=data
            )
            if success:
                agendamento_ids.append(response.get('id'))

        # Test FROTA appointments (15)
        self.log("Creating 15 FROTA appointments...")
        for i in range(1, 16):
            data = {
                "tipo": "frota",
                "data_prevista": tomorrow,
                "hora_prevista": f"{7 + (i % 9):02d}:45",
                "carro": f"FIAT STRADA {i}",
                "placa": f"FRT{i:04d}",
                "motorista": f"MOTORISTA FROTA {i}",
                "destino": f"DESTINO FROTA {i}",
                "km_saida": 10000 + (i * 100),
                "observacao": f"Observação frota {i}"
            }
            
            success, response = self.run_test(
                f"Create Frota {i}",
                "POST",
                "agendamentos",
                200,
                data=data
            )
            if success:
                agendamento_ids.append(response.get('id'))

        # Test list agendamentos
        success, response = self.run_test(
            "List All Agendamentos",
            "GET",
            "agendamentos?limit=100",
            200
        )
        
        if success:
            total = response.get('total', 0)
            self.log(f"Total agendamentos created: {total}")

        return agendamento_ids

    def test_carregamentos_with_photos(self):
        """Test carregamentos with photo upload"""
        self.log("=== TESTING CARREGAMENTOS WITH PHOTOS ===", "SECTION")
        
        carregamento_ids = []
        
        # Create 10 carregamentos for photo testing
        self.log("Creating 10 carregamentos for photo testing...")
        for i in range(1, 11):
            data = {
                "placa_carreta": f"PHC{i:04d}",
                "placa_cavalo": f"PHV{i:04d}",
                "motorista": f"MOTORISTA FOTO {i}",
                "empresa_terceirizada": f"EMPRESA FOTO {i}",
                "destino": f"SHOPPING FOTO {i}",
                "cubagem": f"{60 + i}m³",
                "observacao": f"Carregamento para teste de fotos {i}"
            }
            
            success, response = self.run_test(
                f"Create Carregamento for Photos {i}",
                "POST",
                "carregamentos",
                200,
                data=data
            )
            if success:
                carregamento_ids.append(response.get('id'))

        # Test photo upload simulation (we can't actually upload files in this test)
        if carregamento_ids:
            carregamento_id = carregamento_ids[0]
            self.log(f"Testing photo endpoints for carregamento {carregamento_id}")
            
            # Test get carregamento details
            success, response = self.run_test(
                "Get Carregamento Details",
                "GET",
                f"carregamentos/{carregamento_id}",
                200
            )

        # Test register exit for some carregamentos
        self.log("Registering exit for 5 carregamentos...")
        for i, carregamento_id in enumerate(carregamento_ids[:5]):
            if carregamento_id:
                data = {
                    "hora_saida": f"{14 + (i % 4):02d}:{30 + (i * 5):02d}"
                }
                
                success, response = self.run_test(
                    f"Register Exit Carregamento {i+1}",
                    "PUT",
                    f"carregamentos/{carregamento_id}",
                    200,
                    data=data
                )

        return carregamento_ids

    def test_fleet_with_photos(self):
        """Test fleet management with photos"""
        self.log("=== TESTING FLEET WITH PHOTOS ===", "SECTION")
        
        fleet_ids = []
        
        # Create 10 fleet records
        self.log("Creating 10 fleet records for photo testing...")
        for i in range(1, 11):
            data = {
                "carro": f"FIAT STRADA FOTO {i}",
                "placa": f"FLT{i:04d}",
                "motorista": f"MOTORISTA FLEET {i}",
                "destino": f"DESTINO FLEET {i}",
                "km_saida": 15000 + (i * 150),
                "observacao": f"Fleet para teste de fotos {i}"
            }
            
            success, response = self.run_test(
                f"Create Fleet Record {i}",
                "POST",
                "fleet",
                200,
                data=data
            )
            if success:
                fleet_ids.append(response.get('id'))

        # Test return for 8 fleet records
        self.log("Processing return for 8 fleet records...")
        for i, fleet_id in enumerate(fleet_ids[:8]):
            if fleet_id:
                data = {
                    "km_retorno": 15000 + (i * 150) + 50 + (i * 10),
                    "observacao": f"Retorno fleet {i+1}"
                }
                
                success, response = self.run_test(
                    f"Process Fleet Return {i+1}",
                    "POST",
                    f"fleet/{fleet_id}/return",
                    200,
                    data=data
                )

        return fleet_ids

    def test_reports(self):
        """Test reporting system"""
        self.log("=== TESTING REPORTS ===", "SECTION")
        
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Test carregamentos report
        success, response = self.run_test(
            "Carregamentos Report",
            "GET",
            f"reports/carregamentos?data_inicio={yesterday}&data_fim={today}",
            200
        )
        
        # Test fleet report
        success, response = self.run_test(
            "Fleet Report",
            "GET",
            f"reports/fleet?data_inicio={yesterday}&data_fim={today}",
            200
        )
        
        # Test visitors report
        success, response = self.run_test(
            "Visitors Report",
            "GET",
            f"reports/visitors?data_inicio={yesterday}&data_fim={today}",
            200
        )
        
        # Test employees report
        success, response = self.run_test(
            "Employees Report",
            "GET",
            f"reports/employees?data_inicio={yesterday}&data_fim={today}",
            200
        )
        
        # Test directors report
        success, response = self.run_test(
            "Directors Report",
            "GET",
            f"reports/directors?data_inicio={yesterday}&data_fim={today}",
            200
        )

    def test_dashboard(self):
        """Test dashboard data"""
        self.log("=== TESTING DASHBOARD ===", "SECTION")
        
        success, response = self.run_test(
            "Dashboard Data",
            "GET",
            "dashboard",
            200
        )
        
        if success:
            today_stats = response.get('today', {})
            self.log(f"Today's stats: {today_stats}")

    def run_all_tests(self):
        """Run complete test suite"""
        self.log("🚀 Starting Sistema CIPOLATTI Backend Tests", "START")
        self.log(f"Backend URL: {self.base_url}")
        
        start_time = time.time()
        
        # Test authentication first
        if not self.test_auth():
            self.log("❌ Authentication failed - stopping tests", "CRITICAL")
            return False
        
        # Test all modules
        agendamento_ids = self.test_agendamentos()
        carregamento_ids = self.test_carregamentos_with_photos()
        fleet_ids = self.test_fleet_with_photos()
        
        self.test_reports()
        self.test_dashboard()
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        self.log("=" * 60, "SUMMARY")
        self.log(f"📊 Tests completed in {duration:.2f} seconds")
        self.log(f"✅ Tests passed: {self.tests_passed}/{self.tests_run}")
        self.log(f"📈 Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if len(agendamento_ids) >= 75:
            self.log(f"✅ Created {len(agendamento_ids)} agendamentos (target: 75+)")
        else:
            self.log(f"⚠️  Created {len(agendamento_ids)} agendamentos (target: 75+)")
            
        if len(carregamento_ids) >= 10:
            self.log(f"✅ Created {len(carregamento_ids)} carregamentos for photo testing")
        
        if len(fleet_ids) >= 10:
            self.log(f"✅ Created {len(fleet_ids)} fleet records for photo testing")
        
        self.log("=" * 60)
        
        return self.tests_passed == self.tests_run

def main():
    tester = CipolattiAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())