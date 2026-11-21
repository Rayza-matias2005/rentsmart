# RentSmart — Orçamento de Locação (R.M Imóveis)

Aplicação em Python (POO) que calcula o orçamento de locação de apartamentos, casas e estúdios, exibe um resumo detalhado e gera um CSV com a projeção dos 12 primeiros meses.

## Como executar

Requisitos: Python 3.8+ (não usa bibliotecas externas).

```bash
python rentsmart.py
```

O programa pergunta o tipo de imóvel, quartos, garagem/vagas, se há crianças (apartamentos) e em quantas parcelas (1 a 5) a taxa contratual será paga. Ao final, imprime o orçamento e cria `projecao_12_meses.csv`.

## Regras implementadas

| Item | Regra |
|---|---|
| Aluguel-base | Apartamento 1q: R$ 700 · Casa 1q: R$ 900 · Estúdio: R$ 1.200 |
| 2 quartos | Apartamento +R$ 200 · Casa +R$ 250 |
| Garagem | Casa/Apartamento: +R$ 300 (1 vaga) |
| Estúdio | Pacote de 2 vagas: R$ 250 · vaga adicional: R$ 60 |
| Desconto | Apartamento sem crianças: 5% sobre o aluguel já com adicionais |
| Taxa contratual | R$ 2.000, em até 5 parcelas, separada do aluguel |

### Decisões de projeto
- Estúdio com 1 vaga paga o pacote de 2 vagas (R$ 250); com 0 vagas não paga estacionamento.
- A taxa é parcelada a partir do mês 1; a diferença de centavos fica na última parcela.
- Valores monetários usam `Decimal` para evitar erros de ponto flutuante.
- O CSV usa `;` como separador e vírgula decimal (abre direto no Excel em português).

## Estrutura de classes

- `Imovel` (abstrata) → `Apartamento`, `Casa`, `Estudio`: cada tipo calcula seus adicionais (herança e polimorfismo).
- `Orcamento`: calcula subtotal, desconto, aluguel mensal, parcelas da taxa, resumo e CSV.
- Funções de entrada (`ler_inteiro`, `ler_sim_nao`) validam os dados digitados.

## Repositório
Link do GitHub: https://github.com/Rayza-matias2005/rentsmart.git
