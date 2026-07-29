# 💊 Painel de Monitoramento da Assistência Farmacêutica — Prefeitura Municipal de Cambé

Este repositório contém o código-fonte de um dashboard interativo desenvolvido em **Python** e **Streamlit** para apoiar o planejamento e as tomadas de decisão da **Comissão de Assistência Farmacêutica** do Município de Cambé - PR.

A ferramenta transforma os registros de distribuição e custos de medicamentos em indicadores visuais, dinâmicos e de fácil interpretação.

---

## 🚀 Funcionalidades Principal

- **Classificação Dinâmica (Curva ABC):**
  - **Classe A (Alto Impacto):** Medicamentos cujas saídas ou custos representam até **30%** do total acumulado no período filtrado.
  - **Classe B (Médio Impacto):** Medicamentos que compõem os **40%** seguintes do total acumulado.
  - **Classe C (Baixo Impacto):** Medicamentos restantes (30% finais do total acumulado).
- **Flexibilidade de Métricas:**
  - Alternância entre **Volume Financeiro (R$)** e **Volume de Movimentação (Quantidade)**.
  - Alternância de método de análise entre **Consumo Médio Mensal** e **Acumulado do Período**.
- **Filtros de Período Customizáveis:**
  - Seleção livre do mês/ano inicial e mês/ano final de análise na barra lateral.
- **Navegação por Abas:**
  - **📂 Introdução:** Contextualização da ferramenta e explicação das regras de negócio/Curva ABC.
  - **📊 Classe de Medicamentos:** Ranking Top 10 dos medicamentos da classe selecionada e gráfico de tendência histórica.
  - **📈 Medicamento Individual:** Consulta detalhada de um medicamento específico com indicadores numéricos e série temporal.
- **Internacionalização:** Formatação de números e valores no padrão brasileiro (`R$ 1.234,56` e `1.234`).

---

## 🛠️ Tecnologias Utilizadas

- **[Python](https://www.python.org/)** (v3.10+)
- **[Streamlit](https://streamlit.io/)** — Framework web interativo
- **[Pandas](https://pandas.pydata.org/)** — Manipulação e tratamento de dados
- **[Plotly](https://plotly.com/python/)** — Gráficos interativos
- **[OpenPyXL](https://openpyxl.readthedocs.io/)** — Leitura de arquivos `.xlsx`

---

## 📂 Estrutura do Repositório

```text
├── dadosABC.xlsx          # Planilha com a base de dados histórica
├── dashboard_ABC.py       # Código principal da aplicação Streamlit
├── requirements.txt       # Dependências do projeto
└── README.md              # Documentação do projeto
