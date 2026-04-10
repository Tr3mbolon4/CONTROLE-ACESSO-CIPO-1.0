#!/usr/bin/env python3
"""
Backend API Testing for Sistema de Controle de Acesso CIPOLATTI
Tests all major API endpoints and functionality
"""

import requests
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class CipolattiAPITester:
    def __init__(self, base_url: str = "https://controle-acesso-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.user_token = None
        
        # Test credentials from the system
        self.admin_email = "admin@portaria.com"
        self.admin_password = "admin123"

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED {details}")
        else:
            self.failed_tests.append({"name": name, "details": details})
            print(f"❌ {name}: FAILED {details}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> tuple:
        """Make HTTP request and return success status and response"""
        url = f"{self.base_url}/api{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"status_code": response.status_code, "text": response.text[:200]}
            
            return success, response_data
            
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}

    def test_auth_login(self) -> bool:
        """Test admin login functionality"""
        print("\n🔐 Testing Authentication...")
        
        # Test login
        success, response = self.make_request(
            'POST', 
            '/auth/login',
            {"email": self.admin_email, "password": self.admin_password}
        )
        
        if success and response.get("email") == self.admin_email:
            self.log_test("Admin Login", True, f"Logged in as {response.get('name', 'Admin')}")
            return True
        else:
            self.log_test("Admin Login", False, f"Response: {response}")
            return False

    def test_auth_me(self) -> bool:
        """Test getting current user info"""
        success, response = self.make_request('GET', '/auth/me')
        
        if success and response.get("email") == self.admin_email:
            self.log_test("Get Current User", True, f"User: {response.get('name')}")
            return True
        else:
            self.log_test("Get Current User", False, f"Response: {response}")
            return False

    def test_visitors_crud(self) -> bool:
        """Test visitors CRUD operations"""
        print("\n👥 Testing Visitors API...")
        
        # Create visitor
        visitor_data = {
            "nome": "TESTE VISITANTE",
            "placa": "TEST123",
            "veiculo": "CARRO TESTE",
            "observacao": "Teste automatizado"
        }
        
        success, response = self.make_request('POST', '/visitors', visitor_data, 200)
        if not success:
            self.log_test("Create Visitor", False, f"Response: {response}")
            return False
        
        visitor_id = response.get("id")
        if not visitor_id:
            self.log_test("Create Visitor", False, "No ID returned")
            return False
        
        self.log_test("Create Visitor", True, f"Created visitor ID: {visitor_id}")
        
        # List visitors
        success, response = self.make_request('GET', '/visitors')
        if success and isinstance(response.get("items"), list):
            self.log_test("List Visitors", True, f"Found {len(response['items'])} visitors")
        else:
            self.log_test("List Visitors", False, f"Response: {response}")
        
        # Get specific visitor
        success, response = self.make_request('GET', f'/visitors/{visitor_id}')
        if success and response.get("nome") == "TESTE VISITANTE":
            self.log_test("Get Visitor", True, f"Retrieved visitor: {response.get('nome')}")
        else:
            self.log_test("Get Visitor", False, f"Response: {response}")
        
        # Update visitor (register exit)
        update_data = {"hora_saida": "18:00"}
        success, response = self.make_request('PUT', f'/visitors/{visitor_id}', update_data)
        if success and response.get("hora_saida") == "18:00":
            self.log_test("Update Visitor (Exit)", True, "Exit time registered")
        else:
            self.log_test("Update Visitor (Exit)", False, f"Response: {response}")
        
        # Delete visitor (admin only)
        success, response = self.make_request('DELETE', f'/visitors/{visitor_id}', expected_status=200)
        if success:
            self.log_test("Delete Visitor", True, "Visitor deleted")
        else:
            self.log_test("Delete Visitor", False, f"Response: {response}")
        
        return True

    def test_agendamentos_crud(self) -> bool:
        """Test agendamentos (scheduling) CRUD operations"""
        print("\n📅 Testing Agendamentos API...")
        
        # Create visitor scheduling
        today = datetime.now().strftime("%Y-%m-%d")
        agendamento_data = {
            "tipo": "visitante",
            "data_prevista": today,
            "hora_prevista": "14:00",
            "nome": "VISITANTE AGENDADO",
            "placa": "AGD123",
            "observacao": "Teste de agendamento"
        }
        
        success, response = self.make_request('POST', '/agendamentos', agendamento_data, 200)
        if not success:
            self.log_test("Create Agendamento", False, f"Response: {response}")
            return False
        
        agendamento_id = response.get("id")
        if not agendamento_id:
            self.log_test("Create Agendamento", False, "No ID returned")
            return False
        
        self.log_test("Create Agendamento", True, f"Created agendamento ID: {agendamento_id}")
        
        # List agendamentos
        success, response = self.make_request('GET', '/agendamentos')
        if success and isinstance(response.get("items"), list):
            self.log_test("List Agendamentos", True, f"Found {len(response['items'])} agendamentos")
        else:
            self.log_test("List Agendamentos", False, f"Response: {response}")
        
        # Test dar entrada (convert scheduling to active record)
        success, response = self.make_request('POST', f'/agendamentos/{agendamento_id}/dar-entrada', expected_status=200)
        if success and response.get("message"):
            self.log_test("Dar Entrada Agendamento", True, f"Entry registered: {response.get('tipo')}")
        else:
            self.log_test("Dar Entrada Agendamento", False, f"Response: {response}")
        
        return True

    def test_carregamentos_crud(self) -> bool:
        """Test carregamentos (loading) CRUD operations"""
        print("\n🚛 Testing Carregamentos API...")
        
        carregamento_data = {
            "placa_carreta": "CAR123",
            "placa_cavalo": "CAV456",
            "cubagem": "50m³",
            "motorista": "MOTORISTA TESTE",
            "empresa_terceirizada": "EMPRESA TESTE LTDA",
            "destino": "SHOPPING TESTE",
            "observacao": "Teste automatizado"
        }
        
        success, response = self.make_request('POST', '/carregamentos', carregamento_data, 200)
        if not success:
            self.log_test("Create Carregamento", False, f"Response: {response}")
            return False
        
        carregamento_id = response.get("id")
        if not carregamento_id:
            self.log_test("Create Carregamento", False, "No ID returned")
            return False
        
        self.log_test("Create Carregamento", True, f"Created carregamento ID: {carregamento_id}")
        
        # List carregamentos
        success, response = self.make_request('GET', '/carregamentos')
        if success and isinstance(response.get("items"), list):
            self.log_test("List Carregamentos", True, f"Found {len(response['items'])} carregamentos")
        else:
            self.log_test("List Carregamentos", False, f"Response: {response}")
        
        # Update carregamento (register exit)
        update_data = {"hora_saida": "17:30"}
        success, response = self.make_request('PUT', f'/carregamentos/{carregamento_id}', update_data)
        if success and response.get("status") == "finalizado":
            self.log_test("Update Carregamento (Exit)", True, "Exit registered, status: finalizado")
        else:
            self.log_test("Update Carregamento (Exit)", False, f"Response: {response}")
        
        return True

    def test_employees_crud(self) -> bool:
        """Test employees CRUD operations"""
        print("\n👷 Testing Employees API...")
        
        employee_data = {
            "nome": "FUNCIONARIO TESTE",
            "setor": "TI",
            "responsavel": "GESTOR TESTE",
            "autorizado": True,
            "placa": "FUN123",
            "observacao": "Teste automatizado"
        }
        
        success, response = self.make_request('POST', '/employees', employee_data, 200)
        if not success:
            self.log_test("Create Employee", False, f"Response: {response}")
            return False
        
        employee_id = response.get("id")
        if not employee_id:
            self.log_test("Create Employee", False, "No ID returned")
            return False
        
        self.log_test("Create Employee", True, f"Created employee ID: {employee_id}")
        
        # List employees
        success, response = self.make_request('GET', '/employees')
        if success and isinstance(response.get("items"), list):
            self.log_test("List Employees", True, f"Found {len(response['items'])} employees")
        else:
            self.log_test("List Employees", False, f"Response: {response}")
        
        # Update employee (register exit)
        update_data = {"hora_saida": "18:00"}
        success, response = self.make_request('PUT', f'/employees/{employee_id}', update_data)
        if success and response.get("hora_saida") == "18:00":
            self.log_test("Update Employee (Exit)", True, "Exit time registered")
        else:
            self.log_test("Update Employee (Exit)", False, f"Response: {response}")
        
        return True

    def test_directors_crud(self) -> bool:
        """Test directors CRUD operations"""
        print("\n👔 Testing Directors API...")
        
        director_data = {
            "nome": "DIRETOR TESTE",
            "placa": "DIR123",
            "carro": "BMW X5",
            "observacao": "Teste automatizado"
        }
        
        success, response = self.make_request('POST', '/directors', director_data, 200)
        if not success:
            self.log_test("Create Director", False, f"Response: {response}")
            return False
        
        director_id = response.get("id")
        if not director_id:
            self.log_test("Create Director", False, "No ID returned")
            return False
        
        self.log_test("Create Director", True, f"Created director ID: {director_id}")
        
        # List directors
        success, response = self.make_request('GET', '/directors')
        if success and isinstance(response.get("items"), list):
            self.log_test("List Directors", True, f"Found {len(response['items'])} directors")
        else:
            self.log_test("List Directors", False, f"Response: {response}")
        
        # Test lunch break functionality
        update_data = {"hora_saida_almoco": "12:00"}
        success, response = self.make_request('PUT', f'/directors/{director_id}', update_data)
        if success and response.get("hora_saida_almoco") == "12:00":
            self.log_test("Director Lunch Break", True, "Lunch break registered")
        else:
            self.log_test("Director Lunch Break", False, f"Response: {response}")
        
        # Test lunch return
        update_data = {"hora_retorno_almoco": "13:00"}
        success, response = self.make_request('PUT', f'/directors/{director_id}', update_data)
        if success and response.get("hora_retorno_almoco") == "13:00":
            self.log_test("Director Lunch Return", True, "Lunch return registered")
        else:
            self.log_test("Director Lunch Return", False, f"Response: {response}")
        
        return True

    def test_fleet_crud(self) -> bool:
        """Test fleet CRUD operations"""
        print("\n🚗 Testing Fleet API...")
        
        fleet_data = {
            "carro": "FIAT STRADA",
            "placa": "FLT123",
            "motorista": "MOTORISTA FROTA",
            "destino": "CLIENTE TESTE",
            "km_saida": 50000.0,
            "observacao": "Teste automatizado"
        }
        
        success, response = self.make_request('POST', '/fleet', fleet_data, 200)
        if not success:
            self.log_test("Create Fleet Record", False, f"Response: {response}")
            return False
        
        fleet_id = response.get("id")
        if not fleet_id:
            self.log_test("Create Fleet Record", False, "No ID returned")
            return False
        
        self.log_test("Create Fleet Record", True, f"Created fleet ID: {fleet_id}")
        
        # List fleet
        success, response = self.make_request('GET', '/fleet')
        if success and isinstance(response.get("items"), list):
            self.log_test("List Fleet", True, f"Found {len(response['items'])} fleet records")
        else:
            self.log_test("List Fleet", False, f"Response: {response}")
        
        # Test return functionality
        return_data = {
            "km_retorno": 50150.0,
            "observacao": "Retorno teste"
        }
        success, response = self.make_request('POST', f'/fleet/{fleet_id}/return', return_data)
        if success and response.get("status") == "retornado":
            km_rodado = response.get("km_rodado", 0)
            self.log_test("Fleet Return", True, f"Vehicle returned, KM driven: {km_rodado}")
        else:
            self.log_test("Fleet Return", False, f"Response: {response}")
        
        return True

    def test_dashboard(self) -> bool:
        """Test dashboard API"""
        print("\n📊 Testing Dashboard API...")
        
        success, response = self.make_request('GET', '/dashboard')
        if success and "today" in response:
            today_stats = response.get("today", {})
            self.log_test("Dashboard", True, 
                f"Today: {today_stats.get('visitors', 0)} visitors, "
                f"{today_stats.get('employees', 0)} employees, "
                f"{today_stats.get('fleet_in_use', 0)} fleet in use")
        else:
            self.log_test("Dashboard", False, f"Response: {response}")
        
        return success

    def test_reports(self) -> bool:
        """Test reports API"""
        print("\n📋 Testing Reports API...")
        
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Test visitors report
        success, response = self.make_request('GET', f'/reports/visitors?data_inicio={yesterday}&data_fim={today}')
        if success and "items" in response:
            self.log_test("Visitors Report", True, f"Found {len(response['items'])} visitor records")
        else:
            self.log_test("Visitors Report", False, f"Response: {response}")
        
        # Test fleet report
        success, response = self.make_request('GET', f'/reports/fleet?data_inicio={yesterday}&data_fim={today}')
        if success and "items" in response:
            total_km = response.get("total_km", 0)
            self.log_test("Fleet Report", True, f"Found {len(response['items'])} fleet records, Total KM: {total_km}")
        else:
            self.log_test("Fleet Report", False, f"Response: {response}")
        
        # Test employees report
        success, response = self.make_request('GET', f'/reports/employees?data_inicio={yesterday}&data_fim={today}')
        if success and "items" in response:
            self.log_test("Employees Report", True, f"Found {len(response['items'])} employee records")
        else:
            self.log_test("Employees Report", False, f"Response: {response}")
        
        # Test directors report
        success, response = self.make_request('GET', f'/reports/directors?data_inicio={yesterday}&data_fim={today}')
        if success and "items" in response:
            self.log_test("Directors Report", True, f"Found {len(response['items'])} director records")
        else:
            self.log_test("Directors Report", False, f"Response: {response}")
        
        return True

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🚀 Starting CIPOLATTI Access Control System API Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Authentication is required for all other tests
        if not self.test_auth_login():
            print("\n❌ Authentication failed - cannot continue with other tests")
            return self.get_results()
        
        # Test current user endpoint
        self.test_auth_me()
        
        # Test all CRUD operations
        self.test_visitors_crud()
        self.test_agendamentos_crud()
        self.test_carregamentos_crud()
        self.test_employees_crud()
        self.test_directors_crud()
        self.test_fleet_crud()
        
        # Test dashboard and reports
        self.test_dashboard()
        self.test_reports()
        
        return self.get_results()

    def get_results(self) -> Dict[str, Any]:
        """Get test results summary"""
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        results = {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "failed_tests": len(self.failed_tests),
            "success_rate": round(success_rate, 2),
            "failed_test_details": self.failed_tests
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run} ({success_rate:.1f}%)")
        
        if self.failed_tests:
            print(f"❌ Failed Tests: {len(self.failed_tests)}")
            for failed in self.failed_tests:
                print(f"   - {failed['name']}: {failed['details']}")
        
        return results

def main():
    """Main test execution"""
    tester = CipolattiAPITester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if results["failed_tests"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())