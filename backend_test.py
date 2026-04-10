#!/usr/bin/env python3
"""
CIPOLATTI Access Control System - Backend API Testing
Tests all backend APIs including authentication, CRUD operations, and photo uploads
"""

import requests
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import io
import os

class CIPOLATTIAPITester:
    def __init__(self, base_url="https://cipo-access.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.user_token = None
        
        # Test data storage
        self.created_ids = {
            'agendamentos': [],
            'carregamentos': [],
            'fleet': [],
            'visitors': [],
            'employees': [],
            'directors': []
        }

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        self.tests_run += 1
        
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                if files:
                    # For file uploads, don't set content-type header
                    headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
                    response = requests.post(url, files=files, data=data, headers=headers, cookies=self.session.cookies)
                else:
                    response = self.session.post(url, json=data, params=params)
            elif method == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method == 'DELETE':
                response = self.session.delete(url, params=params)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    self.log(f"   Error: {error_detail}")
                except:
                    self.log(f"   Error: {response.text}")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Exception: {str(e)}")
            self.failed_tests.append(f"{name}: Exception - {str(e)}")
            return False, {}

    def test_auth_login(self):
        """Test login with admin credentials"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@portaria.com", "password": "admin123"}
        )
        if success:
            self.log("✅ Login successful - Admin authenticated")
            return True
        return False

    def test_auth_me(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        if success and response.get('role') == 'admin':
            self.log(f"✅ User info retrieved - Role: {response.get('role')}")
            return True
        return False

    def test_dashboard(self):
        """Test dashboard endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard",
            200
        )
        if success:
            today_stats = response.get('today', {})
            self.log(f"✅ Dashboard loaded - Visitors today: {today_stats.get('visitors', 0)}")
            return True
        return False

    def create_agendamentos_bulk(self, count=15):
        """Create multiple agendamentos of different types"""
        tipos = ['carregamento', 'visitante', 'funcionario', 'diretoria', 'frota']
        created_count = 0
        
        for i in range(count):
            tipo = tipos[i % len(tipos)]
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            base_data = {
                "tipo": tipo,
                "data_prevista": tomorrow,
                "hora_prevista": f"{8 + (i % 10)}:00",
                "observacao": f"Teste agendamento {i+1} - {tipo}"
            }
            
            # Add specific fields based on type
            if tipo == 'carregamento':
                base_data.update({
                    "placa_carreta": f"CAR{i:04d}",
                    "placa_cavalo": f"CAV{i:04d}",
                    "motorista": f"MOTORISTA TESTE {i+1}",
                    "empresa_terceirizada": f"EMPRESA TESTE {i+1}",
                    "destino": f"SHOPPING TESTE {i+1}",
                    "cubagem": f"{50 + i}m³"
                })
            elif tipo == 'visitante':
                base_data.update({
                    "nome": f"VISITANTE TESTE {i+1}",
                    "placa": f"VIS{i:04d}"
                })
            elif tipo == 'funcionario':
                base_data.update({
                    "nome": f"FUNCIONARIO TESTE {i+1}",
                    "setor": f"SETOR {i+1}",
                    "responsavel": f"RESPONSAVEL {i+1}",
                    "tipo_permissao": "saida_antecipada" if i % 2 == 0 else "entrada_atrasada",
                    "hora_permitida": f"{16 + (i % 3)}:00",
                    "placa": f"FUN{i:04d}"
                })
            elif tipo == 'diretoria':
                base_data.update({
                    "nome": f"DIRETOR TESTE {i+1}",
                    "placa": f"DIR{i:04d}"
                })
            elif tipo == 'frota':
                base_data.update({
                    "carro": f"FIAT STRADA {i+1}",
                    "placa": f"FRT{i:04d}",
                    "motorista": f"MOTORISTA FROTA {i+1}",
                    "destino": f"DESTINO {i+1}",
                    "km_saida": 10000 + (i * 100)
                })
            
            success, response = self.run_test(
                f"Create Agendamento {tipo} #{i+1}",
                "POST",
                "agendamentos",
                200,
                data=base_data
            )
            
            if success and response.get('id'):
                self.created_ids['agendamentos'].append(response['id'])
                created_count += 1
        
        self.log(f"✅ Created {created_count}/{count} agendamentos")
        return created_count == count

    def test_dar_entrada_carregamentos(self):
        """Test giving entry to carregamento agendamentos"""
        # Get carregamento agendamentos
        success, response = self.run_test(
            "List Carregamento Agendamentos",
            "GET",
            "agendamentos",
            200,
            params={"tipo": "carregamento", "status": "pendente"}
        )
        
        if not success:
            return False
            
        agendamentos = response.get('items', [])
        carregamento_agendamentos = [a for a in agendamentos if a.get('tipo') == 'carregamento'][:5]
        
        entrada_count = 0
        for ag in carregamento_agendamentos:
            success, response = self.run_test(
                f"Dar Entrada Carregamento {ag.get('id', '')[:8]}",
                "POST",
                f"agendamentos/{ag['id']}/dar-entrada",
                200
            )
            if success:
                entrada_count += 1
                if response.get('registro_id'):
                    self.created_ids['carregamentos'].append(response['registro_id'])
        
        self.log(f"✅ Processed {entrada_count} carregamento entries")
        return entrada_count > 0

    def test_dar_entrada_frota(self):
        """Test giving entry to frota agendamentos"""
        success, response = self.run_test(
            "List Frota Agendamentos",
            "GET",
            "agendamentos",
            200,
            params={"tipo": "frota", "status": "pendente"}
        )
        
        if not success:
            return False
            
        agendamentos = response.get('items', [])
        frota_agendamentos = [a for a in agendamentos if a.get('tipo') == 'frota'][:5]
        
        entrada_count = 0
        for ag in frota_agendamentos:
            success, response = self.run_test(
                f"Dar Entrada Frota {ag.get('id', '')[:8]}",
                "POST",
                f"agendamentos/{ag['id']}/dar-entrada",
                200
            )
            if success:
                entrada_count += 1
                if response.get('registro_id'):
                    self.created_ids['fleet'].append(response['registro_id'])
        
        self.log(f"✅ Processed {entrada_count} frota entries")
        return entrada_count > 0

    def test_photo_upload_carregamentos(self):
        """Test photo upload for carregamentos"""
        if not self.created_ids['carregamentos']:
            self.log("⚠️ No carregamentos available for photo testing")
            return False
            
        # Create a simple test image
        test_image = self.create_test_image()
        upload_count = 0
        
        for carregamento_id in self.created_ids['carregamentos'][:3]:  # Test first 3
            for categoria in ['geral', 'placa', 'motorista']:
                files = {'file': ('test.jpg', test_image, 'image/jpeg')}
                data = {'categoria': categoria}
                
                success, response = self.run_test(
                    f"Upload Photo Carregamento {carregamento_id[:8]} - {categoria}",
                    "POST",
                    f"carregamentos/{carregamento_id}/photos",
                    200,
                    data=data,
                    files=files
                )
                if success:
                    upload_count += 1
        
        self.log(f"✅ Uploaded {upload_count} carregamento photos")
        return upload_count > 0

    def test_photo_upload_fleet(self):
        """Test photo upload for fleet"""
        if not self.created_ids['fleet']:
            self.log("⚠️ No fleet records available for photo testing")
            return False
            
        test_image = self.create_test_image()
        upload_count = 0
        
        for fleet_id in self.created_ids['fleet'][:3]:  # Test first 3
            for categoria in ['placa', 'frente', 'lateral']:
                files = {'file': ('test.jpg', test_image, 'image/jpeg')}
                
                success, response = self.run_test(
                    f"Upload Photo Fleet {fleet_id[:8]} - {categoria}",
                    "POST",
                    f"fleet/{fleet_id}/photos",
                    200,
                    params={'category': categoria, 'moment': 'saida'},
                    files=files
                )
                if success:
                    upload_count += 1
        
        self.log(f"✅ Uploaded {upload_count} fleet photos")
        return upload_count > 0

    def test_fleet_return(self):
        """Test fleet return functionality"""
        if not self.created_ids['fleet']:
            self.log("⚠️ No fleet records available for return testing")
            return False
            
        return_count = 0
        for fleet_id in self.created_ids['fleet'][:2]:  # Return first 2
            # Get fleet details first
            success, fleet_data = self.run_test(
                f"Get Fleet {fleet_id[:8]}",
                "GET",
                f"fleet/{fleet_id}",
                200
            )
            
            if success:
                km_saida = fleet_data.get('km_saida', 10000)
                return_data = {
                    "km_retorno": km_saida + 150,  # Add 150km
                    "observacao": "Retorno teste"
                }
                
                success, response = self.run_test(
                    f"Return Fleet {fleet_id[:8]}",
                    "POST",
                    f"fleet/{fleet_id}/return",
                    200,
                    data=return_data
                )
                if success:
                    return_count += 1
        
        self.log(f"✅ Processed {return_count} fleet returns")
        return return_count > 0

    def test_carregamento_exit(self):
        """Test carregamento exit functionality"""
        if not self.created_ids['carregamentos']:
            self.log("⚠️ No carregamentos available for exit testing")
            return False
            
        exit_count = 0
        for carregamento_id in self.created_ids['carregamentos'][:2]:  # Exit first 2
            now = datetime.now()
            exit_data = {
                "hora_saida": now.strftime("%H:%M")
            }
            
            success, response = self.run_test(
                f"Exit Carregamento {carregamento_id[:8]}",
                "PUT",
                f"carregamentos/{carregamento_id}",
                200,
                data=exit_data
            )
            if success:
                exit_count += 1
        
        self.log(f"✅ Processed {exit_count} carregamento exits")
        return exit_count > 0

    def test_reports_generation(self):
        """Test report generation for all types"""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        report_types = ['visitors', 'fleet', 'employees', 'directors', 'carregamentos']
        reports_generated = 0
        
        for report_type in report_types:
            success, response = self.run_test(
                f"Generate {report_type.title()} Report",
                "GET",
                f"reports/{report_type}",
                200,
                params={
                    "data_inicio": yesterday,
                    "data_fim": today
                }
            )
            if success:
                reports_generated += 1
                items_count = len(response.get('items', []))
                self.log(f"   📊 {report_type}: {items_count} records")
        
        self.log(f"✅ Generated {reports_generated}/{len(report_types)} reports")
        return reports_generated == len(report_types)

    def create_test_image(self):
        """Create a simple test image for upload testing"""
        # Create a minimal JPEG-like binary data
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
        jpeg_data = jpeg_header + b'\x00' * 100  # Minimal JPEG structure
        jpeg_footer = b'\xff\xd9'
        return io.BytesIO(jpeg_header + jpeg_data + jpeg_footer)

    def test_list_operations(self):
        """Test listing operations for all entities"""
        endpoints = [
            ('agendamentos', 'agendamentos'),
            ('carregamentos', 'carregamentos'),
            ('fleet', 'fleet'),
            ('visitors', 'visitors'),
            ('employees', 'employees'),
            ('directors', 'directors')
        ]
        
        list_success = 0
        for name, endpoint in endpoints:
            success, response = self.run_test(
                f"List {name.title()}",
                "GET",
                endpoint,
                200
            )
            if success:
                list_success += 1
                items_count = len(response.get('items', []))
                self.log(f"   📋 {name}: {items_count} records")
        
        self.log(f"✅ Listed {list_success}/{len(endpoints)} entity types")
        return list_success == len(endpoints)

    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        self.log("🚀 Starting CIPOLATTI Backend API Testing")
        self.log("=" * 60)
        
        # Authentication Tests
        self.log("\n📋 AUTHENTICATION TESTS")
        if not self.test_auth_login():
            self.log("❌ Authentication failed - stopping tests")
            return False
            
        if not self.test_auth_me():
            self.log("❌ User info retrieval failed")
            return False
        
        # Dashboard Test
        self.log("\n📋 DASHBOARD TESTS")
        self.test_dashboard()
        
        # Create Test Data
        self.log("\n📋 AGENDAMENTO CREATION TESTS")
        self.create_agendamentos_bulk(15)
        
        # Entry Processing Tests
        self.log("\n📋 ENTRY PROCESSING TESTS")
        self.test_dar_entrada_carregamentos()
        self.test_dar_entrada_frota()
        
        # Photo Upload Tests
        self.log("\n📋 PHOTO UPLOAD TESTS")
        self.test_photo_upload_carregamentos()
        self.test_photo_upload_fleet()
        
        # Exit/Return Tests
        self.log("\n📋 EXIT/RETURN TESTS")
        self.test_carregamento_exit()
        self.test_fleet_return()
        
        # List Operations Tests
        self.log("\n📋 LIST OPERATIONS TESTS")
        self.test_list_operations()
        
        # Report Generation Tests
        self.log("\n📋 REPORT GENERATION TESTS")
        self.test_reports_generation()
        
        return True

    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "=" * 60)
        self.log("📊 TEST SUMMARY")
        self.log("=" * 60)
        self.log(f"Total Tests: {self.tests_run}")
        self.log(f"Passed: {self.tests_passed}")
        self.log(f"Failed: {len(self.failed_tests)}")
        self.log(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            self.log("\n❌ FAILED TESTS:")
            for failure in self.failed_tests:
                self.log(f"   • {failure}")
        
        # Print created IDs summary
        self.log("\n📋 CREATED TEST DATA:")
        for entity_type, ids in self.created_ids.items():
            if ids:
                self.log(f"   • {entity_type}: {len(ids)} records")
        
        return len(self.failed_tests) == 0

def main():
    """Main test execution"""
    tester = CIPOLATTIAPITester()
    
    try:
        success = tester.run_comprehensive_test()
        all_passed = tester.print_summary()
        
        return 0 if all_passed else 1
        
    except KeyboardInterrupt:
        tester.log("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        tester.log(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())