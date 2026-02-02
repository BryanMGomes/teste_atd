let paginaAtual = 1;
let filtroDataAtual = '';
let graficoBarras = null;
let graficoCircular = null;

document.addEventListener('DOMContentLoaded', function() {
    carregarDatasDisponiveis();
    carregarEstatisticas();
    carregarHistorico();
    
    document.getElementById('btn-aplicar-filtro').addEventListener('click', aplicarFiltro);
    document.getElementById('btn-limpar-filtro').addEventListener('click', limparFiltro);
    document.getElementById('btn-anterior').addEventListener('click', paginaAnterior);
    document.getElementById('btn-proximo').addEventListener('click', proximaPagina);
    
    atualizarLinksExportacao();
});

async function carregarDatasDisponiveis() {
    try {
        const response = await fetch('/admin_2026/datas');
        const data = await response.json();
        
        const select = document.getElementById('filtro-data');
        
        data.datas.forEach(date => {
            const option = document.createElement('option');
            option.value = date;
            option.textContent = formatarData(date);
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao carregar datas:', error);
    }
}

async function carregarEstatisticas() {
    try {
        let url = '/admin_2026/estatisticas';
        if (filtroDataAtual) {
            url += '?data=' + filtroDataAtual;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        document.getElementById('stat-muito-satisfeito').textContent = data.totais.muito_satisfeito;
        document.getElementById('stat-satisfeito').textContent = data.totais.satisfeito;
        document.getElementById('stat-insatisfeito').textContent = data.totais.insatisfeito;
        
        document.getElementById('percent-muito-satisfeito').textContent = data.percentagens.muito_satisfeito + '%';
        document.getElementById('percent-satisfeito').textContent = data.percentagens.satisfeito + '%';
        document.getElementById('percent-insatisfeito').textContent = data.percentagens.insatisfeito + '%';
        
        document.getElementById('total-geral').textContent = data.total_geral;
        
        atualizarGraficos(data);
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

async function carregarHistorico() {
    try {
        let url = `/admin_2026/historico?pagina=${paginaAtual}`;
        if (filtroDataAtual) {
            url += '&data=' + filtroDataAtual;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        const tbody = document.getElementById('tabela-body');
        tbody.innerHTML = '';
        
        const grauLabels = {
            'muito_satisfeito': '😊 Muito Satisfeito',
            'satisfeito': '🙂 Satisfeito',
            'insatisfeito': '😞 Insatisfeito'
        };
        
        data.registos.forEach(reg => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${reg.id}</td>
                <td>${grauLabels[reg.grau_satisfacao] || reg.grau_satisfacao}</td>
                <td>${formatarData(reg.data)}</td>
                <td>${reg.hora}</td>
                <td>${reg.dia_semana}</td>
            `;
            tbody.appendChild(tr);
        });
        
        document.getElementById('info-pagina').textContent = 
            `Página ${data.pagina} de ${data.total_paginas || 1}`;
        
        document.getElementById('btn-anterior').disabled = paginaAtual <= 1;
        document.getElementById('btn-proximo').disabled = paginaAtual >= data.total_paginas;
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
    }
}

function atualizarGraficos(data) {
    const cores = {
        muito_satisfeito: '#11998e',
        satisfeito: '#f5576c',
        insatisfeito: '#eb3349'
    };
    
    const labels = ['Muito Satisfeito', 'Satisfeito', 'Insatisfeito'];
    const valores = [
        data.totais.muito_satisfeito,
        data.totais.satisfeito,
        data.totais.insatisfeito
    ];
    const coresArray = [cores.muito_satisfeito, cores.satisfeito, cores.insatisfeito];
    
    if (graficoBarras) {
        graficoBarras.destroy();
    }
    
    const ctxBarras = document.getElementById('grafico-barras').getContext('2d');
    graficoBarras = new Chart(ctxBarras, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Número de Avaliações',
                data: valores,
                backgroundColor: coresArray,
                borderRadius: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Avaliações por Tipo',
                    font: { size: 16 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
    
    if (graficoCircular) {
        graficoCircular.destroy();
    }
    
    const ctxCircular = document.getElementById('grafico-circular').getContext('2d');
    graficoCircular = new Chart(ctxCircular, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: coresArray,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Distribuição Percentual',
                    font: { size: 16 }
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function aplicarFiltro() {
    const select = document.getElementById('filtro-data');
    let valor = select.value;
    
    if (valor === 'hoje') {
        const hoje = new Date().toISOString().split('T')[0];
        filtroDataAtual = hoje;
    } else {
        filtroDataAtual = valor;
    }
    
    paginaAtual = 1;
    carregarEstatisticas();
    carregarHistorico();
    atualizarLinksExportacao();
}

function limparFiltro() {
    document.getElementById('filtro-data').value = '';
    filtroDataAtual = '';
    paginaAtual = 1;
    carregarEstatisticas();
    carregarHistorico();
    atualizarLinksExportacao();
}

function paginaAnterior() {
    if (paginaAtual > 1) {
        paginaAtual--;
        carregarHistorico();
    }
}

function proximaPagina() {
    paginaAtual++;
    carregarHistorico();
}

function atualizarLinksExportacao() {
    let csvUrl = '/admin_2026/exportar/csv';
    let txtUrl = '/admin_2026/exportar/txt';
    
    if (filtroDataAtual) {
        csvUrl += '?data=' + filtroDataAtual;
        txtUrl += '?data=' + filtroDataAtual;
    }
    
    document.getElementById('btn-export-csv').href = csvUrl;
    document.getElementById('btn-export-txt').href = txtUrl;
}

function formatarData(dataStr) {
    const partes = dataStr.split('-');
    return `${partes[2]}/${partes[1]}/${partes[0]}`;
}
