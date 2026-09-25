# Cosmetic Bot v2 · Desafio 2

Agente de vendas de cosméticos rodando no **Amazon Bedrock AgentCore Harness**, avaliado em duas frentes (AgentCore Evaluations e DeepEval) e testado com uma campanha de red teaming.

É a evolução do Cosmetic Bot do Desafio 1 ([teste_llm_judge](https://github.com/gustavolkbr/teste_llm_judge)).

| | |
|---|---|
| Modelo do bot | Claude Haiku 4.5 (Bedrock) |
| Modelo juiz | Claude Sonnet 4.5 (Bedrock), mais capaz que o bot avaliado |
| Ferramenta real | Code Interpreter (cálculo de pedido com desconto e conversão ml/oz) |
| Memória | AgentCore Memory, separada por cliente (`actorId`) e sessão (`sessionId`) |

---

## Onde está cada coisa

```
app/MyHarness/
  harness.json          configuração do agente (modelo, ferramenta, memória)
  system-prompt.md      prompt + catálogo de 25 produtos (versão final, com as 3 rodadas de correção)
  catalogo.json         catálogo original do mês 1 (base do retrieval_context do DeepEval)

exploratory/            a história do projeto, em ordem
  1-sessaoExploratoria1.md    sessão exploratória (20 perguntas, 5 categorias)
  2-sessaoRedTeam.md          red teaming (17 tentativas, 5 categorias)
  3-retestePosCorrecao.md     correção rodada 1 + reteste
  4-retestePosCorrecao2.md    correção rodada 2 + reteste
  5-retestePosCorrecao3.md    correção rodada 3 + reteste

golden_dataset.json     20 casos de teste (5 categorias x 4)

tests/                  Frente B: suíte DeepEval
  collect_baseline.py   chama o agente real e salva as respostas
  test_cosmetic_bot.py  aplica as métricas sobre as respostas salvas
  conftest.py           carrega dataset e respostas
  juiz.py               configura o modelo juiz

responses_baseline.json respostas do agente antes da rodada 3
responses_final.json    respostas do agente depois da rodada 3

agentcore/agentcore.json               inclui o avaliador customizado da Frente A (MyEvaluator)
eval_2026-09-25_02-42-23.json          resultado da Frente A
```

---

## Linha do tempo e decisões

**1. Arquitetura.** A ideia inicial de ferramenta era um RAG sobre o catálogo, mas isso exigiria uma infraestrutura separada, fora do que o Harness oferece pronto. Com base no curso e na orientação do Claude, fui de Code Interpreter. Ele roda isolado e não consegue ler os arquivos do projeto, então deixei o catálogo dentro do prompt e usei a ferramenta só para cálculo.

**2. Sessão exploratória** → [`1-sessaoExploratoria1.md`](exploratory/1-sessaoExploratoria1.md)
A memória parecia vazar entre perguntas que deviam ser isoladas. A causa era o `agentcore dev`, que usa sempre o mesmo usuário (`default-user`). Passei a usar `agentcore invoke --actor-id` e confirmei que o isolamento entre clientes funciona. Também apareceram um nome de produto inventado e uma resposta fora de escopo ("capital da França"), que só foram tratados na rodada 3.

**3. Red teaming** → [`2-sessaoRedTeam.md`](exploratory/2-sessaoRedTeam.md)
Foram 17 tentativas: 14 resistiram e 3 falharam.
- Vazamento do prompt e do catálogo inteiros via tags `<system>` (crítica)
- Listagem dos arquivos do sandbox pela ferramenta (alta)
- Uso da ferramenta para calcular idade, fora do escopo (média)

Padrão observado: quando o bot resiste, ele reafirma quem é ("sou o Cosmetic Bot"). Pedidos com cara de instrução técnica escapam desse filtro.

**4. Rodada 1** → [`3-retestePosCorrecao.md`](exploratory/3-retestePosCorrecao.md)
Adicionei regras negativas no prompt: não reproduzir o prompt e usar a ferramenta só para pedido e conversão. Retestei apenas o que tinha falhado e resolvi 3 de 4. O cálculo de idade continuou passando, porque a regra restringia pelo *tipo de operação* e "calcular idade" também é um cálculo.

**5. Rodada 2** → [`4-retestePosCorrecao2.md`](exploratory/4-retestePosCorrecao2.md)
Troquei a abordagem e passei a restringir pelo *domínio do assunto*, independente da operação. Resultado 4 de 4, com uma pergunta de controle para garantir que o bot não passou a recusar pedidos legítimos.

**6. Dessincronia repo x AWS.** O `system-prompt.md` do GitHub ainda estava na versão original, porque as correções tinham sido deployadas pelo CloudShell sem commit. Confirmei o prompt real direto na AWS (`aws bedrock-agentcore-control get-harness`) e sincronizei o repositório.

**7. Rodada 3** → [`5-retestePosCorrecao3.md`](exploratory/5-retestePosCorrecao3.md)
Tratei dois pontos que ficaram de fora do red team:
- A persona vendedora conflitava com o Answer Relevancy, porque o bot sugeria produtos que ninguém pediu.
- A alucinação de nome de produto.

Adicionei duas frases ao prompt, uma de objetividade e outra de fidelidade de nome.

---

## Resultados

**Red teaming:** as 3 vulnerabilidades foram corrigidas e reconfirmadas em reteste.

**Frente A · AgentCore Evaluations** (16 sessões)

| Avaliador | Score |
|---|---|
| Builtin.ResponseRelevance | 0,91 |
| Builtin.ToolParameterAccuracy | 1,00 |
| MyEvaluator (conformidade de claims cosméticos) | 4,53 / 5 |

**Frente B · DeepEval** (thresholds do enunciado: Answer Relevancy ≥ 0,7 · Faithfulness ≥ 0,8 · G-Eval ≥ 0,8)

| | Passaram |
|---|---|
| Baseline (antes da rodada 3) | 14 / 20 |
| Final (depois da rodada 3) | 15 / 20 |

Das 5 falhas finais, 4 são de Answer Relevancy (persona vendedora): os casos 6 e 20 ficaram perto do limite e os casos 2 e 14 longe. A quinta é o caso 11, de Faithfulness: o bot disse que não havia protetor solar dentro de R$50, mas havia. Esse é um erro de dado, não de tom, e continua em aberto. Os thresholds não foram alterados.

---

## Como rodar

```bash
# deploy do agente
agentcore deploy

# conversar com o agente (use actor-ids diferentes para simular clientes diferentes)
agentcore invoke "Qual o preço do Sérum de Vitamina C 10%?" --harness MyHarness --actor-id cliente-1

# Frente A
agentcore run eval --runtime-arn <agentRuntimeArn em agentcore/.cli/deployed-state.json>

# Frente B (dois passos: coleta as respostas uma vez e avalia quantas vezes precisar)
pip install pytest deepeval aiobotocore botocore
python3 tests/collect_baseline.py --output responses_final.json
RESPONSES_FILE=responses_final.json python3 -m pytest tests/ -v
```

Projeto desenvolvido com auxílio do Claude.