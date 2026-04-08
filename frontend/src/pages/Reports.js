import React, { useState } from 'react';
import { reportsAPI } from '../services/api';
import { 
  FileText,
  FilePdf,
  FileXls,
  MagnifyingGlass,
  Printer,
  Download
} from '@phosphor-icons/react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '../components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import { toast } from 'sonner';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

const Reports = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('visitors');
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalKm, setTotalKm] = useState(0);
  
  const [filters, setFilters] = useState({
    data_inicio: new Date().toISOString().split('T')[0],
    data_fim: new Date().toISOString().split('T')[0],
    nome: '',
    placa: '',
    setor: '',
    motorista: '',
    destino: '',
    porteiro: ''
  });

  const loadReport = async () => {
    if (!filters.data_inicio || !filters.data_fim) {
      toast.error('Selecione o período');
      return;
    }
    
    setLoading(true);
    try {
      let response;
      const params = {
        data_inicio: filters.data_inicio,
        data_fim: filters.data_fim
      };
      
      if (filters.nome) params.nome = filters.nome;
      if (filters.placa) params.placa = filters.placa;
      if (filters.porteiro) params.porteiro = filters.porteiro;
      
      switch (activeTab) {
        case 'visitors':
          response = await reportsAPI.visitors(params);
          break;
        case 'fleet':
          if (filters.motorista) params.motorista = filters.motorista;
          if (filters.destino) params.destino = filters.destino;
          response = await reportsAPI.fleet(params);
          setTotalKm(response.data.total_km || 0);
          break;
        case 'employees':
          if (filters.setor) params.setor = filters.setor;
          response = await reportsAPI.employees(params);
          break;
        case 'directors':
          response = await reportsAPI.directors(params);
          break;
        default:
          return;
      }
      
      setData(response.data.items);
      setTotal(response.data.total);
    } catch (error) {
      toast.error('Erro ao gerar relatório');
    } finally {
      setLoading(false);
    }
  };

  const getColumns = () => {
    switch (activeTab) {
      case 'visitors':
        return ['Nome', 'Data', 'Entrada', 'Saída', 'Placa', 'Veículo', 'Porteiro'];
      case 'fleet':
        return ['Placa', 'Carro', 'Motorista', 'Destino', 'Saída', 'Retorno', 'KM Rodado', 'Porteiro Saída'];
      case 'employees':
        return ['Nome', 'Setor', 'Data', 'Entrada', 'Saída', 'Autorizado', 'Placa', 'Porteiro'];
      case 'directors':
        return ['Nome', 'Data', 'Entrada', 'Saída', 'Placa', 'Carro', 'Porteiro'];
      default:
        return [];
    }
  };

  const getRowData = (item) => {
    switch (activeTab) {
      case 'visitors':
        return [item.nome, item.data, item.hora_entrada, item.hora_saida || '-', item.placa || '-', item.veiculo || '-', item.porteiro];
      case 'fleet':
        return [item.placa, item.carro, item.motorista, item.destino, `${item.data_saida} ${item.hora_saida}`, item.data_retorno ? `${item.data_retorno} ${item.hora_retorno}` : '-', item.km_rodado ? `${item.km_rodado} km` : '-', item.porteiro_saida];
      case 'employees':
        return [item.nome, item.setor, item.data, item.hora_entrada, item.hora_saida || '-', item.autorizado ? 'Sim' : 'Não', item.placa || '-', item.porteiro];
      case 'directors':
        return [item.nome, item.data, item.hora_entrada, item.hora_saida || '-', item.placa || '-', item.carro || '-', item.porteiro];
      default:
        return [];
    }
  };

  const getTitle = () => {
    const titles = {
      visitors: 'Visitantes',
      fleet: 'Frota',
      employees: 'Funcionários',
      directors: 'Diretoria'
    };
    return titles[activeTab];
  };

  const exportPDF = () => {
    const doc = new jsPDF();
    const title = `Relatório de ${getTitle()}`;
    const period = `Período: ${filters.data_inicio} a ${filters.data_fim}`;
    
    doc.setFontSize(16);
    doc.text(title, 14, 15);
    doc.setFontSize(10);
    doc.text(period, 14, 22);
    doc.text(`Total de registros: ${total}`, 14, 28);
    if (activeTab === 'fleet' && totalKm > 0) {
      doc.text(`Total KM rodado: ${totalKm}`, 14, 34);
    }
    
    const columns = getColumns();
    const rows = data.map(item => getRowData(item));
    
    doc.autoTable({
      head: [columns],
      body: rows,
      startY: activeTab === 'fleet' ? 40 : 35,
      styles: { fontSize: 8 },
      headStyles: { fillColor: [38, 38, 38] }
    });
    
    doc.save(`relatorio_${activeTab}_${filters.data_inicio}_${filters.data_fim}.pdf`);
    toast.success('PDF gerado com sucesso');
  };

  const exportExcel = () => {
    const columns = getColumns();
    const rows = data.map(item => {
      const rowData = getRowData(item);
      const obj = {};
      columns.forEach((col, idx) => {
        obj[col] = rowData[idx];
      });
      return obj;
    });
    
    const ws = XLSX.utils.json_to_sheet(rows);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, getTitle());
    
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
    const dataBlob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    saveAs(dataBlob, `relatorio_${activeTab}_${filters.data_inicio}_${filters.data_fim}.xlsx`);
    toast.success('Excel gerado com sucesso');
  };

  const handlePrint = () => {
    const columns = getColumns();
    const rows = data.map(item => getRowData(item));
    
    const printContent = `
      <html>
      <head>
        <title>Relatório de ${getTitle()}</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          h1 { font-size: 18px; margin-bottom: 5px; }
          .info { font-size: 12px; color: #666; margin-bottom: 15px; }
          table { width: 100%; border-collapse: collapse; font-size: 11px; }
          th { background: #262626; color: white; padding: 8px; text-align: left; }
          td { border-bottom: 1px solid #ddd; padding: 6px; }
          tr:hover { background: #f5f5f5; }
        </style>
      </head>
      <body>
        <h1>Relatório de ${getTitle()}</h1>
        <div class="info">
          Período: ${filters.data_inicio} a ${filters.data_fim}<br>
          Total de registros: ${total}
          ${activeTab === 'fleet' && totalKm > 0 ? `<br>Total KM rodado: ${totalKm}` : ''}
        </div>
        <table>
          <thead>
            <tr>${columns.map(col => `<th>${col}</th>`).join('')}</tr>
          </thead>
          <tbody>
            ${rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('')}
          </tbody>
        </table>
      </body>
      </html>
    `;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  };

  return (
    <div className="space-y-6" data-testid="reports-page">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-white font-['Outfit']">Relatórios</h1>
        <p className="text-gray-500 mt-1">Gere relatórios detalhados por período</p>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => { setActiveTab(v); setData([]); setTotal(0); }}>
        <TabsList className="bg-[#0A0A0A] border border-[#262626]">
          <TabsTrigger value="visitors" className="data-[state=active]:bg-[#262626]" data-testid="tab-visitors">
            Visitantes
          </TabsTrigger>
          <TabsTrigger value="fleet" className="data-[state=active]:bg-[#262626]" data-testid="tab-fleet">
            Frota
          </TabsTrigger>
          <TabsTrigger value="employees" className="data-[state=active]:bg-[#262626]" data-testid="tab-employees">
            Funcionários
          </TabsTrigger>
          <TabsTrigger value="directors" className="data-[state=active]:bg-[#262626]" data-testid="tab-directors">
            Diretoria
          </TabsTrigger>
        </TabsList>

        {/* Filters */}
        <div className="card-dark p-4 mt-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <Label className="text-gray-400 text-xs">Data Início *</Label>
              <Input
                type="date"
                value={filters.data_inicio}
                onChange={(e) => setFilters({ ...filters, data_inicio: e.target.value })}
                className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                data-testid="report-data-inicio"
              />
            </div>
            <div>
              <Label className="text-gray-400 text-xs">Data Fim *</Label>
              <Input
                type="date"
                value={filters.data_fim}
                onChange={(e) => setFilters({ ...filters, data_fim: e.target.value })}
                className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                data-testid="report-data-fim"
              />
            </div>
            <div>
              <Label className="text-gray-400 text-xs">Nome</Label>
              <Input
                placeholder="Filtrar por nome"
                value={filters.nome}
                onChange={(e) => setFilters({ ...filters, nome: e.target.value })}
                className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                data-testid="report-nome"
              />
            </div>
            <div>
              <Label className="text-gray-400 text-xs">Placa</Label>
              <Input
                placeholder="Filtrar por placa"
                value={filters.placa}
                onChange={(e) => setFilters({ ...filters, placa: e.target.value })}
                className="bg-[#0A0A0A] border-[#262626] text-white mt-1 font-mono"
                data-testid="report-placa"
              />
            </div>
            {activeTab === 'fleet' && (
              <>
                <div>
                  <Label className="text-gray-400 text-xs">Motorista</Label>
                  <Input
                    placeholder="Filtrar por motorista"
                    value={filters.motorista}
                    onChange={(e) => setFilters({ ...filters, motorista: e.target.value })}
                    className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                    data-testid="report-motorista"
                  />
                </div>
                <div>
                  <Label className="text-gray-400 text-xs">Destino</Label>
                  <Input
                    placeholder="Filtrar por destino"
                    value={filters.destino}
                    onChange={(e) => setFilters({ ...filters, destino: e.target.value })}
                    className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                    data-testid="report-destino"
                  />
                </div>
              </>
            )}
            {activeTab === 'employees' && (
              <div>
                <Label className="text-gray-400 text-xs">Setor</Label>
                <Input
                  placeholder="Filtrar por setor"
                  value={filters.setor}
                  onChange={(e) => setFilters({ ...filters, setor: e.target.value })}
                  className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                  data-testid="report-setor"
                />
              </div>
            )}
            <div>
              <Label className="text-gray-400 text-xs">Porteiro</Label>
              <Input
                placeholder="Filtrar por porteiro"
                value={filters.porteiro}
                onChange={(e) => setFilters({ ...filters, porteiro: e.target.value })}
                className="bg-[#0A0A0A] border-[#262626] text-white mt-1"
                data-testid="report-porteiro"
              />
            </div>
          </div>
          
          <div className="flex flex-wrap gap-3 mt-4">
            <Button 
              onClick={loadReport}
              disabled={loading}
              className="bg-white text-black hover:bg-gray-200"
              data-testid="report-generate-button"
            >
              <MagnifyingGlass size={18} className="mr-2" />
              {loading ? 'Gerando...' : 'Gerar Relatório'}
            </Button>
            
            {data.length > 0 && (
              <>
                <Button 
                  onClick={exportPDF}
                  className="bg-red-600 text-white hover:bg-red-700"
                  data-testid="report-export-pdf"
                >
                  <FilePdf size={18} className="mr-2" />
                  Exportar PDF
                </Button>
                <Button 
                  onClick={exportExcel}
                  className="bg-green-600 text-white hover:bg-green-700"
                  data-testid="report-export-excel"
                >
                  <FileXls size={18} className="mr-2" />
                  Exportar Excel
                </Button>
                <Button 
                  onClick={handlePrint}
                  variant="outline"
                  className="border-[#262626] text-white hover:bg-[#262626]"
                  data-testid="report-print"
                >
                  <Printer size={18} className="mr-2" />
                  Imprimir
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Results */}
        {data.length > 0 && (
          <div className="card-dark mt-4">
            <div className="p-4 border-b border-[#262626] flex items-center justify-between">
              <div>
                <span className="text-white font-medium">{total}</span>
                <span className="text-gray-500 ml-1">registros encontrados</span>
              </div>
              {activeTab === 'fleet' && totalKm > 0 && (
                <div>
                  <span className="text-gray-500">Total KM: </span>
                  <span className="text-white font-mono font-medium">{totalKm} km</span>
                </div>
              )}
            </div>
            
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-[#262626] hover:bg-transparent">
                    {getColumns().map((col, idx) => (
                      <TableHead key={idx} className="text-gray-400">{col}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.map((item, idx) => (
                    <TableRow key={idx} className="border-[#262626] hover:bg-[#1F1F1F]">
                      {getRowData(item).map((cell, cellIdx) => (
                        <TableCell 
                          key={cellIdx} 
                          className={`${cellIdx === 0 ? 'text-white font-medium' : 'text-gray-400'} ${
                            (activeTab === 'fleet' && cellIdx === 0) || 
                            (activeTab !== 'fleet' && getColumns()[cellIdx] === 'Placa') 
                              ? 'font-mono' : ''
                          }`}
                        >
                          {cell}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
        )}

        {data.length === 0 && !loading && (
          <div className="card-dark p-12 mt-4 text-center">
            <FileText size={48} className="mx-auto text-gray-600 mb-4" />
            <p className="text-gray-500">Selecione o período e clique em "Gerar Relatório"</p>
          </div>
        )}
      </Tabs>
    </div>
  );
};

export default Reports;
