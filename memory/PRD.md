# PRD - Sistema de Controle de Acesso CIPOLATTI

## Original Problem Statement
Sistema de controle de acesso para empresa CIPOLATTI com módulos para:
- Visitantes
- Funcionários
- Diretoria
- Frota
- Carregamentos
- Agendamentos
- Relatórios

### Bugs Reportados
1. Relatório precisa ter o nome CIPOLATTI, logo e ser mais profissional/moderno
2. Ao selecionar imprimir em qualquer modalidade, trava e só retorna após fechar página de impressão
3. Erro ao fazer agendamento de visitante, diretoria, funcionário, frota

## User Personas
- **Administrador**: Acesso total ao sistema
- **Porteiro**: Registro de entrada/saída, consultas
- **Gerente**: Relatórios e dashboards

## Core Requirements (Static)
- Login com autenticação JWT + cookies
- CRUD de visitantes, funcionários, diretoria, frota, carregamentos
- Sistema de agendamentos com múltiplos tipos
- Relatórios com filtros por data
- Impressão de fichas e relatórios
- Upload de fotos para veículos e carregamentos
- Dashboard com estatísticas

## What's Been Implemented

### 2026-04-10 - Bug Fixes & Improvements
- [x] **Bug de Impressão Corrigido**: 
  - Migrado de `window.open() + print()` para `printUtils.js` com iframe
  - Arquivos atualizados: Directors.js, Fleet.js, Carregamentos.js, Reports.js
  - Impressão agora é não-bloqueante

- [x] **Bug de Agendamento Corrigido**:
  - Alterado `km_saida` de `float` para `str` no backend para aceitar strings vazias
  - Adicionada função `getErrorMessage()` no api.js para tratar erros corretamente
  - Data prevista agora é preenchida automaticamente com data atual

- [x] **Relatórios Profissionais**:
  - Template de impressão com logo CIPOLATTI
  - Design moderno e profissional já implementado em `printUtils.js`
  - Header com logo, título e informações do documento
  - Footer com data/hora de geração

- [x] **Session Token**: Aumentado de 15 min para 8 horas

## Test Results
- Backend: 100% success (41/41 tests)
- Frontend: 90% success
- Módulos funcionais: Dashboard, Visitantes, Funcionários, Diretoria, Frota, Carregamentos, Agendamentos, Relatórios

## Prioritized Backlog

### P0 - Critical (Completed)
- [x] Bug de impressão travando interface
- [x] Bug de criação de agendamentos
- [x] Relatórios profissionais com CIPOLATTI

### P1 - High Priority
- [ ] Adicionar mais data-testid para melhorar testabilidade
- [ ] Melhorar UX de filtros em agendamentos

### P2 - Medium Priority
- [ ] Exportação para PDF com logo
- [ ] Notificações de agendamentos próximos
- [ ] Modo offline básico

## Next Tasks
1. Validar todos os fluxos de impressão em diferentes navegadores
2. Testar upload de fotos em frota e carregamentos
3. Verificar responsividade em dispositivos móveis
