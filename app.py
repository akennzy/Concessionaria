from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime
import locale

# Configuração de localização para moeda brasileira
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

app = Flask(__name__)
app.secret_key = "chave_secreta_concessionaria"

# Funções auxiliares para manipulação de dados
def carregar_veiculos():
    try:
        with open('veiculos.json', 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        # Criar arquivo com dados padrão se não existir
        veiculos = [
            {
                "id": 1,
                "modelo": "SUV X200",
                "marca": "AutoTech",
                "ano": 2023,
                "preco": 120000.00,
                "tipo": "novo",
                "status": "disponível",
                "motor": "2.0 Turbo",
                "potencia": "200 cv",
                "combustivel": "Flex",
                "cambio": "Automático",
                "quilometragem": 0,
                "cor": "Preto",
                "descricao": "SUV compacto com design moderno e tecnologia de ponta.",
                "imagem": "suv_x200.jpg"
            },
            {
                "id": 2,
                "modelo": "Sedan LX",
                "marca": "CarMaster",
                "ano": 2022,
                "preco": 85000.00,
                "tipo": "usado",
                "status": "disponível",
                "motor": "1.6",
                "potencia": "120 cv",
                "combustivel": "Flex",
                "cambio": "Manual",
                "quilometragem": 35000,
                "cor": "Prata",
                "descricao": "Sedan espaçoso, econômico e em excelente estado.",
                "imagem": "sedan_lx.jpg"
            },
            {
                "id": 3,
                "modelo": "Hatch Turbo",
                "marca": "SpeedCar",
                "ano": 2023,
                "preco": 75000.00,
                "tipo": "novo",
                "status": "em manutenção",
                "motor": "1.0 Turbo",
                "potencia": "130 cv",
                "combustivel": "Flex",
                "cambio": "Manual",
                "quilometragem": 0,
                "cor": "Vermelho",
                "descricao": "Hatch esportivo com excelente desempenho e baixo consumo.",
                "imagem": "hatch_turbo.jpg"
            },
            {
                "id": 4,
                "modelo": "Pickup 4x4",
                "marca": "TruckPower",
                "ano": 2021,
                "preco": 180000.00,
                "tipo": "usado",
                "status": "reservado",
                "motor": "3.0 Diesel",
                "potencia": "250 cv",
                "combustivel": "Diesel",
                "cambio": "Automático",
                "quilometragem": 45000,
                "cor": "Azul",
                "descricao": "Pickup robusta para trabalho pesado e lazer.",
                "imagem": "pickup_4x4.jpg"
            },
            {
                "id": 5,
                "modelo": "Elétrico EV",
                "marca": "EcoTech",
                "ano": 2023,
                "preco": 220000.00,
                "tipo": "novo",
                "status": "disponível",
                "motor": "Elétrico",
                "potencia": "300 cv",
                "combustivel": "Elétrico",
                "cambio": "Automático",
                "quilometragem": 0,
                "cor": "Branco",
                "descricao": "Carro 100% elétrico com autonomia de 450 km.",
                "imagem": "eletrico_ev.jpg"
            }
        ]
        with open('veiculos.json', 'w', encoding='utf-8') as arquivo:
            json.dump(veiculos, arquivo, indent=4, ensure_ascii=False)
        return veiculos

def salvar_veiculos(veiculos):
    with open('veiculos.json', 'w', encoding='utf-8') as arquivo:
        json.dump(veiculos, arquivo, indent=4, ensure_ascii=False)

def carregar_agendamentos():
    try:
        with open('agendamentos.json', 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        # Criar arquivo vazio se não existir
        with open('agendamentos.json', 'w', encoding='utf-8') as arquivo:
            json.dump([], arquivo)
        return []

def salvar_agendamento(agendamento):
    agendamentos = carregar_agendamentos()
    # Gerar ID para novo agendamento
    if agendamentos:
        novo_id = max(item['id'] for item in agendamentos) + 1
    else:
        novo_id = 1
    
    agendamento['id'] = novo_id
    agendamentos.append(agendamento)
    
    with open('agendamentos.json', 'w', encoding='utf-8') as arquivo:
        json.dump(agendamentos, arquivo, indent=4, ensure_ascii=False)

def formatar_moeda(valor):
    return locale.currency(valor, grouping=True)

# Rotas da aplicação
@app.route('/')
def index():
    veiculos = carregar_veiculos()
    tipo_filtro = request.args.get('tipo', '')
    
    if tipo_filtro:
        veiculos_filtrados = [v for v in veiculos if v['tipo'] == tipo_filtro]
    else:
        veiculos_filtrados = veiculos
    
    for veiculo in veiculos_filtrados:
        veiculo['preco_formatado'] = formatar_moeda(veiculo['preco'])
    
    return render_template('index.html', veiculos=veiculos_filtrados, filtro=tipo_filtro)

@app.route('/detalhe/<int:veiculo_id>')
def detalhe(veiculo_id):
    veiculos = carregar_veiculos()
    veiculo = next((v for v in veiculos if v['id'] == veiculo_id), None)
    
    if not veiculo:
        flash('Veículo não encontrado.')
        return redirect(url_for('index'))
    
    veiculo['preco_formatado'] = formatar_moeda(veiculo['preco'])
    
    return render_template('detalhe.html', veiculo=veiculo)

@app.route('/agendar/<int:veiculo_id>', methods=['GET', 'POST'])
def agendar(veiculo_id):
    veiculos = carregar_veiculos()
    veiculo = next((v for v in veiculos if v['id'] == veiculo_id), None)
    
    if not veiculo:
        flash('Veículo não encontrado.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        data = request.form['data']
        horario = request.form['horario']
        
        # Validações básicas
        if not (nome and telefone and data and horario):
            flash('Por favor, preencha todos os campos.')
            return render_template('agendar.html', veiculo=veiculo)
        
        novo_agendamento = {
            'nome': nome,
            'telefone': telefone,
            'data': data,
            'horario': horario,
            'veiculo_id': veiculo_id,
            'modelo_veiculo': veiculo['modelo'],
            'marca_veiculo': veiculo['marca'],
            'status': 'pendente',
            'data_agendamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        salvar_agendamento(novo_agendamento)
        flash('Test drive agendado com sucesso!')
        return redirect(url_for('index'))
    
    return render_template('agendar.html', veiculo=veiculo)

@app.route('/simular/<int:veiculo_id>', methods=['GET', 'POST'])
def simular(veiculo_id):
    veiculos = carregar_veiculos()
    veiculo = next((v for v in veiculos if v['id'] == veiculo_id), None)
    
    if not veiculo:
        flash('Veículo não encontrado.')
        return redirect(url_for('index'))
    
    veiculo['preco_formatado'] = formatar_moeda(veiculo['preco'])
    resultado = None
    
    if request.method == 'POST':
        try:
            entrada = float(request.form['entrada'].replace('.', '').replace(',', '.'))
            parcelas = int(request.form['parcelas'])
            taxa_juros = 1.5  # Taxa de juros mensal (%)
            
            if entrada < 0 or entrada >= veiculo['preco']:
                flash('Valor de entrada inválido.')
                return render_template('simular.html', veiculo=veiculo, resultado=None)
                
            if parcelas <= 0 or parcelas > 72:
                flash('Número de parcelas deve estar entre 1 e 72.')
                return render_template('simular.html', veiculo=veiculo, resultado=None)
            
            valor_financiar = veiculo['preco'] - entrada
            # Cálculo de juros compostos
            taxa_decimal = taxa_juros / 100
            valor_parcela = (valor_financiar * taxa_decimal) / (1 - (1 + taxa_decimal) ** -parcelas)
            
            resultado = {
                'entrada': formatar_moeda(entrada),
                'valor_financiar': formatar_moeda(valor_financiar),
                'parcelas': parcelas,
                'valor_parcela': formatar_moeda(valor_parcela),
                'total': formatar_moeda(entrada + (valor_parcela * parcelas))
            }
            
        except (ValueError, TypeError):
            flash('Por favor, insira valores válidos.')
    
    return render_template('simular.html', veiculo=veiculo, resultado=resultado)

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        
        if usuario == 'admin' and senha == '1234':
            session['logado'] = True
            return redirect(url_for('painel'))
        else:
            erro = 'Usuário ou senha inválidos.'
    
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.pop('logado', None)
    return redirect(url_for('index'))

@app.route('/painel')
def painel():
    if not session.get('logado'):
        flash('Acesso restrito. Faça login para continuar.')
        return redirect(url_for('login'))
    
    agendamentos = carregar_agendamentos()
    # Ordenar agendamentos por data e horário (mais recentes primeiro)
    agendamentos.sort(key=lambda x: x['data_agendamento'], reverse=True)
    
    return render_template('painel.html', agendamentos=agendamentos)

@app.route('/editar/<int:veiculo_id>', methods=['GET', 'POST'])
def editar(veiculo_id):
    if not session.get('logado'):
        flash('Acesso restrito. Faça login para continuar.')
        return redirect(url_for('login'))
    
    veiculos = carregar_veiculos()
    veiculo = next((v for v in veiculos if v['id'] == veiculo_id), None)
    
    if not veiculo:
        flash('Veículo não encontrado.')
        return redirect(url_for('painel'))
    
    if request.method == 'POST':
        novo_status = request.form['status']
        
        for v in veiculos:
            if v['id'] == veiculo_id:
                v['status'] = novo_status
                break
        
        salvar_veiculos(veiculos)
        flash(f'Status do veículo {veiculo["modelo"]} atualizado para {novo_status}.')
        return redirect(url_for('painel'))
    
    return render_template('editar.html', veiculo=veiculo)

@app.route('/veiculos_admin')
def veiculos_admin():
    if not session.get('logado'):
        flash('Acesso restrito. Faça login para continuar.')
        return redirect(url_for('login'))
    
    veiculos = carregar_veiculos()
    for veiculo in veiculos:
        veiculo['preco_formatado'] = formatar_moeda(veiculo['preco'])
    
    return render_template('veiculos_admin.html', veiculos=veiculos)

@app.template_filter('formatar_data')
def formatar_data(data_str):
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d')
        return data.strftime('%d/%m/%Y')
    except:
        return data_str

if __name__ == '__main__':
    # Garantir que os arquivos de dados existam
    carregar_veiculos()
    carregar_agendamentos()
    app.run(debug=True)