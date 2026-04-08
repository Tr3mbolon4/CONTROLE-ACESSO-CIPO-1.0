# Sistema de Controle de Acesso para Portaria - PRD

## Visão Geral
Sistema web completo para gerenciamento de portaria empresarial com controle de visitantes, frota, funcionários e diretoria.

## Data de Criação
08/04/2026

## Tecnologias
- **Backend**: FastAPI + MongoDB + JWT Auth
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Storage**: Emergent Object Storage para fotos
- **Tema**: Dark Modern (Archetype 4 - Swiss & High-Contrast)

## Personas
1. **Porteiro** - Registra entradas/saídas, anexa fotos
2. **Gestor** - Visualiza relatórios e histórico
3. **Diretoria** - Dashboard gerencial
4. **Administrador** - Acesso total + gerenciamento de usuários

## Funcionalidades Implementadas ✅

### Autenticação
- [x] Login com JWT
- [x] Controle de perfis (Portaria, Gestor, Diretoria, Admin)
- [x] Proteção contra brute force
- [x] Token refresh automático

### Módulo Visitantes
- [x] Registro de entrada/saída
- [x] Filtros por nome, placa, período
- [x] Impressão de registro
- [x] Visualização detalhada

### Módulo Frota
- [x] Registro de saída de veículo
- [x] Registro de retorno com KM
- [x] Cálculo automático de KM rodado
- [x] Upload de fotos (placa, motorista, interior, etc.)
- [x] Galeria de fotos com categorias
- [x] Separação fotos saída/retorno

### Módulo Funcionários
- [x] Registro entrada/saída
- [x] Campo de autorização (SIM/NÃO)
- [x] Filtro por setor

### Módulo Diretoria
- [x] Registro rápido
- [x] Consulta e filtros

### Dashboard
- [x] Métricas do dia (visitantes, funcionários, frota)
- [x] Veículos em uso
- [x] Visitantes recentes
- [x] Ações rápidas
- [x] Resumo semanal

### Relatórios
- [x] Filtros avançados por período
- [x] Exportação PDF
- [x] Exportação Excel
- [x] Impressão

### Configurações
- [x] Gerenciamento de usuários
- [x] CRUD de usuários
- [x] Atribuição de perfis

### Histórico
- [x] Registro de alterações no backend
- [x] Quem alterou e quando

## Credenciais de Teste
- **Admin**: admin@portaria.com / admin123

## Backlog P0/P1/P2

### P0 (Crítico) - Concluído
- ✅ Sistema de autenticação
- ✅ CRUD completo para todos os módulos
- ✅ Dashboard funcional
- ✅ Upload de fotos

### P1 (Importante) - Pendente
- [ ] Busca global rápida
- [ ] Notificações em tempo real
- [ ] Paginação nas tabelas

### P2 (Desejável) - Futuro
- [ ] Leitura automática de placa (OCR)
- [ ] QR Code para check-in
- [ ] Cadastro de empresas terceiras
- [ ] Assinatura digital
- [ ] Multiempresa
- [ ] Auditoria completa

## Próximos Passos
1. Implementar busca global
2. Adicionar paginação nas listagens
3. Melhorar validações de formulário
4. Implementar cache para dashboard
