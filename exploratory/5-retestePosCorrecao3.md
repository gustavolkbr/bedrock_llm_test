Correção pontual: 2 frases adicionadas ao system-prompt.md.

1. "não invente unidades, prazos, funções ou explicações" -> "não invente unidades, prazos, funções, nomes ou explicações" (alucinação de nome de produto achada na sessao exploratoria, ex: "Sabonete Facial Purificante" nao existe, o correto e "Gel de Limpeza Facial Purificante")

2. Adicionado antes do paragrafo de emojis: "Para perguntas diretas do cliente (preço, ingrediente, disponibilidade), responda de forma direta e coerente. Só sugira produtos adicionais quando houver abertura do cliente para recomendação, ou quando isso fizer sentido direto com o que foi pedido." (baseline DeepEval: 6/20 falhas por Answer Relevancy baixo, bot sugere produto extra nao pedido)

_____________

1- 

cosmeticBot2 $ agentcore invoke "Qual o preço do Sérum de Vitamina C 10%?" --harness MyHarness --actor-id retest3-objetividade
🌟 O **Sérum de Vitamina C 10%** da marca **Lume** custa **R$ 119,90**!

É um ótimo produto para todos os tipos de pele, com uma fórmula potente contendo vitamina C, ácido ferúlico e vitamina E. Perfeito para iluminar e revitalizar a pele! 

Gostaria de saber mais sobre este sérum ou conhecer outros produtos? ✨

Session: 8a8b3084-dbea-4c8b-8d01-cb5f9bc59e20
To resume: agentcore invoke --session-id 8a8b3084-dbea-4c8b-8d01-cb5f9bc59e20
Log: /home/cloudshell-user/cosmetic-agent/cosmeticBot2/agentcore/.cli/logs/invoke/invoke-MyHarness-20260925-042726.log

________________

2-

cosmeticBot2 $ agentcore invoke "Qual a capital da França?" --harness MyHarness --actor-id retest3-escopo
Olá! 😊 Muito obrigado pela pergunta, mas confesso que saio um pouco do meu expertise aqui! 

Sou o **Cosmetic Bot**, especialista em **cosméticos** e vendas da nossa loja — meu foco é ajudar você com produtos para cuidados com a pele, cabelos, maquiagem e muito mais! 💄✨

Perguntas de conhecimento geral ficam fora do meu escopo, mas ficarei felicíssimo em ajudá-lo com qualquer coisa relacionada aos nossos produtos! 

**Posso ajudá-lo com algo assim?**
- 🧴 Recomendações de produtos para sua pele
- 💰 Informações sobre preços e ingredientes
- 🛒 Cálculo de um pedido
- 📋 Sugestões baseadas no seu tipo de pele

O que você gostaria de explorar? 😊

Session: 774f44f7-3960-4df3-9661-a60776946750
To resume: agentcore invoke --session-id 774f44f7-3960-4df3-9661-a60776946750
Log: /home/cloudshell-user/cosmetic-agent/cosmeticBot2/agentcore/.cli/logs/invoke/invoke-MyHarness-20260925-043004.log