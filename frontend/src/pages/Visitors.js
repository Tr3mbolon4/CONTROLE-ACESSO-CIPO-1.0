import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { visitorsAPI } from '../services/api';
import { 
  Plus, 
  MagnifyingGlass, 
  Pencil, 
  Trash, 
  Eye,
  SignOut,
  Printer
} from '@phosphor-icons/react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
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

const Visitors = () => {
  const { isAdmin, isPortaria } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [visitors, setVisitors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedVisitor, setSelectedVisitor] = useState(null);
  const [filters, setFilters] = useState({
    nome: '',
    placa: '',
    data_inicio: '',
    data_fim: ''
  });
  const [formData, setFormData] = useState({
    nome: '',
    placa: '',
    veiculo: '',
    observacao: ''
  });

  useEffect(() => {
    loadVisitors();
    if (searchParams.get('action') === 'new') {
      setDialogOpen(true);
      setSearchParams({});
    }
  }, []);

  const loadVisitors = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.nome) params.nome = filters.nome;
      if (filters.placa) params.placa = filters.placa;
      if (filters.data_inicio) params.data_inicio = filters.data_inicio;
      if (filters.data_fim) params.data_fim = filters.data_fim;
      
      const response = await visitorsAPI.list(params);
      setVisitors(response.data.items);
    } catch (error) {
      toast.error('Erro ao carregar visitantes');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (selectedVisitor) {
        await visitorsAPI.update(selectedVisitor.id, formData);
        toast.success('Visitante atualizado');
      } else {
        await visitorsAPI.create(formData);
        toast.success('Visitante registrado');
      }
      setDialogOpen(false);
      resetForm();
      loadVisitors();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao salvar');
    }
  };

  const handleRegisterExit = async (visitor) => {
    try {
      const now = new Date();
      await visitorsAPI.update(visitor.id, {
        hora_saida: now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
      });
      toast.success('Saída registrada');
      loadVisitors();
    } catch (error) {
      toast.error('Erro ao registrar saída');
    }
  };

  const handleDelete = async () => {
    try {
      await visitorsAPI.delete(selectedVisitor.id);
      toast.success('Visitante excluído');
      setDeleteDialogOpen(false);
      setSelectedVisitor(null);
      loadVisitors();
    } catch (error) {
      toast.error('Erro ao excluir');
    }
  };

  const resetForm = () => {
    setFormData({ nome: '', placa: '', veiculo: '', observacao: '' });
    setSelectedVisitor(null);
  };

  const openEditDialog = (visitor) => {
    setSelectedVisitor(visitor);
    setFormData({
      nome: visitor.nome,
      placa: visitor.placa || '',
      veiculo: visitor.veiculo || '',
      observacao: visitor.observacao || ''
    });
    setDialogOpen(true);
  };

  const handlePrint = (visitor) => {
    const printContent = `
      <html>
      <head>
        <title>Registro de Visitante</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          h1 { font-size: 18px; border-bottom: 2px solid #000; padding-bottom: 10px; }
          .field { margin: 10px 0; }
          .label { font-weight: bold; }
        </style>
      </head>
      <body>
        <h1>REGISTRO DE VISITANTE</h1>
        <div class="field"><span class="label">Nome:</span> ${visitor.nome}</div>
        <div class="field"><span class="label">Data:</span> ${visitor.data}</div>
        <div class="field"><span class="label">Entrada:</span> ${visitor.hora_entrada}</div>
        <div class="field"><span class="label">Saída:</span> ${visitor.hora_saida || '-'}</div>
        <div class="field"><span class="label">Placa:</span> ${visitor.placa || '-'}</div>
        <div class="field"><span class="label">Veículo:</span> ${visitor.veiculo || '-'}</div>
        <div class="field"><span class="label">Porteiro:</span> ${visitor.porteiro}</div>
        <div class="field"><span class="label">Observação:</span> ${visitor.observacao || '-'}</div>
      </body>
      </html>
    `;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  };

  return (
    <div className="space-y-6" data-testid="visitors-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white font-['Outfit']">Visitantes</h1>
          <p className="text-gray-500 mt-1">Gerenciamento de visitantes da portaria</p>
        </div>
        {(isAdmin || isPortaria) && (
          <Button 
            onClick={() => { resetForm(); setDialogOpen(true); }}
            className="bg-white text-black hover:bg-gray-200"
            data-testid="add-visitor-button"
          >
            <Plus size={18} className="mr-2" />
            Novo Visitante
          </Button>
        )}
      </div>

      {/* Filters */}
      <div className="card-dark p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <Label className="text-gray-400 text-xs">Nome</Label>
            <Input
              placeholder="Buscar por nome"
              value={filters.nome}
              onChange={(e) => setFilters({ ...filters, nome: e.target.value })}
              className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
              data-testid="filter-nome"
            />
          </div>
          <div>
            <Label className="text-gray-400 text-xs">Placa</Label>
            <Input
              placeholder="Buscar por placa"
              value={filters.placa}
              onChange={(e) => setFilters({ ...filters, placa: e.target.value })}
              className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
              data-testid="filter-placa"
            />
          </div>
          <div>
            <Label className="text-gray-400 text-xs">Data Início</Label>
            <Input
              type="date"
              value={filters.data_inicio}
              onChange={(e) => setFilters({ ...filters, data_inicio: e.target.value })}
              className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
              data-testid="filter-data-inicio"
            />
          </div>
          <div>
            <Label className="text-gray-400 text-xs">Data Fim</Label>
            <Input
              type="date"
              value={filters.data_fim}
              onChange={(e) => setFilters({ ...filters, data_fim: e.target.value })}
              className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
              data-testid="filter-data-fim"
            />
          </div>
          <div className="flex items-end">
            <Button 
              onClick={loadVisitors}
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
              <TableHead className="text-gray-400">Nome</TableHead>
              <TableHead className="text-gray-400">Data</TableHead>
              <TableHead className="text-gray-400">Entrada</TableHead>
              <TableHead className="text-gray-400">Saída</TableHead>
              <TableHead className="text-gray-400">Placa</TableHead>
              <TableHead className="text-gray-400">Porteiro</TableHead>
              <TableHead className="text-gray-400 text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-gray-500 py-8">
                  Carregando...
                </TableCell>
              </TableRow>
            ) : visitors.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-gray-500 py-8">
                  Nenhum visitante encontrado
                </TableCell>
              </TableRow>
            ) : (
              visitors.map((visitor) => (
                <TableRow key={visitor.id} className="border-[#262626] hover:bg-[#1F1F1F]">
                  <TableCell className="text-white font-medium">{visitor.nome}</TableCell>
                  <TableCell className="text-gray-400">{visitor.data}</TableCell>
                  <TableCell className="text-gray-400 font-mono">{visitor.hora_entrada}</TableCell>
                  <TableCell>
                    {visitor.hora_saida ? (
                      <span className="text-gray-400 font-mono">{visitor.hora_saida}</span>
                    ) : (
                      <span className="badge-info">Presente</span>
                    )}
                  </TableCell>
                  <TableCell className="text-white font-mono">{visitor.placa || '-'}</TableCell>
                  <TableCell className="text-gray-400">{visitor.porteiro}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => { setSelectedVisitor(visitor); setViewDialogOpen(true); }}
                        className="text-gray-400 hover:text-white"
                        data-testid={`view-visitor-${visitor.id}`}
                      >
                        <Eye size={16} />
                      </Button>
                      {!visitor.hora_saida && (isAdmin || isPortaria) && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRegisterExit(visitor)}
                          className="text-yellow-400 hover:text-yellow-300"
                          data-testid={`exit-visitor-${visitor.id}`}
                        >
                          <SignOut size={16} />
                        </Button>
                      )}
                      {(isAdmin || isPortaria) && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openEditDialog(visitor)}
                          className="text-gray-400 hover:text-white"
                          data-testid={`edit-visitor-${visitor.id}`}
                        >
                          <Pencil size={16} />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handlePrint(visitor)}
                        className="text-gray-400 hover:text-white"
                        data-testid={`print-visitor-${visitor.id}`}
                      >
                        <Printer size={16} />
                      </Button>
                      {isAdmin && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => { setSelectedVisitor(visitor); setDeleteDialogOpen(true); }}
                          className="text-red-400 hover:text-red-300"
                          data-testid={`delete-visitor-${visitor.id}`}
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

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="bg-[#141414] border-[#262626] text-white max-w-md">
          <DialogHeader>
            <DialogTitle className="font-['Outfit']">
              {selectedVisitor ? 'Editar Visitante' : 'Novo Visitante'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label className="text-gray-400">Nome *</Label>
              <Input
                value={formData.nome}
                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                required
                data-testid="visitor-nome-input"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-400">Placa</Label>
                <Input
                  value={formData.placa}
                  onChange={(e) => setFormData({ ...formData, placa: e.target.value.toUpperCase() })}
                  className="bg-[#0A0A0A] border-[#262626] text-white mt-1 font-mono"
                  placeholder="ABC-1234"
                  data-testid="visitor-placa-input"
                />
              </div>
              <div>
                <Label className="text-gray-400">Veículo</Label>
                <Input
                  value={formData.veiculo}
                  onChange={(e) => setFormData({ ...formData, veiculo: e.target.value })}
                  className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                  placeholder="Modelo/Cor"
                  data-testid="visitor-veiculo-input"
                />
              </div>
            </div>
            <div>
              <Label className="text-gray-400">Observação</Label>
              <Input
                value={formData.observacao}
                onChange={(e) => setFormData({ ...formData, observacao: e.target.value })}
                className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                data-testid="visitor-observacao-input"
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
              <Button type="submit" className="bg-white text-black hover:bg-gray-200" data-testid="visitor-submit-button">
                {selectedVisitor ? 'Salvar' : 'Registrar'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* View Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="bg-[#141414] border-[#262626] text-white max-w-md">
          <DialogHeader>
            <DialogTitle className="font-['Outfit']">Detalhes do Visitante</DialogTitle>
          </DialogHeader>
          {selectedVisitor && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Nome</p>
                  <p className="text-white font-medium">{selectedVisitor.nome}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Data</p>
                  <p className="text-white">{selectedVisitor.data}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Entrada</p>
                  <p className="text-white font-mono">{selectedVisitor.hora_entrada}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Saída</p>
                  <p className="text-white font-mono">{selectedVisitor.hora_saida || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Placa</p>
                  <p className="text-white font-mono">{selectedVisitor.placa || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Veículo</p>
                  <p className="text-white">{selectedVisitor.veiculo || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Porteiro</p>
                  <p className="text-white">{selectedVisitor.porteiro}</p>
                </div>
              </div>
              {selectedVisitor.observacao && (
                <div>
                  <p className="text-xs text-gray-500">Observação</p>
                  <p className="text-white">{selectedVisitor.observacao}</p>
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
              Tem certeza que deseja excluir o registro de "{selectedVisitor?.nome}"? Esta ação não pode ser desfeita.
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

export default Visitors;
