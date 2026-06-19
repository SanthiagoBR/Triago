"""Gerador de chamados sintéticos para testes de carga (Modo Simulação).

Combina modelos de frases por categoria para produzir um volume configurável de
tickets. Por padrão grava em ``data/synthetic_tickets.csv`` para NÃO sobrescrever
o conjunto de treino curado em ``data/training_data.csv``.

Uso:
    python scripts/generate_dataset.py            # 300 tickets -> synthetic_tickets.csv
    python scripts/generate_dataset.py -n 1000    # 1000 tickets
    python scripts/generate_dataset.py -o data/training_data.csv  # sobrescreve treino
"""

import argparse
import csv
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_OUTPUT = DATA_DIR / "synthetic_tickets.csv"

TEMPLATES = {
    "Banco de Dados": [
        "Erro ao conectar no banco de dados durante {ctx}",
        "Consulta SQL travando e gerando timeout no {ctx}",
        "Backup do banco não completou por falha de {ctx}",
        "Erro de permissão ao executar consulta no {ctx}",
        "Banco de dados corrompido após {ctx}",
    ],
    "Rede": [
        "Servidor de rede lento e desconectando no {ctx}",
        "Conexão Wi-Fi instável em {ctx}",
        "Falha na autenticação da VPN corporativa no {ctx}",
        "Perda de pacotes na rede durante {ctx}",
        "Sem acesso à internet no {ctx}",
    ],
    "Acesso/Login": [
        "Não consigo efetuar login no {ctx}",
        "Usuário e senha rejeitados ao acessar o {ctx}",
        "Solicitação para trocar senha do {ctx}",
        "Conta bloqueada após tentativas no {ctx}",
        "Usuário sem permissão para acessar o {ctx}",
    ],
    "Hardware": [
        "Computador não liga após {ctx}",
        "HD fazendo barulho estranho no {ctx}",
        "Tela azul ao iniciar o {ctx}",
        "Impressora não responde no {ctx}",
        "Notebook superaquecendo durante {ctx}",
    ],
    "Financeiro": [
        "Cobrança indevida no boleto do {ctx}",
        "Solicitação de reembolso não processada no {ctx}",
        "Falha ao lançar nota fiscal no {ctx}",
        "Divergência de valores no relatório {ctx}",
        "Pagamento não compensado no {ctx}",
    ],
}

CONTEXTS = [
    "setor financeiro", "departamento de RH", "filial de São Paulo", "matriz",
    "horário de pico", "fim de expediente", "processo de fechamento mensal",
    "ambiente de produção", "estação de trabalho", "servidor principal",
    "queda de energia", "atualização do sistema",
]


def generate(n: int, seed: int = 42):
    rng = random.Random(seed)
    categories = list(TEMPLATES)
    for _ in range(n):
        category = rng.choice(categories)
        template = rng.choice(TEMPLATES[category])
        text = template.format(ctx=rng.choice(CONTEXTS))
        urgency = rng.randint(1, 3)
        yield text, category, urgency


def main():
    parser = argparse.ArgumentParser(description="Gera chamados sintéticos para teste de carga.")
    parser.add_argument("-n", "--count", type=int, default=300, help="Número de tickets (padrão: 300)")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT, help="Arquivo de saída CSV")
    parser.add_argument("--seed", type=int, default=42, help="Semente para reprodutibilidade")
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "category", "urgency"])
        for text, category, urgency in generate(args.count, args.seed):
            writer.writerow([text, category, urgency])

    print(f"Gerados {args.count} chamados sintéticos em {args.output}")


if __name__ == "__main__":
    main()
