async function carregarProdutos() {
    let resposta = await fetch('/produtos');
    let produtos = await resposta.json();
    let tabela = document.getElementById("tabela-produtos");
    tabela.innerHTML = "";

    produtos.forEach(produto => {
        let linha = document.createElement("tr");
        linha.innerHTML = `
            <td>${produto[1]}</td>
            <td>${produto[2]}</td>
            <td>R$ ${produto[3]}</td>
            <td>
                <button class="btn-editar" onclick="abrirEdicao(${produto[0]}, '${produto[1]}', ${produto[2]}, ${produto[3]})">✏️</button>
                <button class="btn-remover" onclick="removerProduto(${produto[0]})">🗑️</button>
            </td>
        `;
        tabela.appendChild(linha);
    });
}

async function removerProduto(id) {
    if (confirm("Tem certeza que deseja remover este produto?")) {
        await fetch(`/remover/${id}`, { method: 'DELETE' });
        carregarProdutos();
    }
}

function limparInputsProdutos (nome, preco, quantidade) {
    document.getElementById("nome").value = "";
    document.getElementById("preco").value = "";
    document.getElementById("quantidade").value = "";
}

function abrirEdicao(id, nome, quantidade, preco) {
    document.getElementById("edit-id").value = id;
    document.getElementById("edit-nome").value = nome;
    document.getElementById("edit-quantidade").value = quantidade;
    document.getElementById("edit-preco").value = preco;
    document.getElementById("popup-editar").style.display = "block";
}

function abrirPopup() {
    document.getElementById("popup").style.display = "block";
}

function fecharPopupEdicao() {
    document.getElementById("popup-editar").style.display = "none";
}

function fecharPopup() {
    document.getElementById("popup").style.display = "none";
    limparInputsProdutos()
    
}

async function adicionarProduto() {
    let nome = document.getElementById("nome").value;
    let quantidade = document.getElementById("quantidade").value;
    let preco = document.getElementById("preco").value;

    if (!nome || quantidade <= 0 || preco <= 0) {
        alert("Preencha os campos corretamente!");
        return;
    }

    await fetch('/api/adicionar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, quantidade, preco })
    });

    fecharPopup();
    carregarProdutos();
}

async function atualizarProduto() {
    let id = document.getElementById("edit-id").value;
    let quantidade = document.getElementById("edit-quantidade").value;
    let preco = document.getElementById("edit-preco").value;

    if (quantidade <= 0 || preco <= 0) {
        alert("Preencha os campos corretamente!");
        return;
    }

    await fetch(`/atualizar_produto/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantidade, preco })
    });

    fecharPopupEdicao();
    carregarProdutos();
}

async function register() {
    let username = document.getElementById("user").value;
    let password = document.getElementById("password").value;

    await fetch(`/register/insert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    alert("Usuario cadastrado")
}

function exportarExcel() {
    let link = document.createElement("a");
    link.href = "/exportar_excel";
    link.download = "relatorio_estoque.xlsx";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link)
}

const nomes = produtos.map(produto => produto[0]);
const quantidades = produtos.map(produto => produto[1]);

const ctx = document.getElementById('meuGrafico');

new Chart(ctx, {
    type: 'bar',

    data: {
        labels: nomes,

        datasets: [{
            label: 'Quantidade',
            data: quantidades
        }]
    }
});