// static/clientes.js

document.addEventListener('DOMContentLoaded', () => {
    const tabClientes = document.getElementById('clientes');
    if (!tabClientes) return;

    const formCliente = document.getElementById('form-cliente');
    const searchSelect = document.getElementById('cliente-search');
    const formTitulo = document.getElementById('form-cliente-titulo');
    const clienteIdInput = document.getElementById('cliente-id');
    
    const btnSalvar = document.getElementById('btn-salvar-cliente');
    const btnAtualizar = document.getElementById('btn-atualizar-cliente');
    const btnExcluir = document.getElementById('btn-excluir-cliente');
    const btnLimpar = document.getElementById('btn-limpar-cliente');

    const clientePropostasArea = document.getElementById('cliente-propostas-area');
    const tbodyClientePropostas = document.getElementById('tbody-cliente-propostas');
    const clientePropostasTitulo = document.getElementById('cliente-propostas-titulo');

    let todosClientes = [];

    const carregarTodosClientes = async () => {
        try {
            const response = await fetch('/api/clientes/listar');
            if (!response.ok) throw new Error('Falha ao buscar lista de clientes.');
            todosClientes = await response.json();
            searchSelect.innerHTML = '<option value="">Digite para buscar...</option>';
            todosClientes.forEach(cliente => {
                const option = document.createElement('option');
                option.value = cliente.id;
                option.textContent = cliente.nome;
                searchSelect.appendChild(option);
            });
            $(searchSelect).select2({ theme: 'bootstrap-5', placeholder: 'Digite para buscar...' });
        } catch (error) { console.error(error); alert(error.message); }
    };
    
    const mudarModoFormulario = (modo, cliente = null) => {
        formCliente.reset();
        clienteIdInput.value = '';
        
        // Reset CNH para Não Informado por padrão
        document.getElementById('cnh-ni').checked = true;

        if (modo === 'edicao' && cliente) {
            clienteIdInput.value = cliente.id;
            document.getElementById('cliente-nome').value = cliente.nome || '';
            document.getElementById('cliente-celular').value = cliente.celular || '';
            document.getElementById('cliente-tel-recado').value = cliente.tel_recado || '';
            document.getElementById('cliente-email').value = cliente.email || '';
            document.getElementById('cliente-cpf').value = cliente.cpf || '';
            document.getElementById('cliente-nascimento').value = cliente.nascimento || '';
            
            // Logica CNH
            if (cliente.cnh === 'Sim') document.getElementById('cnh-sim').checked = true;
            else if (cliente.cnh === 'Não') document.getElementById('cnh-nao').checked = true;
            else document.getElementById('cnh-ni').checked = true;

            document.getElementById('cliente-observacao').value = cliente.observacao || '';

            formTitulo.textContent = `Editando: ${cliente.nome}`;
            btnSalvar.classList.add('d-none');
            btnAtualizar.classList.remove('d-none');
            btnExcluir.classList.remove('d-none');
            
            clientePropostasArea.style.display = 'block';
            clientePropostasTitulo.textContent = `Propostas de ${cliente.nome}`;
            carregarPropostasDoCliente(cliente.nome);

        } else { 
            formTitulo.textContent = 'Cadastrar Novo Cliente';
            btnSalvar.classList.remove('d-none');
            btnAtualizar.classList.add('d-none');
            btnExcluir.classList.add('d-none');
            clientePropostasArea.style.display = 'none';
            $(searchSelect).val(null).trigger('change'); 
        }
    };

    const carregarPropostasDoCliente = async (nomeCliente) => {
        tbodyClientePropostas.innerHTML = `<tr><td colspan="8">Carregando propostas...</td></tr>`;
        try {
            const response = await fetch(`/api/propostas/por-cliente/${encodeURIComponent(nomeCliente)}`);
            if (!response.ok) throw new Error('Erro ao buscar propostas do cliente.');
            const propostas = await response.json();
            renderizarTabelaPropostasCliente(propostas);
        } catch (error) {
            tbodyClientePropostas.innerHTML = `<tr><td colspan="8" class="text-danger">${error.message}</td></tr>`;
        }
    };

    const renderizarTabelaPropostasCliente = (propostas) => {
        tbodyClientePropostas.innerHTML = '';
        if (propostas.length === 0) {
            tbodyClientePropostas.innerHTML = '<tr><td colspan="7" class="text-center">Nenhuma proposta encontrada para este cliente.</td></tr>';
            return;
        }
        propostas.forEach(p => {
            const tr = document.createElement('tr');
            
            const ano = (p.ano_min && p.ano_max && p.ano_min !== p.ano_max) ? `${p.ano_min}-${p.ano_max}` : (p.ano_min || p.ano_max || '');
            let precoExibido = '';
            const precoMinF = p.preco_min ? new Intl.NumberFormat('pt-BR').format(p.preco_min) : '';
            const precoMaxF = p.preco_max ? new Intl.NumberFormat('pt-BR').format(p.preco_max) : '';
            if (precoMinF && precoMaxF) precoExibido = (precoMinF === precoMaxF) ? precoMaxF : `${precoMinF} - ${precoMaxF}`;
            else precoExibido = precoMinF || precoMaxF;

            const badge = `<span class="badge bg-${p.tipo === 'Compra' ? 'primary' : 'success'} text-capitalize">${p.tipo}</span>`;
            
            let cambioIcon = '';
            if (p.cambio === 'Automatico') cambioIcon = `<i class="bi bi-gear-wide-connected cambio-icon text-muted ms-1" data-bs-toggle="tooltip" title="Automático"></i>`;
            else if (p.cambio === 'Manual') cambioIcon = `<i class="bi bi-gear cambio-icon text-muted ms-1" data-bs-toggle="tooltip" title="Manual"></i>`;
            
            let corSwatch = '';
            if (p.cor) {
                const corMap = { "BRANCA": "white", "PRETA": "black", "PRATA": "silver", "CINZA": "gray", "VERMELHA": "red", "AZUL": "blue", "VERDE": "green", "AMARELA": "yellow", "MARRON": "saddlebrown", "DOURADA": "gold", "VINHO": "maroon" };
                const corCss = corMap[p.cor.toUpperCase()] || p.cor.toLowerCase();
                const corStyle = `background-color: ${corCss};`;
                corSwatch = `<span class="color-swatch" style="${corStyle}" data-bs-toggle="tooltip" title="${p.cor}"></span>`;
            }

            let obsInfo = '';
            if (p.observacoes) {
                obsInfo = ` <i class="bi bi-info-circle ms-2 text-info" data-bs-toggle="tooltip" title="${p.observacoes}"></i>`;
            }

            let veiculoDesc = `${p.fabricante || ''} - ${p.modelo || ''}${cambioIcon}${corSwatch}${obsInfo}`;
            
            tr.innerHTML = `
                <td>${p.id}</td>
                <td>${p.data_inclusao}</td>
                <td>${badge}</td>
                <td>${p.categoria||''}</td>
                <td>${veiculoDesc}</td>
                <td>${ano}</td>
                <td>${precoExibido}</td>
                <td>
                    <button class="btn btn-sm btn-primary btn-icon btn-visualizar-proposta" data-id="${p.id}" data-bs-toggle="tooltip" title="Ver/Editar Proposta">
                        <i class="bi bi-eye"></i>
                    </button>
                </td>
            `;
            tbodyClientePropostas.appendChild(tr);
        });
        [...tbodyClientePropostas.querySelectorAll('[data-bs-toggle="tooltip"]')].map(el => new bootstrap.Tooltip(el));
    };

    const salvarOuAtualizarCliente = async () => {
        const clienteData = {
            id: clienteIdInput.value ? parseInt(clienteIdInput.value) : null,
            nome: document.getElementById('cliente-nome').value,
            celular: document.getElementById('cliente-celular').value,
            tel_recado: document.getElementById('cliente-tel-recado').value,
            email: document.getElementById('cliente-email').value,
            cpf: document.getElementById('cliente-cpf').value,
            nascimento: document.getElementById('cliente-nascimento').value,
            cnh: document.querySelector('input[name="cliente-cnh"]:checked').value,
            observacao: document.getElementById('cliente-observacao').value
        };

        if (!clienteData.nome) {
            alert('O campo Nome é obrigatório.');
            return;
        }

        try {
            const response = await fetch('/api/clientes/salvar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(clienteData)
            });
            const resultado = await response.json();
            if (!resultado.success) throw new Error(resultado.message);

            alert(resultado.message);
            await carregarTodosClientes();
            mudarModoFormulario('novo');
            if (typeof popularSelect === 'function') {
                 popularSelect(document.getElementById('prop-pessoa'), '/api/clientes/listar-nomes', 'Selecione');
            }
        } catch (error) { alert(`Erro: ${error.message}`); }
    };
    
    $(searchSelect).on('change', function() {
        const selectedId = $(this).val();
        if (selectedId) {
            const cliente = todosClientes.find(c => c.id == selectedId);
            if (cliente) mudarModoFormulario('edicao', cliente);
        }
    });
    
    btnLimpar.addEventListener('click', () => mudarModoFormulario('novo'));
    formCliente.addEventListener('submit', (e) => { e.preventDefault(); salvarOuAtualizarCliente(); });
    btnAtualizar.addEventListener('click', salvarOuAtualizarCliente);
    btnExcluir.addEventListener('click', async () => {
        const id = clienteIdInput.value;
        const nome = document.getElementById('cliente-nome').value;
        if (!id) return;
        if (confirm(`Tem certeza que deseja excluir "${nome}"?`)) {
            try {
                const response = await fetch(`/api/clientes/excluir/${id}`, { method: 'DELETE' });
                const resultado = await response.json();
                if (!resultado.success) throw new Error(resultado.message);
                alert(resultado.message);
                await carregarTodosClientes();
                mudarModoFormulario('novo');
                if (typeof popularSelect === 'function') {
                     popularSelect(document.getElementById('prop-pessoa'), '/api/clientes/listar-nomes', 'Selecione');
                }
            } catch (error) { alert(`Erro: ${error.message}`); }
        }
    });

    tbodyClientePropostas.addEventListener('click', (e) => {
        const btnVisualizar = e.target.closest('.btn-visualizar-proposta');
        if (btnVisualizar) {
            const propostaId = btnVisualizar.dataset.id;
            if (typeof carregarPropostaParaEdicao === 'function') carregarPropostaParaEdicao(propostaId);
            else alert('Função para visualizar proposta não encontrada.');
        }
    });
    
    const tabNav = document.getElementById('tab-clientes-nav');
    tabNav.addEventListener('shown.bs.tab', carregarTodosClientes, { once: true });
});