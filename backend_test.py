#!/usr/bin/env python3
"""
Backend API Testing for Portaria Access Control System
Tests all endpoints with proper authentication and role-based access
"""

import requests
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class PortariaAPITester:
    def __init__(self, base_url: str = "https://cipo-v1.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.admin_credentials = {"email": "admin@cipolatti.com", "password": "admin123"}
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.user_data = None

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")
        if success:
            self.tests_passed += 1
        else:
            self.failed_tests.append({"name": name, "details": details})

    def make_request(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> tuple:
        """Make HTTP request and return success status and response"""
        url = f"{self.base_url}/api/{endpoint}"
        try:
            if method == 'GET':
                response = self.session.get(url)
            elif method == 'POST':
                response = self.session.post(url, json=data)
            elif method == 'PUT':
                response = self.session.put(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"status_code": response.status_code, "text": response.text[:200]}
            
            return success, response_data
        except Exception as e:
            return False, {"error": str(e)}

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test login with correct credentials
        success, response = self.make_request('POST', 'auth/login', self.admin_credentials)
        if success and 'email' in response:
            self.user_data = response
            self.log_test("Admin Login", True, f"Logged in as {response.get('name', 'Admin')}")
        else:
            self.log_test("Admin Login", False, f"Response: {response}")
            return False

        # Test /auth/me endpoint
        success, response = self.make_request('GET', 'auth/me')
        self.log_test("Get Current User", success, f"User: {response.get('name', 'Unknown')}" if success else str(response))

        # Test login with wrong credentials
        success, response = self.make_request('POST', 'auth/login', 
                                            {"email": "wrong@email.com", "password": "wrong"}, 
                                            expected_status=401)
        self.log_test("Invalid Login Rejection", success, "Correctly rejected invalid credentials" if success else str(response))

        return True

    def test_dashboard_endpoint(self):
        """Test dashboard endpoint"""
        print("\n📊 Testing Dashboard Endpoint...")
        
        success, response = self.make_request('GET', 'dashboard')
        if success:
            required_keys = ['today', 'week', 'recent_visitors', 'recent_fleet', 'fleet_out']
            has_all_keys = all(key in response for key in required_keys)
            self.log_test("Dashboard Data Structure", has_all_keys, 
                         f"Has keys: {list(response.keys())}" if has_all_keys else f"Missing keys from: {required_keys}")
            
            # Check today stats
            today_stats = response.get('today', {})
            expected_today_keys = ['visitors', 'employees', 'directors', 'fleet_in_use', 'fleet_returned']
            has_today_stats = all(key in today_stats for key in expected_today_keys)
            self.log_test("Dashboard Today Stats", has_today_stats, 
                         f"Today stats: {today_stats}" if has_today_stats else f"Missing today keys")
        else:
            self.log_test("Dashboard Endpoint", False, str(response))

    def test_visitors_endpoints(self):
        """Test visitors CRUD operations"""
        print("\n👥 Testing Visitors Endpoints...")
        
        # Create visitor
        visitor_data = {
            "nome": "João Silva",
            "placa": "ABC-1234",
            "veiculo": "Honda Civic",
            "observacao": "Visitante teste"
        }
        success, response = self.make_request('POST', 'visitors', visitor_data, expected_status=200)
        visitor_id = None
        if success and 'id' in response:
            visitor_id = response['id']
            self.log_test("Create Visitor", True, f"Created visitor ID: {visitor_id}")
        else:
            self.log_test("Create Visitor", False, str(response))

        # List visitors
        success, response = self.make_request('GET', 'visitors')
        if success and 'items' in response:
            self.log_test("List Visitors", True, f"Found {len(response['items'])} visitors")
        else:
            self.log_test("List Visitors", False, str(response))

        # Get specific visitor
        if visitor_id:
            success, response = self.make_request('GET', f'visitors/{visitor_id}')
            self.log_test("Get Visitor by ID", success, f"Visitor: {response.get('nome', 'Unknown')}" if success else str(response))

            # Update visitor (add exit time)
            update_data = {"hora_saida": "18:30"}
            success, response = self.make_request('PUT', f'visitors/{visitor_id}', update_data)
            self.log_test("Update Visitor", success, f"Updated exit time" if success else str(response))

    def test_fleet_endpoints(self):
        """Test fleet CRUD operations"""
        print("\n🚗 Testing Fleet Endpoints...")
        
        # Create fleet record
        fleet_data = {
            "carro": "Toyota Corolla",
            "placa": "XYZ-5678",
            "motorista": "Carlos Santos",
            "destino": "Centro da cidade",
            "km_saida": 15000.5,
            "observacao": "Viagem de negócios"
        }
        success, response = self.make_request('POST', 'fleet', fleet_data, expected_status=200)
        fleet_id = None
        if success and 'id' in response:
            fleet_id = response['id']
            self.log_test("Create Fleet Record", True, f"Created fleet ID: {fleet_id}")
        else:
            self.log_test("Create Fleet Record", False, str(response))

        # List fleet
        success, response = self.make_request('GET', 'fleet')
        if success and 'items' in response:
            self.log_test("List Fleet", True, f"Found {len(response['items'])} fleet records")
        else:
            self.log_test("List Fleet", False, str(response))

        # Return fleet vehicle
        if fleet_id:
            return_data = {
                "km_retorno": 15050.0,
                "observacao": "Retorno sem problemas"
            }
            success, response = self.make_request('POST', f'fleet/{fleet_id}/return', return_data)
            self.log_test("Return Fleet Vehicle", success, f"Vehicle returned" if success else str(response))

    def test_employees_endpoints(self):
        """Test employees CRUD operations"""
        print("\n👨‍💼 Testing Employees Endpoints...")
        
        # Create employee record
        employee_data = {
            "nome": "Maria Oliveira",
            "setor": "TI",
            "responsavel": "João Manager",
            "autorizado": True,
            "placa": "DEF-9012",
            "observacao": "Funcionária do setor de TI"
        }
        success, response = self.make_request('POST', 'employees', employee_data, expected_status=200)
        employee_id = None
        if success and 'id' in response:
            employee_id = response['id']
            self.log_test("Create Employee Record", True, f"Created employee ID: {employee_id}")
        else:
            self.log_test("Create Employee Record", False, str(response))

        # List employees
        success, response = self.make_request('GET', 'employees')
        if success and 'items' in response:
            self.log_test("List Employees", True, f"Found {len(response['items'])} employee records")
        else:
            self.log_test("List Employees", False, str(response))

        # Update employee (add exit time)
        if employee_id:
            update_data = {"hora_saida": "17:00"}
            success, response = self.make_request('PUT', f'employees/{employee_id}', update_data)
            self.log_test("Update Employee", success, f"Updated exit time" if success else str(response))

    def test_directors_endpoints(self):
        """Test directors CRUD operations"""
        print("\n👑 Testing Directors Endpoints...")
        
        # Create director record
        director_data = {
            "nome": "Dr. Roberto Silva",
            "placa": "GHI-3456",
            "carro": "BMW X5",
            "observacao": "Diretor executivo"
        }
        success, response = self.make_request('POST', 'directors', director_data, expected_status=200)
        director_id = None
        if success and 'id' in response:
            director_id = response['id']
            self.log_test("Create Director Record", True, f"Created director ID: {director_id}")
        else:
            self.log_test("Create Director Record", False, str(response))

        # List directors
        success, response = self.make_request('GET', 'directors')
        if success and 'items' in response:
            self.log_test("List Directors", True, f"Found {len(response['items'])} director records")
        else:
            self.log_test("List Directors", False, str(response))

        # Update director (add exit time)
        if director_id:
            update_data = {"hora_saida": "19:00"}
            success, response = self.make_request('PUT', f'directors/{director_id}', update_data)
            self.log_test("Update Director", success, f"Updated exit time" if success else str(response))

    def test_carregamentos_endpoints(self):
        """Test carregamentos CRUD operations"""
        print("\n🚛 Testing Carregamentos Endpoints...")
        
        # Create carregamento record
        carregamento_data = {
            "placa_carreta": "ABC1234",
            "placa_cavalo": "XYZ5678",
            "cubagem": "50m³",
            "motorista": "José Silva",
            "empresa_terceirizada": "Transportes ABC",
            "destino": "Shopping Center Norte",
            "observacao": "Carregamento teste"
        }
        success, response = self.make_request('POST', 'carregamentos', carregamento_data, expected_status=200)
        carregamento_id = None
        if success and 'id' in response:
            carregamento_id = response['id']
            self.log_test("Create Carregamento Record", True, f"Created carregamento ID: {carregamento_id}")
        else:
            self.log_test("Create Carregamento Record", False, str(response))

        # List carregamentos
        success, response = self.make_request('GET', 'carregamentos')
        if success and 'items' in response:
            self.log_test("List Carregamentos", True, f"Found {len(response['items'])} carregamento records")
        else:
            self.log_test("List Carregamentos", False, str(response))

        # Update carregamento (add exit time)
        if carregamento_id:
            update_data = {"hora_saida": "16:30"}
            success, response = self.make_request('PUT', f'carregamentos/{carregamento_id}', update_data)
            self.log_test("Update Carregamento", success, f"Updated exit time" if success else str(response))

    def test_agendamentos_endpoints(self):
        """Test agendamentos CRUD operations"""
        print("\n📅 Testing Agendamentos Endpoints...")
        
        # Create carregamento agendamento
        agendamento_data = {
            "tipo": "carregamento",
            "data_prevista": "2024-12-20",
            "hora_prevista": "14:00",
            "placa_carreta": "TEST1234",
            "placa_cavalo": "TEST5678",
            "motorista": "Carlos Teste",
            "empresa_terceirizada": "Empresa Teste",
            "destino": "Shopping Teste",
            "observacao": "Agendamento teste"
        }
        success, response = self.make_request('POST', 'agendamentos', agendamento_data, expected_status=200)
        agendamento_id = None
        if success and 'id' in response:
            agendamento_id = response['id']
            self.log_test("Create Agendamento", True, f"Created agendamento ID: {agendamento_id}")
        else:
            self.log_test("Create Agendamento", False, str(response))

        # List agendamentos
        success, response = self.make_request('GET', 'agendamentos')
        if success and 'items' in response:
            self.log_test("List Agendamentos", True, f"Found {len(response['items'])} agendamento records")
        else:
            self.log_test("List Agendamentos", False, str(response))

        # Test dar entrada endpoint
        if agendamento_id:
            success, response = self.make_request('POST', f'agendamentos/{agendamento_id}/dar-entrada')
            self.log_test("Dar Entrada Agendamento", success, f"Entrada processed" if success else str(response))

    def test_uppercase_conversion(self):
        """Test automatic uppercase conversion for license plates"""
        print("\n🔤 Testing Uppercase Conversion...")
        
        # Test visitor with lowercase plate
        visitor_data = {
            "nome": "teste uppercase",
            "placa": "abc1234",
            "veiculo": "teste car",
            "observacao": "Teste conversão"
        }
        success, response = self.make_request('POST', 'visitors', visitor_data, expected_status=200)
        if success:
            # Check if plate was converted to uppercase
            plate_converted = response.get('placa') == 'ABC1234'
            name_converted = response.get('nome') == 'TESTE UPPERCASE'
            self.log_test("Uppercase Conversion - Visitor", plate_converted and name_converted, 
                         f"Plate: {response.get('placa')}, Name: {response.get('nome')}")
        else:
            self.log_test("Uppercase Conversion - Visitor", False, str(response))

    def test_reports_endpoints(self):
        """Test reports endpoints"""
        print("\n📋 Testing Reports Endpoints...")
        
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Test visitors report
        success, response = self.make_request('GET', f'reports/visitors?data_inicio={yesterday}&data_fim={today}')
        if success and 'items' in response:
            self.log_test("Visitors Report", True, f"Report has {len(response['items'])} visitors")
        else:
            self.log_test("Visitors Report", False, str(response))

        # Test fleet report
        success, response = self.make_request('GET', f'reports/fleet?data_inicio={yesterday}&data_fim={today}')
        if success and 'items' in response:
            self.log_test("Fleet Report", True, f"Report has {len(response['items'])} fleet records")
        else:
            self.log_test("Fleet Report", False, str(response))

        # Test employees report
        success, response = self.make_request('GET', f'reports/employees?data_inicio={yesterday}&data_fim={today}')
        if success and 'items' in response:
            self.log_test("Employees Report", True, f"Report has {len(response['items'])} employee records")
        else:
            self.log_test("Employees Report", False, str(response))

        # Test directors report
        success, response = self.make_request('GET', f'reports/directors?data_inicio={yesterday}&data_fim={today}')
        if success and 'items' in response:
            self.log_test("Directors Report", True, f"Report has {len(response['items'])} director records")
        else:
            self.log_test("Directors Report", False, str(response))
        """Test reports endpoints"""
        print("\n📋 Testing Reports Endpoints...")
        
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Test visitors report
        success, response = self.make_request('GET', f'reports/visitors?data_inicio={yesterday}&data_fim={today}')
        if success and 'items' in response:
            self.log_test("Visitors Report", True, f"Report has {len(response['items'])} visitors")
        else:
            self.log_test("Visitors Report", False, str(response))

        # Test fleet report
        success, response = self.make_request('GET', f'reports/fleet?data_inicio={yesterday}&data_fim={today}')
        if success and 'items' in response:
            self.log_test("Fleet Report", True, f"Report has {len(response['items'])} fleet records")
        else:
            self.log_test("Fleet Report", False, str(response))

        # Test employees report
        success, response = self.make_request('GET', f'reports/employees?data_inicio={yesterday}&data_fim={today}')
        if success and 'items' in response:
            self.log_test("Employees Report", True, f"Report has {len(response['items'])} employee records")
        else:
            self.log_test("Employees Report", False, str(response))

        # Test directors report
        success, response = self.make_request('GET', f'reports/directors?data_inicio={yesterday}&data_fim={today}')
        if success and 'items' in response:
            self.log_test("Directors Report", True, f"Report has {len(response['items'])} director records")
        else:
            self.log_test("Directors Report", False, str(response))

    def test_user_management_endpoints(self):
        """Test user management endpoints (admin only)"""
        print("\n👤 Testing User Management Endpoints...")
        
        # List users
        success, response = self.make_request('GET', 'users')
        if success and isinstance(response, list):
            self.log_test("List Users", True, f"Found {len(response)} users")
        else:
            self.log_test("List Users", False, str(response))

        # Create test user
        user_data = {
            "email": "test@portaria.com",
            "password": "test123",
            "name": "Test User",
            "role": "portaria"
        }
        success, response = self.make_request('POST', 'users', user_data, expected_status=200)
        test_user_id = None
        if success and 'id' in response:
            test_user_id = response['id']
            self.log_test("Create User", True, f"Created user ID: {test_user_id}")
        else:
            self.log_test("Create User", False, str(response))

        # Update user
        if test_user_id:
            update_data = {"name": "Updated Test User"}
            success, response = self.make_request('PUT', f'users/{test_user_id}', update_data)
            self.log_test("Update User", success, f"Updated user name" if success else str(response))

            # Delete test user
            success, response = self.make_request('DELETE', f'users/{test_user_id}')
            self.log_test("Delete User", success, f"User deleted" if success else str(response))

    def test_logout(self):
        """Test logout endpoint"""
        print("\n🚪 Testing Logout...")
        
        success, response = self.make_request('POST', 'auth/logout')
        self.log_test("Logout", success, "Successfully logged out" if success else str(response))

    def run_all_tests(self):
        """Run all test suites"""
        print("🧪 Starting Portaria Access Control API Tests")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)

        # Authentication is required for all other tests
        if not self.test_auth_endpoints():
            print("❌ Authentication failed - stopping tests")
            return False

        # Run all test suites
        self.test_dashboard_endpoint()
        self.test_visitors_endpoints()
        self.test_fleet_endpoints()
        self.test_employees_endpoints()
        self.test_directors_endpoints()
        self.test_carregamentos_endpoints()
        self.test_agendamentos_endpoints()
        self.test_uppercase_conversion()
        self.test_reports_endpoints()
        self.test_user_management_endpoints()
        self.test_logout()

        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests ({len(self.failed_tests)}):")
            for test in self.failed_tests:
                print(f"  - {test['name']}: {test['details']}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"✅ Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 80  # Consider 80%+ as passing

def main():
    tester = PortariaAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())