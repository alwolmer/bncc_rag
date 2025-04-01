from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnableMap, RunnablePassthrough
from langchain_core.runnables import RunnableBranch
from langchain_core.runnables import chain
from langchain_core.messages import HumanMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

import streamlit as st
from vectorstore.loader import load_llm

llm = load_llm()


# # --- Classes de avaliação ---
# class AvaliacaoEstrutura(BaseModel):
#     objetivos: str
#     conteudos: str
#     metodologia: str
#     avaliacao: str
#     recursos_e_materiais: str
#     tempo_e_sequencia: str
#     outros_elementos_relevantes: str

# class AvaliacaoFinal(BaseModel):
#     codigos_bncc: List[str]
#     avaliacao_estrutura: AvaliacaoEstrutura
#     avaliacao_estilo: str
#     avaliacao_conteudo: str

class SubtopicoEstrutura(BaseModel):
    presente: bool = Field(..., description="Se o sub-tópico está presente ou não no plano")
    adequado: bool = Field(..., description="Se o sub-tópico está adequado ou não no plano")
    identificacao: Optional[str] = Field(..., description="Identificação do que foi encontrado no plano acerca do sub-tópico")
    sugestao_melhoria: Optional[str] = Field(None, description="Sugestão de melhoria, se aplicável")

class AvaliacaoPlano(BaseModel):
    codigos_bncc: List[str] = Field(..., description="Códigos da BNCC selecionados")
    objetivos: SubtopicoEstrutura = Field(..., description="Avaliação dos objetivos")
    conteudos: SubtopicoEstrutura = Field(..., description="Avaliação dos conteúdos")
    metodologia: SubtopicoEstrutura = Field(..., description="Avaliação da metodologia")
    avaliacao: SubtopicoEstrutura = Field(..., description="Avaliação da avaliação")
    recursos: SubtopicoEstrutura = Field(..., description="Avaliação dos recursos")
    materiais: SubtopicoEstrutura = Field(..., description="Avaliação dos materiais")
    tempo: SubtopicoEstrutura = Field(..., description="Avaliação do tempo")

avaliacao_parser = PydanticOutputParser(pydantic_object=AvaliacaoPlano)

# --- Prompt detalhado para avaliação ---
avaliar_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um especialista em currículos da educação básica brasileira. Você analisa planos de aula para avaliar se atendem a determinados requisitos, especialmente em relação a critérios estruturais fundamentais e coerência com a Base Nacional Comum Curricular. Você jamais dá respostas para além dos formatos explicitamente definidos em cada instrução."),
    ("human", """Plano de aula:
{plano}

Habilidades da BNCC (selecionadas por similaridade):
{habilidades_bncc}

Etapa de ensino: {etapa}
Componente(s) curricular(es): {componentes}
Ano: {ano}

Com base nas informações acima, faça uma avaliação detalhada do plano de aula e responda aos seguintes pontos:
     
---

### 1. **Códigos da BNCC**:
Selecione entre uma e três habilidades da BNCC que melhor se encaixem no plano, considerando a pertinência das habilidades respectivas. 
- Não invente códigos nem atribua códigos incorretos. 
- Use **apenas os códigos fornecidos na listagem acima**.

---

### 2. **Avaliação da Estrutura**

Avalie a estrutura do plano de aula considerando os sete itens listados abaixo. Para cada item, responda aos seguintes aspectos:

- **i. O item está presente no plano?** (booleano)
- **ii. O que foi apresentado está adequado?** (booleano)
    - Só marque positivamente se o item foi identificado (explícita ou implicitamente) **e** não houver sugestões de melhoria.
    - Se houver **qualquer sugestão de melhoria**, a resposta deve ser negativa.
    - Para os itens **não obrigatórios** ("Recursos" e "Materiais"), você pode marcar positivo mesmo que estejam ausentes, **desde que sua ausência não comprometa o plano**.
    - Para os demais itens, **a ausência torna automaticamente inadequada**, com marcação negativa.
- **iii. O que foi identificado?** (descreva de forma concisa e objetiva; deixe em branco se não foi identificado)
- **iv. Sugestões de melhoria?** 
     - Seja conciso e objetivo.
     - Dê sugestões acionáveis, e nunca faça comentários genéricos como "é importante definir isso para um bom andamento da aula", a relevância de cada um dos pontos abordados já está dada e não precisa ser justificada.
     - Faça sugestões específicas se o contexto permitir (ex: em um plano que fale sobre Grécia Antiga, a sugestão para pode ser "compreender a estrutura social da pólis grega").
     - Se o contexto (texto do plano e habilidades selecionadas) não permitirem inferir o que está ausente, indique que o usuário precisará decidir quanto a isso ou trazer mais contexto.
     - Só deixa a sugestão em branco se o item estiver plenamente adequado.

---

#### 2.1. **Objetivos**

Este item se refere às intenções educativas do plano: o que se espera que os alunos desenvolvam, compreendam ou consigam realizar ao final da aula. Sugestões do objetivo para a aula podem ser encontradas nas habilidades da BNCC. 

**Exemplos adequados:**
- "Reconhecer e utilizar figuras de linguagem em textos poéticos."
- "Estimular o respeito e a escuta ativa nas apresentações orais."

**Exemplos inadequados:**
- "Leitura de um poema." (isso é uma atividade, não um objetivo)
- Ausência total de formulação de objetivos.

---

#### 2.2. **Conteúdos**

Conteúdos são os saberes mobilizados ou construídos ao longo da aula. Podem ser conceituais (saberes teóricos), procedimentais (saberes práticos) ou atitudinais (valores e posturas). Sugestões do conteúdo para a aula podem ser encontradas nas habilidades da BNCC.

**Exemplos adequados:**
- Conceitual: "Noção de escala cartográfica."
- Procedimental: "Construção de um gráfico de barras."
- Atitudinal: "Cooperação em trabalho em grupo."

**Exemplos inadequados:**
- "Atividade interdisciplinar." (vago)
- "Diversos conteúdos." (não especificado)

---

#### 2.3. **Metodologia**

A metodologia descreve as estratégias de ensino e aprendizagem: o que será feito, como será feito, em que ordem, e qual o papel do professor e dos alunos. Não confundir com o conteúdo que a aula pretende abordar.

**Exemplos adequados:**
- "O professor introduz o tema com uma pergunta-problema. Os alunos debatem em grupos e produzem cartazes com suas propostas."

**Exemplos inadequados:**
- "Fazer a atividade do livro." (sem mediação docente ou participação clara dos alunos)
- Apenas listagem de páginas ou conteúdos sem descrição da dinâmica.

---

#### 2.4. **Avaliação**

Diz respeito a como o professor pretende acompanhar, registrar e interpretar o progresso dos alunos. Deve incluir pelo menos um item entre: instrumentos, critérios e formas de feedback.

**Exemplos adequados:**
- "Autoavaliação ao final da aula com critérios definidos em conjunto com os alunos."
- "Análise das produções escritas com base em clareza, coesão e adequação temática."
- "Observação da participação dos alunos nas discussões."

**Exemplos inadequados:**
- "Avaliativo." (sem mais informações)
- Avaliação ausente ou genérica.

---

#### 2.5. **Recursos** *(opcional)*

Recursos são ferramentas tecnológicas, visuais ou de apoio que não são consumíveis. Exemplos: livros didáticos, vídeos, sistema de som, slides, instrumentos de laboratório, etc. Não confundir com materiais, que são consumíveis.

**Exemplos adequados:**
- "Slides com exemplos de paralelismo."
- "Vídeo sobre o ciclo da água."

**Exemplo de ausência justificada:**
- Aula expositiva com quadro e fala do professor, sem necessidade de recursos adicionais.

**Exemplos inadequados:**
- "Materiais diversos." (vago)
- Uso de recursos implícitos (ex: "exibição de trecho de filme", "ouvir canção tal" sem mencionar os recursos audiovisuais necessários para tal).

---

#### 2.6. **Materiais** *(opcional)*

Materiais são itens físicos utilizados ou manipulados pelos alunos, normalmente consumíveis ou concretos. Ex: cartolina, tinta, argila, reagentes, etc. Não confundir com recursos.

**Exemplos adequados:**
- "Cartolina e pincéis para produção de cartazes."
- "Argila para modelar o relevo estudado."

**Exemplo de ausência justificada:**
- Aula centrada em leitura, debate e registro no caderno.

**Exemplos inadequados:**
- Uso de materiais implícitos (ex: "desenho", mas sem mencionar papel ou lápis).

---

#### 2.7. **Tempo**

Envolve a duração total da aula e/ou o tempo estimado para cada etapa. Também se refere à ordem clara das atividades propostas.

**Exemplos adequados:**
- "Aula de 50 minutos: introdução (10'), atividade em grupo (25'), síntese coletiva (15')."
- "Sequência: leitura – discussão – produção textual."

**Exemplos inadequados:**
- Atividades listadas sem ordem ou referência temporal.
- Apenas menção genérica à "duração da aula".
- Ausência total de referência ao tempo.1

---



Retorne exclusivamente no seguinte formato JSON:

{format_instructions}""")
])

# # --- Função auxiliar para formatar habilidades ---
# def formatar_habilidades_bncc(habs: List[dict]) -> List[dict]:
#     return "\n".join(f"{h['Código']} - {h['Habilidade']}" for h in habs if 'Código' in h and 'Habilidade' in h)

# --- Função de avaliação final ---
def avaliar_plano_avaliacao_final_fn(state: dict) -> dict:
    avaliar_chain = (
        {
            "plano": lambda x: x["plano"],
            "habilidades_bncc": lambda x: x["habilidades_bncc"],
            "componentes": lambda x: x["componentes"],
            "ano": lambda x: x["ano"],
            "etapa": lambda x: x["etapa"],
            "format_instructions": lambda _: avaliacao_parser.get_format_instructions()
        }
        | avaliar_prompt
        | llm
        | avaliacao_parser
    )
    parsed = avaliar_chain.invoke(state)

    parsed = {
        **parsed.model_dump()
    }

    state["habilidades_bncc"] = list(set([f"{hab['Código']} - {hab['Habilidade']}" for hab in state["habilidades_bncc"] if hab["Código"] in parsed['codigos_bncc']]))

    return {**state, "avaliacao_estrutura": parsed}

avaliar_plano_chain = RunnableLambda(avaliar_plano_avaliacao_final_fn)

# Em uma LangGraph, você aplicaria `buscar_habilidades_relevantes(retriever)` como nó inicial,
# seguido por `full_componente_ano_extractor`, e então um roteamento com base em `errors`.

#      1. Estrutura:
# Verifique se o plano apresenta todos os elementos fundamentais de um plano de aula bem elaborado, condizente com a etapa de ensino (Educação Infantil, Ensino Fundamental ou Ensino Médio) e o componente curricular indicado. Analise cada um dos seguintes aspectos:

#     1. **Objetivos**
#     2. **Conteúdos**
#     3. **Metodologia**
#     4. **Avaliação**
#     5. **Recursos e materiais**
#     6. **Tempo e sequência**
#     7. **Outros elementos relevantes**

#     Para **cada um dos itens acima**, indique:
#       - O que o modelo identificou no plano que corresponde àquele item.
#       - Caso identifique omissões ou pontos fracos, sugira melhorias objetivas.
#       - Caso o item esteja plenamente atendido, apenas escreva `"Adequado"`.

# Para cada item acima, descreva o que foi identificado e, se necessário, proponha melhorias. Se estiver plenamente adequado, escreva apenas "Adequado".

# 2. Estilo:
# A linguagem está clara e de acordo com a norma culta do português brasileiro? Há erros de conjugação, concordância, regência ou expressões que prejudicam a compreensão? Se houver trechos problemáticos, aponte-os explicitamente com sugestões de correção. Não faça comentários genéricos sobre a norma culta Se estiver plenamente adequado, escreva apenas "Adequado".

# 3. Conteúdo e abordagem:
# As atividades e objetivos estão alinhados com as habilidades listadas? Proponha ajustes objetivos, se necessário. Se estiver plenamente adequado, escreva apenas "Adequado".


### 2. **Avaliação da Estrutura**:
     
    # - Avalie a estrutura do plano de aula, considerando os seguintes aspectos:
    #  1. **Objetivos**: extrair objetivos gerais e específicos, objetivos de aprendizagem, objetivos de desenvolvimento.
    #  2. **Conteúdos**: extrair conteúdos conceituais, procedimentais e atitudinais.
    #  3. **Metodologia**: extrair descrição das atividades e dinâmicas propostas, considerando a ainda como o professor irá conduzir a aula e como os alunos irão participar.
    #  4. **Avaliação**: descrição da avaliação, critérios de avaliação e/ou instrumentos de avaliação.
    #  5. **Recursos**: livro didático, apostila, fichas, slides, vídeos, sistemas de som, etc. Não é necessário constar em todos os planos.
    #  6. **Materiais**: cartolina, tinta, giz, cola, argila, fotos, etc. Não é necessário constar em todos os planos.
    #  7. **Tempo**: tempo total da aula, tempo para cada atividade proposta, ordem das atividades.

    #  Para cada um dos itens acima, indique:
    #     i. Se o plano contém algo que corresponda a esse item, explicitamente ou implicitamente (uma resposta de sim ou não).
    #     ii. Se o que você identificou foi adequado (uma resposta de sim ou não).
    #         - Só responda sim se o item foi identificado (explícita ou implicitamente) e não houver sugestões de melhoria para esse item.
    #         - Se houver qualquer sugestão de melhoria (mesmo pequena), a resposta deve ser “não”.
    #         - Para os itens marcados como não obrigatórios (“Recursos” e “Materiais”), é permitido responder sim mesmo que estejam ausentes, desde que você julgue que não fazem falta neste plano específico.
    #         - Para os demais itens, se estiverem ausentes, a resposta deve ser “não”.
    #     iii. O que você identificou no plano que corresponde àquele item. Explicite o que estiver implícito, mas seja sucinto e enumerativo, não faça comentários longos ou genéricos. Só descreva o que foi identificado, não faça sugestões de melhorias. Não escreva nada aqui caso o item não tenha sido identificado.
    #     iv. Caso identifique omissões, pontos fracos, confusão ou ambiguidade, sugira melhorias objetivas. Seja sucinto e enumerativo, não faça comentários longos ou genéricos. Não descreva novamente o que foi identificado, apenas faça sugestões de melhorias. Não escreva nada aqui caso o item esteja plenamente adequado.