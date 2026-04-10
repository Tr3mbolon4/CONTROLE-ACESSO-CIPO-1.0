#!/usr/bin/env python3
"""
CIPOLATTI Access Control System - Backend API Test Suite
Tests all backend endpoints for functionality and integration
"""

import requests
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class CIPOLATTIAPITester:
    def __init__(self, base_url: str = "https://controle-acesso-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.tests_run = 0
        self.tests_passed = 0
        self.token = None
        self.user_data = None
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int = 200, 
                 data: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        self.tests_run += 1
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method == 'PUT':
                response = self.session.put(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}", "ERROR")
                if response.text:
                    self.log(f"   Response: {response.text[:200]}", "ERROR")
                    
            try:
                response_data = response.json() if response.text else {}
            except:
                response_data = {"raw_response": response.text}
                
            return success, response_data
            
        except Exception as e:
            self.log(f"❌ {name} - Exception: {str(e)}", "ERROR")
            return False, {"error": str(e)}
    
    def test_auth_flow(self) -> bool:
        """Test authentication endpoints"""
        self.log("=== Testing Authentication ===")
        
        # Test login
        login_data = {
            "email": "admin@portaria.com",
            "password": "admin123"
        }
        
        success, response = self.run_test("Admin Login", "POST", "auth/login", 200, login_data)
        if not success:
            return False
            
        self.user_data = response
        self.log(f"   Logged in as: {response.get('name', 'Unknown')} ({response.get('role', 'Unknown')})")
        
        # Test /auth/me
        success, response = self.run_test("Get Current User", "GET", "auth/me", 200)
        if not success:
            return False
            
        # Test refresh token
        success, response = self.run_test("Refresh Token", "POST", "auth/refresh", 200)
        
        return success
    
    def test_visitors_crud(self) -> bool:
        """Test visitors CRUD operations"""
        self.log("=== Testing Visitors CRUD ===")
        
        # Create visitor
        visitor_data = {
            "nome": "JOÃO TESTE",
            "placa": "ABC1234",
            "veiculo": "CIVIC PRETO",
            "observacao": "Teste automatizado"
        }
        
        success, response = self.run_test("Create Visitor", "POST", "visitors", 200, visitor_data)
        if not success:
            return False
            
        visitor_id = response.get("id")
        if not visitor_id:
            self.log("❌ No visitor ID returned", "ERROR")
            return False
            
        # Get visitor
        success, response = self.run_test("Get Visitor", "GET", f"visitors/{visitor_id}", 200)
        if not success:
            return False
            
        # List visitors
        success, response = self.run_test("List Visitors", "GET", "visitors", 200)
        if not success:
            return False
            
        # Update visitor (register exit)
        update_data = {"hora_saida": "18:30"}
        success, response = self.run_test("Update Visitor", "PUT", f"visitors/{visitor_id}", 200, update_data)
        if not success:
            return False
            
        # Delete visitor (admin only)
        success, response = self.run_test("Delete Visitor", "DELETE", f"visitors/{visitor_id}", 200)
        
        return success
    
    def test_agendamentos_crud(self) -> bool:
        """Test agendamentos CRUD operations"""
        self.log("=== Testing Agendamentos CRUD ===")
        
        # Create visitor agendamento
        today = datetime.now().strftime("%Y-%m-%d")
        agendamento_data = {
            "tipo": "visitante",
            "data_prevista": today,
            "hora_prevista": "16:30",
            "nome": "MARIA AGENDADA",
            "placa": "XYZ5678",
            "observacao": "Agendamento teste"
        }
        
        success, response = self.run_test("Create Agendamento", "POST", "agendamentos", 200, agendamento_data)
        if not success:
            return False
            
        agendamento_id = response.get("id")
        if not agendamento_id:
            self.log("❌ No agendamento ID returned", "ERROR")
            return False
            
        # List agendamentos
        success, response = self.run_test("List Agendamentos", "GET", "agendamentos", 200)
        if not success:
            return False
            
        # Get specific agendamento
        success, response = self.run_test("Get Agendamento", "GET", f"agendamentos/{agendamento_id}", 200)
        if not success:
            return False
            
        # Test dar entrada (convert to active record)
        success, response = self.run_test("Dar Entrada", "POST", f"agendamentos/{agendamento_id}/dar-entrada", 200)
        if not success:
            return False
            
        # Delete agendamento
        success, response = self.run_test("Delete Agendamento", "DELETE", f"agendamentos/{agendamento_id}", 200)
        
        return success
    
    def test_carregamentos_crud(self) -> bool:
        """Test carregamentos CRUD operations"""
        self.log("=== Testing Carregamentos CRUD ===")
        
        carregamento_data = {
            "placa_carreta": "CAR1234",
            "placa_cavalo": "CAV5678",
            "cubagem": "50m³",
            "motorista": "JOSÉ MOTORISTA",
            "empresa_terceirizada": "TRANSPORTES TESTE LTDA",
            "destino": "SHOPPING CENTER NORTE",
            "observacao": "Carregamento teste"
        }
        
        success, response = self.run_test("Create Carregamento", "POST", "carregamentos", 200, carregamento_data)
        if not success:
            return False
            
        carregamento_id = response.get("id")
        if not carregamento_id:
            self.log("❌ No carregamento ID returned", "ERROR")
            return False
            
        # List carregamentos
        success, response = self.run_test("List Carregamentos", "GET", "carregamentos", 200)
        if not success:
            return False
            
        # Get carregamento
        success, response = self.run_test("Get Carregamento", "GET", f"carregamentos/{carregamento_id}", 200)
        if not success:
            return False
            
        # Update carregamento (register exit)
        update_data = {"hora_saida": "20:15"}
        success, response = self.run_test("Update Carregamento", "PUT", f"carregamentos/{carregamento_id}", 200, update_data)
        if not success:
            return False
            
        # Delete carregamento
        success, response = self.run_test("Delete Carregamento", "DELETE", f"carregamentos/{carregamento_id}", 200)
        
        return success
    
    def test_employees_crud(self) -> bool:
        """Test employees CRUD operations"""
        self.log("=== Testing Employees CRUD ===")
        
        employee_data = {
            "nome": "CARLOS FUNCIONÁRIO",
            "setor": "VENDAS",
            "responsavel": "GERENTE VENDAS",
            "autorizado": True,
            "placa": "FUN1234",
            "observacao": "Funcionário teste"
        }
        
        success, response = self.run_test("Create Employee", "POST", "employees", 200, employee_data)
        if not success:
            return False
            
        employee_id = response.get("id")
        if not employee_id:
            self.log("❌ No employee ID returned", "ERROR")
            return False
            
        # List employees
        success, response = self.run_test("List Employees", "GET", "employees", 200)
        if not success:
            return False
            
        # Get employee
        success, response = self.run_test("Get Employee", "GET", f"employees/{employee_id}", 200)
        if not success:
            return False
            
        # Update employee (register exit)
        update_data = {"hora_saida": "17:45"}
        success, response = self.run_test("Update Employee", "PUT", f"employees/{employee_id}", 200, update_data)
        if not success:
            return False
            
        # Delete employee
        success, response = self.run_test("Delete Employee", "DELETE", f"employees/{employee_id}", 200)
        
        return success
    
    def test_directors_crud(self) -> bool:
        """Test directors CRUD operations"""
        self.log("=== Testing Directors CRUD ===")
        
        director_data = {
            "nome": "ANA DIRETORA",
            "placa": "DIR1234",
            "carro": "BMW X5 PRETA",
            "observacao": "Diretora teste"
        }
        
        success, response = self.run_test("Create Director", "POST", "directors", 200, director_data)
        if not success:
            return False
            
        director_id = response.get("id")
        if not director_id:
            self.log("❌ No director ID returned", "ERROR")
            return False
            
        # List directors
        success, response = self.run_test("List Directors", "GET", "directors", 200)
        if not success:
            return False
            
        # Get director
        success, response = self.run_test("Get Director", "GET", f"directors/{director_id}", 200)
        if not success:
            return False
            
        # Update director (lunch break)
        update_data = {"hora_saida_almoco": "12:00"}
        success, response = self.run_test("Director Lunch Out", "PUT", f"directors/{director_id}", 200, update_data)
        if not success:
            return False
            
        # Update director (lunch return)
        update_data = {"hora_retorno_almoco": "13:00"}
        success, response = self.run_test("Director Lunch Return", "PUT", f"directors/{director_id}", 200, update_data)
        if not success:
            return False
            
        # Update director (final exit)
        update_data = {"hora_saida": "18:00"}
        success, response = self.run_test("Director Exit", "PUT", f"directors/{director_id}", 200, update_data)
        if not success:
            return False
            
        # Delete director
        success, response = self.run_test("Delete Director", "DELETE", f"directors/{director_id}", 200)
        
        return success
    
    def test_fleet_crud(self) -> bool:
        """Test fleet CRUD operations"""
        self.log("=== Testing Fleet CRUD ===")
        
        fleet_data = {
            "carro": "FIAT STRADA",
            "placa": "FLT1234",
            "motorista": "PEDRO MOTORISTA",
            "destino": "CLIENTE ZONA SUL",
            "km_saida": 15000.0,
            "observacao": "Viagem teste"
        }
        
        success, response = self.run_test("Create Fleet Record", "POST", "fleet", 200, fleet_data)
        if not success:
            return False
            
        fleet_id = response.get("id")
        if not fleet_id:
            self.log("❌ No fleet ID returned", "ERROR")
            return False
            
        # List fleet
        success, response = self.run_test("List Fleet", "GET", "fleet", 200)
        if not success:
            return False
            
        # Get fleet record
        success, response = self.run_test("Get Fleet Record", "GET", f"fleet/{fleet_id}", 200)
        if not success:
            return False
            
        # Return fleet
        return_data = {
            "km_retorno": 15150.0,
            "observacao": "Retorno sem problemas"
        }
        success, response = self.run_test("Return Fleet", "POST", f"fleet/{fleet_id}/return", 200, return_data)
        if not success:
            return False
            
        # Delete fleet record
        success, response = self.run_test("Delete Fleet Record", "DELETE", f"fleet/{fleet_id}", 200)
        
        return success
    
    def test_dashboard_and_reports(self) -> bool:
        """Test dashboard and reports endpoints"""
        self.log("=== Testing Dashboard & Reports ===")
        
        # Test dashboard
        success, response = self.run_test("Get Dashboard", "GET", "dashboard", 200)
        if not success:
            return False
            
        # Test reports
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        report_params = {
            "data_inicio": yesterday,
            "data_fim": today
        }
        
        success, response = self.run_test("Visitors Report", "GET", "reports/visitors", 200, params=report_params)
        if not success:
            return False
            
        success, response = self.run_test("Fleet Report", "GET", "reports/fleet", 200, params=report_params)
        if not success:
            return False
            
        success, response = self.run_test("Employees Report", "GET", "reports/employees", 200, params=report_params)
        if not success:
            return False
            
        success, response = self.run_test("Directors Report", "GET", "reports/directors", 200, params=report_params)
        
        return success
    
    def test_logout(self) -> bool:
        """Test logout"""
        self.log("=== Testing Logout ===")
        success, response = self.run_test("Logout", "POST", "auth/logout", 200)
        return success
    
    def run_all_tests(self) -> bool:
        """Run all test suites"""
        self.log("🚀 Starting CIPOLATTI Access Control System Backend Tests")
        self.log(f"   Base URL: {self.base_url}")
        
        test_suites = [
            ("Authentication", self.test_auth_flow),
            ("Visitors CRUD", self.test_visitors_crud),
            ("Agendamentos CRUD", self.test_agendamentos_crud),
            ("Carregamentos CRUD", self.test_carregamentos_crud),
            ("Employees CRUD", self.test_employees_crud),
            ("Directors CRUD", self.test_directors_crud),
            ("Fleet CRUD", self.test_fleet_crud),
            ("Dashboard & Reports", self.test_dashboard_and_reports),
            ("Logout", self.test_logout)
        ]
        
        all_passed = True
        for suite_name, test_func in test_suites:
            self.log(f"\n--- {suite_name} ---")
            if not test_func():
                all_passed = False
                self.log(f"❌ {suite_name} suite failed", "ERROR")
            else:
                self.log(f"✅ {suite_name} suite passed")
        
        # Print summary
        self.log(f"\n📊 Test Summary:")
        self.log(f"   Tests Run: {self.tests_run}")
        self.log(f"   Tests Passed: {self.tests_passed}")
        self.log(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if all_passed:
            self.log("🎉 All test suites passed!")
        else:
            self.log("❌ Some test suites failed", "ERROR")
            
        return all_passed

def main():
    tester = CIPOLATTIAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())