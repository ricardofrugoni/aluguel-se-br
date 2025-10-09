# 🏠 Rental Price Prediction Dashboard

Dashboard interativo para análise de preços de aluguel por temporada no Sudeste
do Brasil.

## 🚀 Funcionalidades

### 🎯 Análise Sazonal (Tab 1)

- **Seleção de Propriedades**: Escolha manual ou aleatória

- **Análise de Discrepância**: Indicadores visuais de sazonalidade

- **Métricas Detalhadas**: Alta vs baixa temporada

- **Gráficos Duais**: Preços absolutos + variações percentuais

- **Tabela Mensal**: Breakdown detalhado por mês

- **Recomendações Inteligentes**: Melhores meses para reservar

### 📊 Visão Geral do Mercado (Tab 2)

- Métricas agregadas do mercado

- Análise por cidade e tipo de propriedade

- Distribuição de preços e ratings

### 🏠 Comparação de Propriedades (Tab 3)

- Comparação lado a lado

- Análise de features similares

- Benchmarking de preços

### 🔮 Predição de Preços (Tab 4)

- Formulário de entrada de dados

- Predição baseada em features

- Análise de impacto de variáveis

## 🛠️ Instalação

### Pré-requisitos

```bash
pip install streamlit pandas numpy plotly

```text

### Execução Rápida

```bash

# Opção 1: Script automatizado

python run_dashboard.py

# Opção 2: Comando direto

streamlit run dashboard/globe_app.py

```text

## 📱 Interface

### 🎨 Design

- **Tema Escuro**: Interface moderna e profissional

- **Gradientes**: Cores vibrantes para destaque

- **Responsivo**: Adaptável a diferentes tamanhos de tela

- **Interativo**: Hover effects e animações

### 🎛️ Controles

- **Filtros Laterais**: Cidade, tipo de propriedade, faixa de preço

- **Seleção de Propriedades**: Dropdown ou botão aleatório

- **Navegação por Tabs**: Organização clara das funcionalidades

## 📊 Análise Sazonal Detalhada

### 🔥 Indicadores de Discrepância

- **EXTREME** (≥50%): 🔥🔥🔥 - Sazonalidade extrema

- **HIGH** (≥30%): 🔥🔥 - Alta sazonalidade

- **MODERATE** (≥15%): 🔥 - Sazonalidade moderada

- **LOW** (<15%): ✅ - Baixa sazonalidade

### 💰 Análise de Economia

- **Savings Potenciais**: Economia ao evitar alta temporada

- **Meses de Melhor Valor**: Períodos com preços mais baixos

- **Picos de Preço**: Meses a evitar para economizar

### 📈 Métricas Avançadas

- **Fatores Sazonais**: Multiplicadores por mês

- **Variações Percentuais**: Desvio do preço base

- **Extremos**: Mês mais caro vs mais barato

- **Diferença Máxima**: Variação entre pico e vale

## 🎯 Casos de Uso

### Para Hóspedes

- **Planejamento de Viagem**: Escolher melhores meses

- **Otimização de Orçamento**: Encontrar períodos mais baratos

- **Análise de Valor**: Entender drivers de preço

- **Comparação**: Avaliar diferentes propriedades

### Para Hosts

- **Estratégia de Preços**: Otimizar preços sazonais

- **Maximização de Receita**: Identificar períodos premium

- **Análise Competitiva**: Comparar com mercado

- **Planejamento**: Preparar para alta/baixa temporada

### Para Plataformas

- **Análise de Mercado**: Tendências e padrões

- **Recomendações**: Sugerir preços otimizados

- **Educação**: Ajudar hosts a otimizar

- **Insights**: Entender comportamento de preços

## 🔧 Configuração Avançada

### Personalização de Cores

```python

# Cores dos indicadores de discrepância

discrepancy_colors = {
    'EXTREME': '#ff0000',

    'HIGH': '#ff6b00',

    'MODERATE': '#ffaa00',

    'LOW': '#00ff00'

}

```text

### Fatores Sazonais

```python

# Rio de Janeiro (alta temporada no verão)

rio_factors = [1.5, 1.6, 1.2, 1.0, 0.9, 0.85, 0.9, 0.95, 1.0, 1.1, 1.2, 1.7]

# São Paulo (menos sazonal)

sp_factors = [1.3, 1.2, 1.0, 0.95, 0.9, 0.9, 1.2, 0.95, 1.0, 1.1, 1.1, 1.4]

```

## 📈 Métricas Disponíveis

### Análise Sazonal

- **Discrepância Percentual**: Variação entre alta e baixa temporada

- **Savings Potenciais**: Economia ao evitar picos

- **Fatores Mensais**: Multiplicadores por mês

- **Classificação**: Nível de sazonalidade

### Análise de Propriedades

- **Preço Base**: Preço de referência

- **Rating**: Avaliação média

- **Reviews**: Número de avaliações

- **Tipo**: Categoria da propriedade

### Análise de Mercado

- **Total de Propriedades**: Contagem geral

- **Preço Médio**: Média do mercado

- **Rating Médio**: Avaliação média

- **Superhosts**: Contagem de hosts premium

## 🚀 Próximas Funcionalidades

### 🔮 Predição Avançada

- **Modelo ML**: Integração com modelos treinados

- **Features Dinâmicas**: Input de amenidades e localização

- **Confiança**: Intervalos de predição

- **Sensibilidade**: Análise de impacto de variáveis

### 📊 Analytics Avançados

- **Clustering**: Agrupamento de propriedades similares

- **Correlações**: Análise de correlação entre features

- **Tendências**: Análise temporal de preços

- **Benchmarking**: Comparação com concorrentes

### 🗺️ Visualização Geográfica

- **Mapas Interativos**: Localização das propriedades

- **Heatmaps**: Densidade de preços por região

- **POIs**: Proximidade a pontos de interesse

- **Clusters**: Agrupamentos geográficos

## 🐛 Troubleshooting

### Problemas Comuns

1. **Streamlit não encontrado**: `pip install streamlit`

2. **Dependências faltando**: `pip install pandas numpy plotly`

3. **Porta ocupada**: Use `--server.port 8502`

4. **Erro de cache**: Limpe cache com `streamlit cache clear`

### Logs e Debug

```bash

# Executar com logs detalhados

streamlit run dashboard/globe_app.py --logger.level debug

# Limpar cache

streamlit cache clear

```

## 📞 Suporte

Para problemas ou sugestões:

- **Issues**: Abra uma issue no repositório

- **Documentação**: Consulte a documentação completa

- **Exemplos**: Veja `example_short_term_rentals.py`

---

## 🏠 Dashboard de Análise de Preços de Aluguel por Temporada - Sudeste do Brasil
