import json
import streamlit as st
from triago import (
    GreedyRouter,
    NaiveBayesClassifier,
    Technician,
    append_decision_log,
    load_category_durations,
    load_decision_logs,
    load_technicians,
    load_training_data,
)


@st.cache_data
def load_data():
    technicians_data = load_technicians()
    technicians = [Technician(**tech) for tech in technicians_data]
    category_durations = load_category_durations()
    training_data = load_training_data()
    return technicians, category_durations, training_data


def build_classifier(training_data):
    classifier = NaiveBayesClassifier(alpha=1.0)
    documents = [row["text"] for row in training_data]
    labels = [row["category"] for row in training_data]
    classifier.fit(documents, labels)
    return classifier


def main():
    st.title("Triago — Sistema Inteligente de Triagem e Roteamento de Chamados")
    st.markdown(
        "Sistema conceitual para classificação automática de tickets, roteamento heurístico e auditoria de decisões."
    )

    technicians, category_durations, training_data = load_data()
    if not training_data:
        st.warning("Nenhum dado de treinamento disponível. Verifique data/training_data.csv.")
        return

    classifier = build_classifier(training_data)
    router = GreedyRouter(technicians, category_durations)

    st.sidebar.header("Configuração de Ticket")
    text = st.sidebar.text_area("Descrição do chamado", height=150)
    category_override = st.sidebar.selectbox(
        "Categoria (opcional)", ["", "Banco de Dados", "Rede", "Acesso/Login", "Hardware", "Financeiro"]
    )
    urgency = st.sidebar.slider("Urgência", 1, 3, 2)

    if st.sidebar.button("Classificar e Rotejar"):
        if not text.strip():
            st.error("Informe a descrição do chamado antes de processar.")
        else:
            category = category_override or classifier.predict(text)
            probabilities = classifier.predict_proba(text)
            ticket = router.build_ticket(text, category, urgency)
            technician, metrics = router.assign(ticket)
            decision = {
                "text": text,
                "category": category,
                "urgency": urgency,
                "probabilities": probabilities,
                "technician": technician.name if technician else None,
                "metrics": metrics,
                "timestamp": st.session_state.get("timestamp", None),
            }
            append_decision_log(decision)
            st.subheader("Resultado da Triagem")
            st.write("**Categoria prevista:**", category)
            st.write("**Técnico selecionado:**", technician.name if technician else "Nenhum disponível")
            st.write("**Justificativa de heurística:**")
            st.json(metrics)
            st.write("**Probabilidades do Naive Bayes:**")
            st.json(probabilities)

    st.sidebar.header("Painel de Monitoramento")
    st.write("### Técnicos e Filas")
    for tech in router.get_technicians():
        st.write(f"**{tech.name}** — Especialidade: {tech.specialty}")
        st.write(f"Fila atual: {tech.queue_length} tickets, espera estimada {tech.estimated_wait:.1f} min")
        st.write("---")

    st.write("### Logs de Decisão")
    logs = load_decision_logs()
    if logs:
        st.write(f"Total de decisões registradas: {len(logs)}")
        st.write(logs[-5:])
    else:
        st.info("Ainda não há decisões registradas.")

    st.write("### Treinamento e Dados")
    st.write(f"Chamados de treinamento: {len(training_data)}")
    st.write("Categorias suportadas: Banco de Dados, Rede, Acesso/Login, Hardware, Financeiro")


if __name__ == "__main__":
    main()
