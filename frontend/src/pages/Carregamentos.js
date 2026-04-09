import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { carregamentosAPI, agendamentosAPI } from '../services/api';
import { 
  Plus, 
  MagnifyingGlass, 
  Pencil, 
  Trash, 
  Eye,
  SignOut,
  Printer,
  CalendarCheck
} from '@phosphor-icons/react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../components/ui/alert-dialog';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const Carregamentos = () => {
  const { isAdmin, isPortaria } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [carregamentos, setCarregamentos] = useState([]);
  const [agendamentos, setAgendamentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [agendamentoDialogOpen, setAgendamentoDialogOpen] = useState(false);
  const [selectedCarregamento, setSelectedCarregamento] = useState(null);
  const [selectedAgendamento, setSelectedAgendamento] = useState(null);
  
  const [filters, setFilters] = useState({
    placa_carreta: '',
    motorista: '',
    empresa: '',
    destino: '',
    status: '',
    data_inicio: '',
    data_fim: ''
  });
  
  const [formData, setFormData] = useState({
    placa_carreta: '',
    placa_cavalo: '',
    cubagem: '',
    motorista: '',
    empresa_terceirizada: '',
    destino: '',
    observacao: '',
    agendamento_id: null
  });

  useEffect(() => {
    loadCarregamentos();
    loadAgendamentosHoje();
    if (searchParams.get('action') === 'new') {
      setDialogOpen(true);
      setSearchParams({});
    }
  }, []);

  const loadCarregamentos = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.placa_carreta) params.placa_carreta = filters.placa_carreta;
      if (filters.motorista) params.motorista = filters.motorista;
      if (filters.empresa) params.empresa = filters.empresa;
      if (filters.destino) params.destino = filters.destino;
      if (filters.status && filters.status !== 'all') params.status = filters.status;
      if (filters.data_inicio) params.data_inicio = filters.data_inicio;
      if (filters.data_fim) params.data_fim = filters.data_fim;
      
      const response = await carregamentosAPI.list(params);
      setCarregamentos(response.data.items);
    } catch (error) {
      toast.error('Erro ao carregar carregamentos');
    } finally {
      setLoading(false);
    }
  };

  const loadAgendamentosHoje = async () => {
    try {
      const response = await agendamentosAPI.list({ tipo: 'carregamento', status: 'pendente' });
      setAgendamentos(response.data.items);
    } catch (error) {
      console.error('Error loading agendamentos:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await carregamentosAPI.create(formData);
      toast.success('Carregamento registrado');
      setDialogOpen(false);
      resetForm();
      loadCarregamentos();
      loadAgendamentosHoje();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao registrar');
    }
  };

  const handleRegisterExit = async (carregamento) => {
    try {
      const now = new Date();
      await carregamentosAPI.update(carregamento.id, {
        hora_saida: now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
      });
      toast.success('Saída registrada');
      loadCarregamentos();
    } catch (error) {
      toast.error('Erro ao registrar saída');
    }
  };

  const handleDelete = async () => {
    try {
      await carregamentosAPI.delete(selectedCarregamento.id);
      toast.success('Carregamento excluído');
      setDeleteDialogOpen(false);
      setSelectedCarregamento(null);
      loadCarregamentos();
    } catch (error) {
      toast.error('Erro ao excluir');
    }
  };

  const resetForm = () => {
    setFormData({
      placa_carreta: '',
      placa_cavalo: '',
      cubagem: '',
      motorista: '',
      empresa_terceirizada: '',
      destino: '',
      observacao: '',
      agendamento_id: null
    });
    setSelectedAgendamento(null);
  };

  const selectAgendamento = (agendamento) => {
    setSelectedAgendamento(agendamento);
    setFormData({
      placa_carreta: agendamento.placa_carreta || '',
      placa_cavalo: agendamento.placa_cavalo || '',
      cubagem: agendamento.cubagem || '',
      motorista: agendamento.motorista || '',
      empresa_terceirizada: agendamento.empresa_terceirizada || '',
      destino: agendamento.destino || '',
      observacao: agendamento.observacao || '',
      agendamento_id: agendamento.id
    });
    setAgendamentoDialogOpen(false);
    setDialogOpen(true);
  };

  const handlePrint = (carregamento) => {
    const printContent = `
      <html>
      <head>
        <title>Registro de Carregamento</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          h1 { font-size: 18px; border-bottom: 2px solid #000; padding-bottom: 10px; }
          .field { margin: 10px 0; }
          .label { font-weight: bold; }
        </style>
      </head>
      <body>
        <h1>REGISTRO DE CARREGAMENTO</h1>
        <div class="field"><span class="label">Data:</span> ${carregamento.data}</div>
        <div class="field"><span class="label">Placa Carreta:</span> ${carregamento.placa_carreta}</div>
        <div class="field"><span class="label">Placa Cavalo:</span> ${carregamento.placa_cavalo}</div>
        <div class="field"><span class="label">Cubagem:</span> ${carregamento.cubagem || '-'}</div>
        <div class="field"><span class="label">Motorista:</span> ${carregamento.motorista}</div>
        <div class="field"><span class="label">Empresa:</span> ${carregamento.empresa_terceirizada}</div>
        <div class="field"><span class="label">Destino:</span> ${carregamento.destino}</div>
        <div class="field"><span class="label">Entrada:</span> ${carregamento.hora_entrada}</div>
        <div class="field"><span class="label">Saída:</span> ${carregamento.hora_saida || '-'}</div>
        <div class="field"><span class="label">Porteiro Entrada:</span> ${carregamento.porteiro_entrada}</div>
        <div class="field"><span class="label">Porteiro Saída:</span> ${carregamento.porteiro_saida || '-'}</div>
        <div class="field"><span class="label">Observação:</span> ${carregamento.observacao || '-'}</div>
      </body>
      </html>
    `;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  };

  return (
    <div className="space-y-6" data-testid="carregamentos-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white font-['Outfit']">Carregamentos</h1>
          <p className="text-gray-500 mt-1">Controle de entrada e saída de carregamentos</p>
        </div>
        <div className="flex gap-2">
          {agendamentos.length > 0 && (isAdmin || isPortaria) && (
            <Button 
              onClick={() => setAgendamentoDialogOpen(true)}
              variant="outline"
              className="border-[#262626] text-white hover:bg-[#262626]"
              data-testid="view-agendamentos-button"
            >
              <CalendarCheck size={18} className="mr-2" />
              Agendados ({agendamentos.length})
            </Button>
          )}
          {(isAdmin || isPortaria) && (
            <Button 
              onClick={() => { resetForm(); setDialogOpen(true); }}
              className="bg-white text-black hover:bg-gray-200"
              data-testid="add-carregamento-button"
            >
              <Plus size={18} className="mr-2" />
              Novo Carregamento
            </Button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="card-dark p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
          <div>
            <Label className="text-gray-400 text-xs">Placa Carreta</Label>
            <Input
              placeholder="Buscar placa"
              value={filters.placa_carreta}
              onChange={(e) => setFilters({ ...filters, placa_carreta: e.target.value })}
              className="bg-[#0A0A0A] border-[#262626] text-white mt-1 font-mono"
              data-testid="filter-placa"
            />
          </div>
          <div>
            <Label className="text-gray-400 text-xs">Motorista</Label>
            <Input
              placeholder="Buscar motorista"
              value={filters.motorista}
              onChange={(e) => setFilters({ ...filters, motorista: e.target.value })}
              className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
              data-testid="filter-motorista"
            />
          </div>
          <div>
            <Label className="text-gray-400 text-xs">Empresa</Label>
            <Input
              placeholder="Buscar empresa"
              value={filters.empresa}
              onChange={(e) => setFilters({ ...filters, empresa: e.target.value })}
              className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
              data-testid="filter-empresa"
            />
          </div>
          <div>
            <Label className="text-gray-400 text-xs">Status</Label>
            <Select value={filters.status} onValueChange={(v) => setFilters({ ...filters, status: v })}>
              <SelectTrigger className="bg-[#0A0A0A] border-[#262626] text-white mt-1">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent className="bg-[#141414] border-[#262626]">
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="em_carregamento">Em Carregamento</SelectItem>
                <SelectItem value="finalizado">Finalizado</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label className="text-gray-400 text-xs">Data Início</Label>
            <Input
              type="date"
              value={filters.data_inicio}
              onChange={(e) => setFilters({ ...filters, data_inicio: e.target.value })}
              className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
            />
          </div>
          <div className="flex items-end">
            <Button 
              onClick={loadCarregamentos}
              className="w-full bg-[#262626] text-white hover:bg-[#363636]"
              data-testid="filter-search-button"
            >
              <MagnifyingGlass size={18} className="mr-2" />
              Buscar
            </Button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card-dark overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-[#262626] hover:bg-transparent">
              <TableHead className="text-gray-400">Carreta</TableHead>
              <TableHead className="text-gray-400">Cavalo</TableHead>
              <TableHead className="text-gray-400">Motorista</TableHead>
              <TableHead className="text-gray-400">Empresa</TableHead>
              <TableHead className="text-gray-400">Destino</TableHead>
              <TableHead className="text-gray-400">Entrada</TableHead>
              <TableHead className="text-gray-400">Saída</TableHead>
              <TableHead className="text-gray-400">Status</TableHead>
              <TableHead className="text-gray-400 text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center text-gray-500 py-8">
                  Carregando...
                </TableCell>
              </TableRow>
            ) : carregamentos.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center text-gray-500 py-8">
                  Nenhum carregamento encontrado
                </TableCell>
              </TableRow>
            ) : (
              carregamentos.map((item) => (
                <TableRow key={item.id} className="border-[#262626] hover:bg-[#1F1F1F]">
                  <TableCell className="text-white font-mono font-medium">{item.placa_carreta}</TableCell>
                  <TableCell className="text-white font-mono">{item.placa_cavalo}</TableCell>
                  <TableCell className="text-white">{item.motorista}</TableCell>
                  <TableCell className="text-gray-400">{item.empresa_terceirizada}</TableCell>
                  <TableCell className="text-gray-400">{item.destino}</TableCell>
                  <TableCell className="text-gray-400 font-mono">{item.hora_entrada}</TableCell>
                  <TableCell className="text-gray-400 font-mono">{item.hora_saida || '-'}</TableCell>
                  <TableCell>
                    {item.status === 'em_carregamento' ? (
                      <span className="badge-warning">Em Carregamento</span>
                    ) : (
                      <span className="badge-success">Finalizado</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => { setSelectedCarregamento(item); setViewDialogOpen(true); }}
                        className="text-gray-400 hover:text-white"
                      >
                        <Eye size={16} />
                      </Button>
                      {item.status === 'em_carregamento' && (isAdmin || isPortaria) && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRegisterExit(item)}
                          className="text-green-400 hover:text-green-300"
                        >
                          <SignOut size={16} />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handlePrint(item)}
                        className="text-gray-400 hover:text-white"
                      >
                        <Printer size={16} />
                      </Button>
                      {isAdmin && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => { setSelectedCarregamento(item); setDeleteDialogOpen(true); }}
                          className="text-red-400 hover:text-red-300"
                        >
                          <Trash size={16} />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Create Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="bg-[#141414] border-[#262626] text-white max-w-lg">
          <DialogHeader>
            <DialogTitle className="font-['Outfit']">
              {selectedAgendamento ? 'Registrar Carregamento (Agendado)' : 'Novo Carregamento'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-400">Placa Carreta *</Label>
                <Input
                  value={formData.placa_carreta}
                  onChange={(e) => setFormData({ ...formData, placa_carreta: e.target.value.toUpperCase() })}
                  className="bg-[#0A0A0A] border-[#262626] text-white mt-1 font-mono"
                  placeholder="ABC-1234"
                  required
                  data-testid="carregamento-placa-carreta"
                />
              </div>
              <div>
                <Label className="text-gray-400">Placa Cavalo *</Label>
                <Input
                  value={formData.placa_cavalo}
                  onChange={(e) => setFormData({ ...formData, placa_cavalo: e.target.value.toUpperCase() })}
                  className="bg-[#0A0A0A] border-[#262626] text-white mt-1 font-mono"
                  placeholder="XYZ-5678"
                  required
                  data-testid="carregamento-placa-cavalo"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-400">Motorista *</Label>
                <Input
                  value={formData.motorista}
                  onChange={(e) => setFormData({ ...formData, motorista: e.target.value })}
                  className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                  required
                  data-testid="carregamento-motorista"
                />
              </div>
              <div>
                <Label className="text-gray-400">Cubagem</Label>
                <Input
                  value={formData.cubagem}
                  onChange={(e) => setFormData({ ...formData, cubagem: e.target.value })}
                  className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                  placeholder="Ex: 50m³"
                  data-testid="carregamento-cubagem"
                />
              </div>
            </div>
            <div>
              <Label className="text-gray-400">Empresa Terceirizada *</Label>
              <Input
                value={formData.empresa_terceirizada}
                onChange={(e) => setFormData({ ...formData, empresa_terceirizada: e.target.value })}
                className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                required
                data-testid="carregamento-empresa"
              />
            </div>
            <div>
              <Label className="text-gray-400">Destino (Shopping) *</Label>
              <Input
                value={formData.destino}
                onChange={(e) => setFormData({ ...formData, destino: e.target.value })}
                className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                placeholder="Shopping onde será realizada a entrega"
                required
                data-testid="carregamento-destino"
              />
            </div>
            <div>
              <Label className="text-gray-400">Observação</Label>
              <Textarea
                value={formData.observacao}
                onChange={(e) => setFormData({ ...formData, observacao: e.target.value })}
                className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                rows={2}
              />
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setDialogOpen(false)}
                className="border-[#262626] text-white hover:bg-[#262626]"
              >
                Cancelar
              </Button>
              <Button type="submit" className="bg-white text-black hover:bg-gray-200" data-testid="carregamento-submit">
                Registrar Entrada
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Agendamentos Dialog */}
      <Dialog open={agendamentoDialogOpen} onOpenChange={setAgendamentoDialogOpen}>
        <DialogContent className="bg-[#141414] border-[#262626] text-white max-w-2xl">
          <DialogHeader>
            <DialogTitle className="font-['Outfit']">Carregamentos Agendados</DialogTitle>
          </DialogHeader>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {agendamentos.map((ag) => (
              <div 
                key={ag.id} 
                className="p-4 bg-[#0A0A0A] rounded-md border border-[#262626] hover:border-[#3B82F6] cursor-pointer transition-colors"
                onClick={() => selectAgendamento(ag)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-white font-medium">{ag.motorista || 'Motorista não informado'}</p>
                    <p className="text-sm text-gray-400">{ag.empresa_terceirizada}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-400">{ag.data_prevista}</p>
                    <p className="text-sm text-gray-500">{ag.hora_prevista || '-'}</p>
                  </div>
                </div>
                <div className="mt-2 flex gap-4 text-xs text-gray-500">
                  {ag.placa_carreta && <span>Carreta: <span className="font-mono text-gray-400">{ag.placa_carreta}</span></span>}
                  {ag.destino && <span>Destino: <span className="text-gray-400">{ag.destino}</span></span>}
                </div>
              </div>
            ))}
            {agendamentos.length === 0 && (
              <p className="text-center text-gray-500 py-8">Nenhum carregamento agendado</p>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* View Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="bg-[#141414] border-[#262626] text-white max-w-lg">
          <DialogHeader>
            <DialogTitle className="font-['Outfit']">Detalhes do Carregamento</DialogTitle>
          </DialogHeader>
          {selectedCarregamento && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Placa Carreta</p>
                  <p className="text-white font-mono font-medium">{selectedCarregamento.placa_carreta}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Placa Cavalo</p>
                  <p className="text-white font-mono">{selectedCarregamento.placa_cavalo}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Motorista</p>
                  <p className="text-white">{selectedCarregamento.motorista}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Cubagem</p>
                  <p className="text-white">{selectedCarregamento.cubagem || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Empresa</p>
                  <p className="text-white">{selectedCarregamento.empresa_terceirizada}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Destino</p>
                  <p className="text-white">{selectedCarregamento.destino}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Data</p>
                  <p className="text-white">{selectedCarregamento.data}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Entrada</p>
                  <p className="text-white font-mono">{selectedCarregamento.hora_entrada}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Saída</p>
                  <p className="text-white font-mono">{selectedCarregamento.hora_saida || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Porteiro Entrada</p>
                  <p className="text-white">{selectedCarregamento.porteiro_entrada}</p>
                </div>
              </div>
              {selectedCarregamento.observacao && (
                <div>
                  <p className="text-xs text-gray-500">Observação</p>
                  <p className="text-white">{selectedCarregamento.observacao}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-[#141414] border-[#262626]">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Confirmar Exclusão</AlertDialogTitle>
            <AlertDialogDescription className="text-gray-400">
              Tem certeza que deseja excluir este carregamento? Esta ação não pode ser desfeita.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-[#262626] text-white hover:bg-[#262626]">
              Cancelar
            </AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDelete}
              className="bg-red-500 text-white hover:bg-red-600"
            >
              Excluir
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Carregamentos;
