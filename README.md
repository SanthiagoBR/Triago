# Triago — Sistema Inteligente de Triagem e Roteamento de Chamados

![Versão](https://img.shields.io/badge/versão-0.1--conceitual-blue)
![Data](https://img.shields.io/badge/data-10%2F06%2F2026-green)

O **Triago** é um sistema baseado em agentes inteligentes projetado para automatizar a triagem de chamados de suporte técnico [1]. Ao receber um ticket em texto livre, o sistema utiliza inteligência artificial para identificar a categoria e a urgência, decidindo automaticamente qual atendente deve receber o chamado [1].

## 📋 Resumo do Projeto
O objetivo central do Triago é minimizar o tempo de resposta ponderado pela urgência do chamado [2]. Ele resolve ineficiências operacionais como a demora no atendimento por classificação manual, erros de encaminhamento que geram retrabalho e a sobrecarga desigual da equipe [4].

## 🚀 Funcionalidades Principais
*   **Classificação Automática:** Utiliza IA para identificar categorias como Banco de Dados, Rede, Acesso/Login, Hardware e Financeiro, além de níveis de urgência [5].
*   **Roteamento Inteligente:** Atribui tickets usando o algoritmo *Greedy Best-First Search* [5].
*   **Painel de Monitoramento:** Interface web que exibe a fila, o atendente escolhido e a justificativa da decisão [6].
*   **Modo Simulação:** Geração de chamados sintéticos para testes de carga [6].
*   **Logs Auditáveis:** Registro completo das probabilidades e custos heurísticos de cada decisão [6].

## 🧠 Arquitetura Técnica e IA

### 1. Classificador Probabilístico (Naive Bayes)
Implementado do zero pela equipe para garantir transparência, utiliza a técnica de *bag-of-words* [2, 7].
*   **Algoritmo:** Naive Bayes Multinomial [2].
*   **Diferencial:** Aplica o Teorema de Bayes com **Suavização de Laplace** para lidar com palavras inéditas sem zerar as probabilidades [7, 8].

### 2. Agente Baseado em Objetivos (Roteamento)
O sistema não apenas reage, mas planeja a atribuição para atingir metas globais de eficiência [8].
*   **Algoritmo de Busca:** *Greedy Best-First Search* [2].
*   **Função Heurística $h(n)$:** 
    $h(n) = \text{urgência} \times \text{tempo estimado de espera} + \text{penalidade de especialidade} + \text{penalidade de sobrecarga}$ [2, 9].
*   **Decisão Técnica:** Optou-se por este algoritmo em vez do A* porque em triagem o custo do caminho percorrido ($g$) é irrelevante, priorizando-se a resposta imediata em tempo $O(n)$ [10, 11].

## 🛠️ Stack Tecnológica
*   **Linguagem:** Python 3 [2, 12].
*   **Interface:** Streamlit [2, 12].
*   **Dados:** Estruturas leves em JSON e CSV [2, 12].

## ⚠️ Limitações da v0.1
*   Treinado com dataset simulado de aproximadamente 300 tickets [11, 13].
*   Sem integração nativa com Jira ou Zendesk [13].
*   Suporte exclusivo para chamados em português [13].
*   Estimativas de tempo de atendimento fixas por categoria [13].

## 🔮 Roadmap (v0.2)
1.  **Aprendizado Contínuo:** Re-treinamento periódico com feedback humano [14, 15].
2.  **Reotimização Global:** Uso de *Simulated Annealing* para balanceamento em picos de carga [14, 16].
3.  **Lógica Fuzzy:** Tratamento de urgência como variável contínua [14].
4.  **Integração Externa:** Conexão com APIs de helpdesk reais e suporte a anexos [14].

## 👥 Equipe
*   Santhiago Chapiewski [1, 4]
*   Pedro Henrique Santos [1, 4]
