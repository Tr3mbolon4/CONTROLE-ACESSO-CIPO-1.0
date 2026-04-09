# PRD - Sistema de Controle de Acesso Cipolatti

## Problema Original
Sistema de controle de acesso para portaria com gerenciamento de visitantes, funcionários, diretoria, frota e carregamentos. Necessidade de melhorias gerais no fluxo de agendamentos e operação da portaria.

## Arquitetura
- **Backend**: FastAPI (Python) com MongoDB
- **Frontend**: React com Tailwind CSS
- **Autenticação**: JWT com cookies HttpOnly

## Personas
1. **Admin** - Acesso total ao sistema
2. **Gestor** - Criação de agendamentos
3. **DSL** - Criação de agendamentos
4. **Portaria** - Registro de entrada/saída, "dar entrada" em agendamentos
5. **Diretoria** - Visualização

## Requisitos Core (Estáticos)
- Controle de entrada/saída de visitantes
- Controle de entrada/saída de funcionários
- Controle de entrada/saída de diretoria
- Controle de frota (saída/retorno de veículos)
- Controle de carregamentos
- Sistema de agendamentos

---

## Implementado (09/04/2026)

### 1. Fluxo de Agendamento com Ação Direta
- ✅ Aba "Agendados" em todos os módulos (Visitantes, Funcionários, Diretoria, Frota, Carregamentos)
- ✅ Botão "Dar Entrada" para converter agendamento em registro ativo
- ✅ Endpoint `POST /api/agendamentos/{id}/dar-entrada`
- ✅ Status: Pendente → Em Andamento → Finalizado

### 2. Controle de Funcionários - Permissão de Horário
- ✅ Campos adicionais: setor, responsável, tipo_permissao (saida_antecipada/entrada_atrasada), hora_permitida
- ✅ Aba "Permissões" na página de Funcionários
- ✅ Agendamentos para exceções de horário

### 3. Padronização de Dados
- ✅ Conversão automática para MAIÚSCULO nas placas
- ✅ Conversão automática para MAIÚSCULO nos campos de texto (nome, motorista, setor, etc.)
- ✅ Funções `normalize_text()` e `normalize_placa()` no backend

### 4. Módulo de Carregamento com Foto
- ✅ Upload de fotos no carregamento
- ✅ Categorias: geral, placa, motorista, carga
- ✅ Galeria de visualização de fotos
- ✅ Endpoint `POST /api/carregamentos/{id}/photos`

### 5. Impressão Melhorada
- ✅ Layout profissional com logo CIPOLATTI
- ✅ Seleção múltipla para impressão em lote
- ✅ Campos organizados com badges de status
- ✅ Rodapé com data/hora e identificação do sistema

### 6. Controle de Saída
- ✅ Indicação visual de saída autorizada/não autorizada
- ✅ Badges coloridos para status

### 7. Frota com Agendamentos
- ✅ Aba "Agendados" na página de Frota
- ✅ Suporte a agendamentos tipo "frota" com campos: carro, placa, motorista, destino, km_saida

---

## Backlog / Próximos Passos

### P0 (Alta Prioridade)
- [ ] Impressão com foto incorporada no layout
- [ ] Exportação para PDF/Excel

### P1 (Média Prioridade)
- [ ] Notificações push para novos agendamentos
- [ ] Dashboard de métricas avançadas
- [ ] Relatórios comparativos por período

### P2 (Baixa Prioridade)
- [ ] Integração com catracas físicas
- [ ] App mobile para porteiros
- [ ] Reconhecimento de placas por câmera

---

## Credenciais de Teste
- **Admin**: admin@cipolatti.com / admin123
