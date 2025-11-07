// static/clientes.js

document.addEventListener('DOMContentLoaded', () => {
    const formCliente = document.getElementById('form-cliente');
    if (!formCliente) return;

    // MAPEAMENTO
    const tbodyClientes = document.getElementById('tbody-clientes');
    const formTitulo = document.getElementById('form-cliente-titulo');
    const btnLimparCliente = document.getElementById('btn-limpar-cliente');
    const clientePropostasArea = document.getElementById('cliente-propostas-area');
    const tbodyClientePropostas = document.getElementById('tbody-cliente-propostas');
    const clientePropostasTitulo = document.getElementById('cliente-propostas-titulo');

    // FUNÇÕES
    const carregarClientes = async () => {
        try {
            const response = await fetch('/api/clientes/listar');
            if (!response.ok) throw new Error('Falha ao carregar clientes.');
            renderizarTabelaClientes(await response.json());
        } catch (error) {
            tbodyClientes.innerHTML = `<tr><td colspan="4" class="text-danger">${error.message}</td></tr>`;
        }
    };

    const renderizarTabelaClientes = (clientes) => {
        tbodyClientes.innerHTML = '';
        if (clientes.length === 0) {
            tbodyClientes.innerHTML = '<tr><td colspan="4" class="text-center">Nenhum cliente cadastrado.</td></tr>';
            return;
        }
        clientes.forEach(cliente => {
            const tr = document.createElement('tr');
            tr.dataset.cliente = JSON.stringify(cliente);
            const obs = cliente.observacao || '';
            tr.innerHTML = `
                <td>${cliente.nome || ''}</td>
                <td>${cliente.celular || ''}</td>
                <td>${obs.substring(0, 30)}${obs.length > 30 ? '...' : ''}</td>
                <td>
                    <button class="btn btn-sm btn-warning btn-editar-cliente">Editar</button>
                    <button class="btn btn-sm btn-danger btn-excluir-cliente" data-id="${cliente.id}">Excluir</button>
                </td>
            `;
            tbodyClientes.appendChild(tr);
        });
    };
    
    const limparFormulario = () => {
        formCliente.reset();
        document.getElementById('cnh-nao').checked = true; // Valor padrão
        document.getElementById('cliente-id').value = '';
        formTitulo.textContent = 'Cadastrar Novo Cliente';
        clientePropostasArea.style.display = 'none';
        document.getElementById('btn-salvar-cliente').textContent = 'Salvar';
    };

    const preencherFormularioParaEdicao = async (cliente) => {
        limparFormulario();
        document.getElementById('cliente-id').value = cliente.id;
        document.getElementById('cliente-nome').value = cliente.nome || '';
        document.getElementById('cliente-celular').value = cliente.celular || '';
        document.getElementById('cliente-tel-recado').value = cliente.tel_recado || '';
        document.getElementById('cliente-email').value = cliente.email || '';
        document.getElementById('cliente-cpf').value = cliente.cpf || '';
        document.getElementById('cliente-nascimento').value = cliente.nascimento || '';
        if (cliente.cnh === 'Sim') document.getElementById('cnh-sim').checked = true;
        else document.getElementById('cnh-nao').checked = true;
        document.getElementById('cliente-observacao').value = cliente.observacao || '';
        
        formTitulo.textContent = `Editando: ${cliente.nome}`;
        document.getElementById('btn-salvar-cliente').textContent = 'Atualizar';
        
        clientePropostasArea.style.display = 'block';
        clientePropostasTitulo.textContent = `Propostas de ${cliente.nome}`;
        await carregarPropostasDoCliente(cliente.nome);
        window.scrollTo(0, 0);
    };

    const carregarPropostasDoCliente = async (nomeCliente) => {
        tbodyClientePropostas.innerHTML = `<tr><td colspan="4">Carregando...</td></tr>`;
        try {
            const response = await fetch(`/api/propostas/por-cliente/${encodeURIComponent(nomeCliente)}`);
            const propostas = await response.json();
            
            tbodyClientePropostas.innerHTML = '';
            if (propostas.length === 0) {
                tbodyClientePropostas.innerHTML = '<tr><td colspan="4">Nenhuma proposta encontrada.</td></tr>';
                return;
            }
            propostas.forEach(p => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${p.id}</td><td>${p.tipo}</td>
                    <td>${p.fabricante||''} ${p.modelo||''} ${p.ano_min||''}</td>
                    <td><button class="btn btn-sm btn-primary btn-visualizar-proposta" data-id="${p.id}">Visualizar</button></td>`;
                tbodyClientePropostas.appendChild(tr);
            });
        } catch (error) {
            tbodyClientePropostas.innerHTML = `<tr><td colspan="4" class="text-danger">Erro ao carregar propostas.</td></tr>`;
        }
    };

    // EVENT LISTENERS
    formCliente.addEventListener('submit', async (e) => {
        e.preventDefault();
        const clienteData = {
            id: document.getElementById('cliente-id').value ? parseInt(document.getElementById('cliente-id').value) : null,
            nome: document.getElementById('cliente-nome').value,
            celular: document.getElementById('cliente-celular').value,
            tel_recado: document.getElementById('cliente-tel-recado').value,
            email: document.getElementById('cliente-email').value,
            cpf: document.getElementById('cliente-cpf').value,
            nascimento: document.getElementById('cliente-nascimento').value,
            cnh: document.querySelector('input[name="cliente-cnh"]:checked').value,
            observacao: document.getElementById('cliente-observacao').value
        };
        try {
            const response = await fetch('/api/clientes/salvar', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(clienteData) });
            const resultado = await response.json();
            if (!resultado.success) throw new Error(resultado.message);

            alert(resultado.message);
            limparFormulario();
            await carregarClientes();
            if (typeof popularSelect === 'function') {
                 popularSelect(document.getElementById('prop-pessoa'), '/api/clientes/listar-nomes', 'Selecione');
            }
        } catch (error) { alert(`Erro: ${error.message}`); }
    });

    btnLimparCliente.addEventListener('click', limparFormulario);

    tbodyClientes.addEventListener('click', async (e) => {
        const btnEditar = e.target.closest('.btn-editar-cliente');
        const btnExcluir = e.target.closest('.btn-excluir-cliente');

        if (btnEditar) {
            const cliente = JSON.parse(btnEditar.closest('tr').dataset.cliente);
            preencherFormularioParaEdicao(cliente);
        }
        if (btnExcluir) {
            const clienteId = btnExcluir.dataset.id;
            const nomeCliente = btnExcluir.closest('tr').cells[0].textContent;
            if (confirm(`Tem certeza que deseja excluir "${nomeCliente}"?`)) {
                try {
                    const response = await fetch(`/api/clientes/excluir/${clienteId}`, { method: 'DELETE' });
                    const resultado = await response.json();
                    if (!resultado.success) throw new Error(resultado.message);
                    alert(resultado.message);
                    await carregarClientes();
                } catch (error) { alert(`Erro: ${error.message}`); }
            }
        }
    });

    tbodyClientePropostas.addEventListener('click', (e) => {
        const btnVisualizar = e.target.closest('.btn-visualizar-proposta');
        if(btnVisualizar) {
            const propostaId = btnVisualizar.dataset.id;
            if(typeof carregarPropostaParaEdicao === 'function') {
                carregarPropostaParaEdicao(propostaId);
            }
        }
    });

    carregarClientes();
});