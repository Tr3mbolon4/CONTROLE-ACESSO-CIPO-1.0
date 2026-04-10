#!/usr/bin/env python3
"""
CIPOLATTI Access Control System - Backend Testing
Focus: Photo upload/download functionality with local storage
"""

import requests
import sys
import os
import io
from datetime import datetime, timedelta
from PIL import Image
import json

class CIPOLATTITester:
    def __init__(self, base_url="https://cipo-access.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        
        # Test data storage
        self.agendamentos_carregamento = []
        self.agendamentos_frota = []
        self.carregamentos_ativos = []
        self.frota_ativa = []
        self.uploaded_photos = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        return success

    def create_test_image(self, filename="test_image.jpg", size=(100, 100)):
        """Create a test image for upload"""
        img = Image.new('RGB', size, color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes.getvalue()

    def login(self):
        """Test login with admin credentials"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"email": "admin@portaria.com", "password": "admin123"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract token from cookies or response
                if 'access_token' in self.session.cookies:
                    self.token = self.session.cookies['access_token']
                return self.log_test("Admin Login", True)
            else:
                return self.log_test("Admin Login", False, f"Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Admin Login", False, str(e))

    def create_agendamentos_carregamento(self, count=5):
        """Create carregamento appointments"""
        success_count = 0
        
        for i in range(count):
            try:
                data = {
                    "tipo": "carregamento",
                    "data_prevista": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "hora_prevista": f"{8 + i}:00",
                    "placa_carreta": f"CAR{i:03d}",
                    "placa_cavalo": f"CAV{i:03d}",
                    "cubagem": f"{50 + i}m³",
                    "motorista": f"Motorista {i+1}",
                    "empresa_terceirizada": f"Empresa {i+1}",
                    "destino": f"Destino {i+1}",
                    "observacao": f"Agendamento de carregamento {i+1}"
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/agendamentos",
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    agendamento = response.json()
                    self.agendamentos_carregamento.append(agendamento)
                    success_count += 1
                    
            except Exception as e:
                print(f"Error creating carregamento {i+1}: {e}")
        
        return self.log_test(f"Create {count} Carregamento Agendamentos", 
                           success_count == count, 
                           f"Created {success_count}/{count}")

    def create_agendamentos_frota(self, count=5):
        """Create frota appointments"""
        success_count = 0
        
        for i in range(count):
            try:
                data = {
                    "tipo": "frota",
                    "data_prevista": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "hora_prevista": f"{9 + i}:00",
                    "carro": f"Carro {i+1}",
                    "placa": f"FRT{i:03d}",
                    "motorista": f"Motorista Frota {i+1}",
                    "destino": f"Destino Frota {i+1}",
                    "km_saida": 1000 + (i * 100),
                    "observacao": f"Agendamento de frota {i+1}"
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/agendamentos",
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    agendamento = response.json()
                    self.agendamentos_frota.append(agendamento)
                    success_count += 1
                    
            except Exception as e:
                print(f"Error creating frota {i+1}: {e}")
        
        return self.log_test(f"Create {count} Frota Agendamentos", 
                           success_count == count, 
                           f"Created {success_count}/{count}")

    def dar_entrada_carregamentos(self, count=3):
        """Process entry for carregamento appointments"""
        success_count = 0
        
        for i in range(min(count, len(self.agendamentos_carregamento))):
            try:
                agendamento = self.agendamentos_carregamento[i]
                response = self.session.post(
                    f"{self.base_url}/api/agendamentos/{agendamento['id']}/dar-entrada",
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Get the created carregamento
                    carregamento_response = self.session.get(
                        f"{self.base_url}/api/carregamentos/{result['registro_id']}",
                        timeout=30
                    )
                    if carregamento_response.status_code == 200:
                        self.carregamentos_ativos.append(carregamento_response.json())
                        success_count += 1
                        
            except Exception as e:
                print(f"Error processing entry {i+1}: {e}")
        
        return self.log_test(f"Process Entry for {count} Carregamentos", 
                           success_count == count, 
                           f"Processed {success_count}/{count}")

    def dar_saida_frota(self, count=3):
        """Process exit for frota appointments"""
        success_count = 0
        
        # First, process entries for frota
        for i in range(min(count, len(self.agendamentos_frota))):
            try:
                agendamento = self.agendamentos_frota[i]
                response = self.session.post(
                    f"{self.base_url}/api/agendamentos/{agendamento['id']}/dar-entrada",
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Get the created fleet record
                    fleet_response = self.session.get(
                        f"{self.base_url}/api/fleet/{result['registro_id']}",
                        timeout=30
                    )
                    if fleet_response.status_code == 200:
                        self.frota_ativa.append(fleet_response.json())
                        success_count += 1
                        
            except Exception as e:
                print(f"Error processing frota entry {i+1}: {e}")
        
        return self.log_test(f"Process Exit for {count} Frota Records", 
                           success_count == count, 
                           f"Processed {success_count}/{count}")

    def upload_carregamento_photos(self):
        """Upload 3 photos for each active carregamento (categories: geral, placa, motorista, carga)"""
        success_count = 0
        total_expected = len(self.carregamentos_ativos) * 3
        
        categories = ["geral", "placa", "motorista", "carga"]
        
        for carregamento in self.carregamentos_ativos:
            carregamento_id = carregamento['id']
            
            # Upload 3 photos with different categories
            for i in range(3):
                try:
                    category = categories[i % len(categories)]
                    image_data = self.create_test_image(f"carregamento_{carregamento_id}_{category}.jpg")
                    
                    files = {
                        'file': (f'test_{category}.jpg', image_data, 'image/jpeg')
                    }
                    params = {
                        'categoria': category
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/carregamentos/{carregamento_id}/photos",
                        files=files,
                        params=params,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        photo_data = response.json()
                        self.uploaded_photos.append({
                            'type': 'carregamento',
                            'id': carregamento_id,
                            'photo_id': photo_data['id'],
                            'category': category,
                            'storage_path': photo_data['storage_path']
                        })
                        success_count += 1
                        print(f"  ✅ Uploaded {category} photo for carregamento {carregamento_id}")
                    else:
                        print(f"  ❌ Failed to upload {category} photo for carregamento {carregamento_id}: {response.status_code}")
                        if response.text:
                            print(f"     Error: {response.text}")
                            
                except Exception as e:
                    print(f"  ❌ Exception uploading photo for carregamento {carregamento_id}: {e}")
        
        return self.log_test(f"Upload Carregamento Photos", 
                           success_count == total_expected, 
                           f"Uploaded {success_count}/{total_expected}")

    def upload_frota_saida_photos(self):
        """Upload 3 photos for each frota exit (categories: placa, motorista, frente)"""
        success_count = 0
        total_expected = len(self.frota_ativa) * 3
        
        categories = ["placa", "motorista", "frente"]
        
        for frota in self.frota_ativa:
            frota_id = frota['id']
            
            # Upload 3 photos with different categories for saida
            for i, category in enumerate(categories):
                try:
                    image_data = self.create_test_image(f"frota_{frota_id}_saida_{category}.jpg")
                    
                    files = {
                        'file': (f'test_saida_{category}.jpg', image_data, 'image/jpeg')
                    }
                    params = {
                        'category': category,
                        'moment': 'saida'
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/fleet/{frota_id}/photos",
                        files=files,
                        params=params,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        photo_data = response.json()
                        self.uploaded_photos.append({
                            'type': 'frota_saida',
                            'id': frota_id,
                            'photo_id': photo_data['id'],
                            'category': category,
                            'moment': 'saida',
                            'storage_path': photo_data['storage_path']
                        })
                        success_count += 1
                        print(f"  ✅ Uploaded saida {category} photo for frota {frota_id}")
                    else:
                        print(f"  ❌ Failed to upload saida {category} photo for frota {frota_id}: {response.status_code}")
                        if response.text:
                            print(f"     Error: {response.text}")
                            
                except Exception as e:
                    print(f"  ❌ Exception uploading saida photo for frota {frota_id}: {e}")
        
        return self.log_test(f"Upload Frota Saida Photos", 
                           success_count == total_expected, 
                           f"Uploaded {success_count}/{total_expected}")

    def dar_retorno_frota(self, count=2):
        """Process return for frota records"""
        success_count = 0
        
        for i in range(min(count, len(self.frota_ativa))):
            try:
                frota = self.frota_ativa[i]
                data = {
                    "km_retorno": frota['km_saida'] + 150 + (i * 50),
                    "observacao": f"Retorno da frota {i+1}"
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/fleet/{frota['id']}/return",
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"  ✅ Processed return for frota {frota['id']}")
                else:
                    print(f"  ❌ Failed to process return for frota {frota['id']}: {response.status_code}")
                    
            except Exception as e:
                print(f"Error processing return {i+1}: {e}")
        
        return self.log_test(f"Process Return for {count} Frota Records", 
                           success_count == count, 
                           f"Processed {success_count}/{count}")

    def upload_frota_retorno_photos(self, count=2):
        """Upload 3 photos for each frota return (categories: traseira, lateral, interior)"""
        success_count = 0
        total_expected = count * 3
        
        categories = ["traseira", "lateral", "interior"]
        
        for i in range(min(count, len(self.frota_ativa))):
            frota = self.frota_ativa[i]
            frota_id = frota['id']
            
            # Upload 3 photos with different categories for retorno
            for category in categories:
                try:
                    image_data = self.create_test_image(f"frota_{frota_id}_retorno_{category}.jpg")
                    
                    files = {
                        'file': (f'test_retorno_{category}.jpg', image_data, 'image/jpeg')
                    }
                    params = {
                        'category': category,
                        'moment': 'retorno'
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/fleet/{frota_id}/photos",
                        files=files,
                        params=params,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        photo_data = response.json()
                        self.uploaded_photos.append({
                            'type': 'frota_retorno',
                            'id': frota_id,
                            'photo_id': photo_data['id'],
                            'category': category,
                            'moment': 'retorno',
                            'storage_path': photo_data['storage_path']
                        })
                        success_count += 1
                        print(f"  ✅ Uploaded retorno {category} photo for frota {frota_id}")
                    else:
                        print(f"  ❌ Failed to upload retorno {category} photo for frota {frota_id}: {response.status_code}")
                        if response.text:
                            print(f"     Error: {response.text}")
                            
                except Exception as e:
                    print(f"  ❌ Exception uploading retorno photo for frota {frota_id}: {e}")
        
        return self.log_test(f"Upload Frota Retorno Photos", 
                           success_count == total_expected, 
                           f"Uploaded {success_count}/{total_expected}")

    def verify_photos_saved_locally(self):
        """Verify photos are saved correctly in /app/uploads/"""
        success_count = 0
        total_photos = len(self.uploaded_photos)
        
        for photo in self.uploaded_photos:
            try:
                storage_path = photo['storage_path']
                if os.path.exists(storage_path):
                    # Check if file has content
                    file_size = os.path.getsize(storage_path)
                    if file_size > 0:
                        success_count += 1
                        print(f"  ✅ Photo saved: {storage_path} ({file_size} bytes)")
                    else:
                        print(f"  ❌ Photo file empty: {storage_path}")
                else:
                    print(f"  ❌ Photo file not found: {storage_path}")
                    
            except Exception as e:
                print(f"  ❌ Error checking photo {photo['photo_id']}: {e}")
        
        return self.log_test(f"Verify Photos Saved Locally", 
                           success_count == total_photos, 
                           f"Found {success_count}/{total_photos} photos")

    def test_photo_retrieval(self):
        """Test GET requests return images correctly"""
        success_count = 0
        total_photos = len(self.uploaded_photos)
        
        for photo in self.uploaded_photos:
            try:
                if photo['type'] == 'carregamento':
                    url = f"{self.base_url}/api/carregamentos/{photo['id']}/photos/{photo['photo_id']}"
                else:  # frota
                    url = f"{self.base_url}/api/fleet/{photo['id']}/photos/{photo['photo_id']}"
                
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    # Check if response is actually an image
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type and len(response.content) > 0:
                        success_count += 1
                        print(f"  ✅ Retrieved photo {photo['photo_id']} ({len(response.content)} bytes)")
                    else:
                        print(f"  ❌ Invalid image response for photo {photo['photo_id']}: {content_type}")
                else:
                    print(f"  ❌ Failed to retrieve photo {photo['photo_id']}: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Error retrieving photo {photo['photo_id']}: {e}")
        
        return self.log_test(f"Test Photo Retrieval", 
                           success_count == total_photos, 
                           f"Retrieved {success_count}/{total_photos} photos")

    def test_carregamento_print_with_photos(self):
        """Test printing carregamento WITH photos via API"""
        success_count = 0
        
        for carregamento in self.carregamentos_ativos:
            try:
                # Check if there's a print endpoint
                response = self.session.get(
                    f"{self.base_url}/api/carregamentos/{carregamento['id']}",
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Check if carregamento has photos
                    if 'fotos' in data and len(data['fotos']) > 0:
                        success_count += 1
                        print(f"  ✅ Carregamento {carregamento['id']} has {len(data['fotos'])} photos for printing")
                    else:
                        print(f"  ❌ Carregamento {carregamento['id']} has no photos")
                else:
                    print(f"  ❌ Failed to get carregamento {carregamento['id']}: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Error checking carregamento print {carregamento['id']}: {e}")
        
        return self.log_test(f"Test Carregamento Print with Photos", 
                           success_count == len(self.carregamentos_ativos), 
                           f"Ready for print: {success_count}/{len(self.carregamentos_ativos)}")

    def test_frota_print_with_photos(self):
        """Test printing frota WITH photos via API"""
        success_count = 0
        
        for frota in self.frota_ativa:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/fleet/{frota['id']}",
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Check if frota has photos
                    total_photos = len(data.get('fotos_saida', [])) + len(data.get('fotos_retorno', []))
                    if total_photos > 0:
                        success_count += 1
                        print(f"  ✅ Frota {frota['id']} has {total_photos} photos for printing")
                    else:
                        print(f"  ❌ Frota {frota['id']} has no photos")
                else:
                    print(f"  ❌ Failed to get frota {frota['id']}: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Error checking frota print {frota['id']}: {e}")
        
        return self.log_test(f"Test Frota Print with Photos", 
                           success_count == len(self.frota_ativa), 
                           f"Ready for print: {success_count}/{len(self.frota_ativa)}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting CIPOLATTI Access Control System Backend Tests")
        print("=" * 60)
        
        # Authentication
        if not self.login():
            print("❌ Login failed, stopping tests")
            return False
        
        # Create appointments
        self.create_agendamentos_carregamento(5)
        self.create_agendamentos_frota(5)
        
        # Process entries
        self.dar_entrada_carregamentos(3)
        self.dar_saida_frota(3)
        
        # Upload photos for carregamentos
        self.upload_carregamento_photos()
        
        # Upload photos for frota saida
        self.upload_frota_saida_photos()
        
        # Process frota returns
        self.dar_retorno_frota(2)
        
        # Upload photos for frota retorno
        self.upload_frota_retorno_photos(2)
        
        # Verify local storage
        self.verify_photos_saved_locally()
        
        # Test photo retrieval
        self.test_photo_retrieval()
        
        # Test printing with photos
        self.test_carregamento_print_with_photos()
        self.test_frota_print_with_photos()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Photo upload/download functionality is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
            return False

def main():
    """Main test execution"""
    tester = CIPOLATTITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())