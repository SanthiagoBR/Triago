import csv
from pathlib import Path

TRAINING_PATH = Path(__file__).resolve().parent.parent / "data" / "training_data.csv"

EXAMPLES = [
    ("Erro ao conectar no banco de dados durante backup", "Banco de Dados"),
    ("Não consigo acessar o sistema, usuário e senha rejeitados", "Acesso/Login"),
    ("Servidor de rede está lento e desconectando frequentemente", "Rede"),
    ("Computador não liga após queda de energia", "Hardware"),
    ("Solicitação de reembolso não processada no financeiro", "Financeiro"),
]

with TRAINING_PATH.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["text", "category"])
    for text, category in EXAMPLES:
        writer.writerow([text, category])

print(f"Generated {TRAINING_PATH}")
