import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# ── Configuração ───────────────────────────────────────────────────────────────
API_URL = "http://localhost:8080"

st.set_page_config(
    page_title="LAPIA – Coleta de Dados Clínicos",
    page_icon="🧠",
    layout="centered",
)

# ══════════════════════════════════════════════════════════════════════════════
# DEFINIÇÃO DAS ESCALAS
# ══════════════════════════════════════════════════════════════════════════════

ESCALAS = {
    "SNAP-IV": {
        "descricao": "Escala de Avaliação de TDAH (26 itens) — SNAP-IV",
        "instrucoes": "Indique a frequência de cada comportamento nas últimas 2 semanas.",
        "opcoes": {"Nem um pouco": 0, "Só um pouco": 1, "Bastante": 2, "Demais": 3},
        "secoes": {
            "Desatenção (Itens 1–9)": [
                "Não consegue prestar muita atenção a detalhes ou comete erros por descuido nos trabalhos da escola ou tarefas",
                "Tem dificuldade de manter a atenção em tarefas ou atividades de lazer",
                "Parece não estar ouvindo quando se fala diretamente com ele",
                "Não segue instruções até o fim e não termina deveres de escola, tarefas ou obrigações",
                "Tem dificuldade para organizar tarefas e atividades",
                "Evita, não gosta ou se envolve contra a vontade em tarefas que exigem esforço mental prolongado",
                "Perde coisas necessárias para atividades (p. ex: brinquedos, deveres da escola, lápis ou livros)",
                "Distrai-se com estímulos externos",
                "É esquecido em atividades do dia-a-dia",
            ],
            "Hiperatividade/Impulsividade (Itens 10–18)": [
                "Mexe com as mãos ou pés ou se remexe na cadeira",
                "Sai do lugar na sala de aula ou em outras situações em que se espera que fique sentado",
                "Corre de um lado para outro ou sobe demais nas coisas em situações em que isto é inapropriado",
                "Tem dificuldade em brincar ou envolver-se em atividades de lazer de forma calma",
                "Não pára ou freqüentemente está a 'mil por hora'",
                "Fala em excesso",
                "Responde as perguntas de forma precipitada antes delas terem sido terminadas",
                "Tem dificuldade de esperar sua vez",
                "Interrompe os outros ou se intromete (por exemplo: intromete-se nas conversas, jogos, etc.)",
            ],
            "Transtorno Desafiador Opositor (Itens 19–26)": [
                "Tem acessos de raiva ou crises de birra",
                "Discute com adultos",
                "Desafia ou recusa-se a obedecer às regras dos adultos",
                "Faz coisas que incomodam os outros de propósito",
                "Culpa os outros por seus próprios erros ou mau comportamento",
                "É irritável ou fica facilmente aborrecido por outras pessoas",
                "Fica irritado e ressentido",
                "É rancoroso ou vingativo",
            ],
        },
        "calculo": "snap_iv",
    },
    "SDQ": {
        "descricao": "Questionário de Capacidades e Dificuldades (SDQ) — 25 itens",
        "instrucoes": "Para cada item, marque o que melhor descreve a criança nos últimos 6 meses.",
        "opcoes": {"Falso": 0, "Mais ou menos verdadeiro": 1, "Verdadeiro": 2},
        "secoes": {
            "Itens SDQ": [
                "Tem consideração pelos sentimentos de outras pessoas",
                "Não consegue parar sentado quando tem que fazer a lição ou comer; mexe-se muito",
                "Muitas vezes se queixa de dor de cabeça, dor de barriga ou enjôo",
                "Tem boa vontade em compartilhar doces, brinquedos, lápis com outras crianças",
                "Frequentemente tem acessos de raiva ou crises de birra",
                "É solitário, prefere brincar sozinho",
                "Geralmente é obediente e faz normalmente o que os adultos lhe pedem",
                "Tem muitas preocupações, muitas vezes parece preocupado com tudo",
                "Tenta ser atencioso se alguém parece magoado, aflito ou se sentindo mal",
                "Está sempre agitado, balançando as pernas ou mexendo as mãos",
                "Tem pelo menos um bom amigo ou amiga",
                "Frequentemente briga com outras crianças ou as amedronta",
                "Frequentemente parece triste, desanimado ou choroso",
                "Em geral, é querido por outras crianças",
                "Facilmente perde a concentração",
                "Fica inseguro quando tem que fazer alguma coisa pela primeira vez, facilmente perde a confiança em si mesmo",
                "É gentil com crianças mais novas",
                "Frequentemente engana ou mente",
                "Outras crianças 'pegam no pé' ou atormentam-no",
                "Frequentemente se oferece para ajudar outras pessoas (pais, professores, outras crianças)",
                "Pensa nas coisas antes de fazê-las",
                "Rouba coisas de casa, da escola ou de outros lugares",
                "Se dá melhor com adultos do que com outras crianças",
                "Tem muitos medos, assusta-se facilmente",
                "Completa as tarefas que começa, tem boa concentração",
            ]
        },
        "calculo": "sdq",
    },
    "PGSI": {
        "descricao": "Problem Gambling Severity Index (PGSI) — 9 itens",
        "instrucoes": "Pensando nos últimos 12 meses, com que frequência...",
        "opcoes": {"Nunca": 0, "Às vezes": 1, "Na maioria das vezes": 2, "Quase sempre": 3},
        "secoes": {
            "Itens PGSI": [
                "Você apostou mais do que realmente poderia perder?",
                "Você precisou apostar quantias cada vez maiores de dinheiro para ter a mesma sensação de prazer?",
                "Depois de ter apostado, você retorna outro dia para tentar recuperar o dinheiro perdido?",
                "Você pediu dinheiro emprestado ou vendeu alguma coisa para conseguir dinheiro para apostar?",
                "Você achou que poderia ter algum problema com apostas?",
                "Apostar já lhe causou algum problema de saúde, como estresse ou ansiedade?",
                "As pessoas já lhe criticaram por apostar, ou disseram que você tinha problemas com apostar?",
                "As suas apostas já causaram algum problema financeiro para você ou sua família?",
                "Você já se sentiu culpado(a) pela maneira como você aposta ou pelo que acontece quando você aposta?",
            ]
        },
        "calculo": "pgsi",
    },
    "CMRS-P": {
        "descricao": "Escala de Classificação de Mania Infantil — Versão para Pais (CMRS-P) — 21 itens",
        "instrucoes": "As questões abaixo se referem ao humor e comportamento do/a seu/sua filho/a no último mês.",
        "opcoes": {"Raro ou nunca": 0, "Às vezes": 1, "Frequentemente": 2, "Muito frequentemente": 3},
        "secoes": {
            "Itens CMRS-P": [
                "Seu/sua filho/a teve momentos que se sentiu muito feliz por horas ou dias seguidos, extremamente animado/a e empolgado/a (alegria exagerada)",
                "Seu/sua filho/a sentiu-se irritado/a, ranzinza, rabugento/a ou furioso/a por horas ou dias seguidos",
                "Seu/sua filho/a pensou que poderia ser ou fazer qualquer coisa (ex: ser um grande líder, o melhor cantor, milionário), fora de brincadeira",
                "Seu/sua filho/a teve problemas por acreditar que tinha habilidades que não tinha, ou superpoderes",
                "Seu/sua filho/a precisou dormir menos que o normal, não se sentindo cansado/a no dia seguinte",
                "Seu/sua filho/a teve momentos de muita energia",
                "Seu/sua filho/a teve momentos em que falava muito, ou muito alto, ou muito rápido",
                "Seu/sua filho/a teve momentos de pensamentos acelerados, parecendo que sua fala não conseguia acompanhar seus pensamentos",
                "Seu/sua filho/a falou tão rápido que pulava de um assunto para outro",
                "Seu/sua filho/a correu por aí fazendo coisas sem parar (estava 'a mil por hora')",
                "Seu/sua filho/a teve dificuldade para manter-se atento/a, sendo facilmente distraído/a",
                "Seu/sua filho/a fez muito mais coisas do que o normal, estava mais produtivo/a ou altamente criativo/a",
                "Seu/sua filho/a comportou-se de uma forma sexualmente inadequada",
                "Seu/sua filho/a falou ou agiu com estranhos de forma inadequada, sendo mais extrovertido/a do que o normal",
                "Seu/sua filho/a fez coisas incomuns que foram tolas ou arriscadas (ex: pulou de alturas, fez compras com dinheiro dos outros)",
                "Seu/sua filho/a teve ataques de fúria ou crises de birra intensas e prolongadas",
                "Seu/sua filho/a fez mais piadas ou brincadeiras do que o normal, riu alto demais ou agiu de maneira boba",
                "Seu/sua filho/a teve mudanças rápidas de humor",
                "Seu/sua filho/a teve algum pensamento estranho (bizarro) ou de desconfiança",
                "Seu/sua filho/a ouviu vozes ou barulhos que ninguém mais podia ouvir",
                "Seu/sua filho/a viu coisas que ninguém mais podia ver",
            ]
        },
        "calculo": "cmrs_p",
    },
    "CY-BOCS": {
        "descricao": "Escala Yale-Brown de Obsessões e Compulsões — versão para crianças (CY-BOCS) — 10 itens",
        "instrucoes": "Avalie a gravidade dos sintomas obsessivo-compulsivos nas últimas semanas (0 = nenhum, 4 = muito grave).",
        "opcoes": {"0 – Nenhum": 0, "1 – Leve": 1, "2 – Moderado": 2, "3 – Grave": 3, "4 – Muito grave": 4},
        "secoes": {
            "Obsessões": [
                "Tempo ocupado pelos pensamentos obsessivos",
                "Interferência provocada pelos pensamentos obsessivos",
                "Sofrimento relacionado aos pensamentos obsessivos",
                "Resistência às obsessões",
                "Grau de controle sobre os pensamentos obsessivos",
            ],
            "Compulsões": [
                "Tempo gasto com comportamentos compulsivos",
                "Interferência provocada pelos comportamentos compulsivos",
                "Sofrimento relacionado ao comportamento compulsivo",
                "Resistência às compulsões",
                "Grau de controle sobre o comportamento compulsivo",
            ],
        },
        "calculo": "cybocs",
    },
    "TOD": {
        "descricao": "Gravidade do Transtorno Opositor Desafiador — Avaliada pelo Clínico (TOD)",
        "instrucoes": "Com base nas informações disponíveis e julgamento clínico, classifique a gravidade dos sintomas opositores desafiadores nos últimos 7 dias.",
        "opcoes": {
            "0 – Nenhum (sem sintomas)": 0,
            "1 – Leve (sintomas em apenas 1 ambiente)": 1,
            "2 – Moderado (sintomas em pelo menos 2 ambientes)": 2,
            "3 – Grave (sintomas em 3 ou mais ambientes)": 3,
        },
        "secoes": {
            "Avaliação Global": [
                "Nível de gravidade dos problemas opositores desafiadores presentes para este indivíduo",
            ]
        },
        "calculo": "tod",
    },
    "HQ-25": {
        "descricao": "Questionário Hikikomori (HQ-25) — 25 itens",
        "instrucoes": "Nos últimos 6 meses, em que medida as afirmações abaixo descrevem você?",
        "opcoes": {
            "Discordo totalmente": 0,
            "Discordo": 1,
            "Nem concordo nem discordo": 2,
            "Concordo": 3,
            "Concordo totalmente": 4,
        },
        "itens_invertidos": [4, 7, 10, 15, 21, 25],  # índices 1-based
        "secoes": {
            "Itens HQ-25": [
                "Eu evito outras pessoas.",
                "Passo a maior parte do meu tempo em casa.",
                "Não há realmente ninguém com quem eu possa conversar sobre assuntos importantes.",
                "Gosto de conhecer pessoas novas. †",
                "Eu me isolo no meu quarto.",
                "As pessoas me incomodam.",
                "Existem pessoas na minha vida que tentam me compreender. †",
                "Sinto-me desconfortável quando estou perto de outras pessoas.",
                "Passo a maior parte do meu tempo sozinho(a).",
                "Consigo compartilhar meus pensamentos pessoais com várias pessoas. †",
                "Não gosto que outras pessoas me vejam.",
                "Raramente encontro pessoas pessoalmente.",
                "É difícil para mim participar de grupos.",
                "Há poucas pessoas com quem posso discutir assuntos importantes.",
                "Gosto de estar em situações sociais. †",
                "Não sigo as regras e os valores da sociedade.",
                "Não existe ninguém realmente importante na minha vida.",
                "Evito conversar com outras pessoas.",
                "Tenho pouco contato com outras pessoas (conversando, escrevendo ou de outras formas).",
                "Prefiro muito mais ficar sozinho(a) do que estar com outras pessoas.",
                "Tenho alguém em quem posso confiar meus problemas. †",
                "Raramente passo tempo sozinho(a).",
                "Não gosto de interações sociais.",
                "Passo muito pouco tempo interagindo com outras pessoas.",
                "Prefiro muito estar cercado(a) por outras pessoas. †",
            ]
        },
        "calculo": "hq25",
    },
    "RLI": {
        "descricao": "Risky Loot Box Index (RLI) — 5 itens",
        "instrucoes": "Indique seu grau de concordância com cada afirmação.",
        "opcoes": {
            "Discordo totalmente": 1,
            "Discordo um pouco": 2,
            "Não concordo nem discordo": 3,
            "Concordo um pouco": 4,
            "Concordo totalmente": 5,
        },
        "secoes": {
            "Itens RLI": [
                "A emoção de abrir loot boxes me encorajou a comprar mais.",
                "Eu frequentemente jogo por mais tempo do que pretendia para poder ganhar loot boxes.",
                "Deixei de lado outras atividades, trabalho ou tarefas para poder ganhar ou comprar mais loot boxes.",
                "Depois de abrir uma loot box, eu geralmente sinto muita vontade de abrir outra.",
                "Comprei mais loot boxes depois de não ter conseguido ganhar itens valiosos.",
            ]
        },
        "calculo": "rli",
    },
    "IGDT-10": {
        "descricao": "Internet Gaming Disorder Test (IGDT-10) — 10 itens",
        "instrucoes": (
            "Por favor, leia as frases abaixo sobre jogos de videogame. O questionário se refere a jogos "
            "tanto online como offline, jogados em qualquer plataforma. Por favor, assinale na escala de "
            "0 a 2 (0 = Nunca / 1 = Às vezes / 2 = Frequentemente) em que intensidade e frequência as "
            "frases abaixo se aplicaram a você ao longo dos últimos 12 meses."
        ),
        "opcoes": {"Nunca (0)": 0, "Às vezes (1)": 1, "Frequentemente (2)": 2},
        "secoes": {
            "Itens IGDT-10": [
                "Quando você não estava jogando, com que frequência imaginou que estava jogando, ficou pensando em jogos anteriores ou em como seria o próximo jogo?",
                "Com que frequência você se sentia inquieto, irritado, ansioso e/ou triste quando não pôde jogar ou quando jogou menos do que o habitual?",
                "Você sentiu necessidade de jogar com maior frequência ou jogou por mais tempo para ter a sensação de que tinha jogado o suficiente?",
                "Você tentou diminuir o tempo que passa jogando e não conseguiu?",
                "Você ficou jogando ao invés de encontrar seus amigos ou participar de atividades de lazer e passatempos que você costumava gostar?",
                "Você já jogou muito apesar de consequências negativas (por exemplo: dormir menos, não conseguir ir bem na escola ou no trabalho, discutir com familiares ou amigos e/ou negligenciar tarefas importantes)?",
                "Você já tentou esconder de sua família, amigos ou outras pessoas importantes para você o quanto você estava jogando, ou mentiu para eles sobre isso?",
                "Você já jogou para aliviar um sentimento negativo (por exemplo: desamparo, culpa ou ansiedade)?",
                "Você já arriscou ou perdeu algum relacionamento importante/significativo por causa do jogo?",
                "Você teve prejuízo no seu desempenho na escola ou no trabalho por causa do jogo?",
            ]
        },
        "calculo": "igdt10",
    },
    "SCARED": {
        "descricao": "Escala de Transtornos Relacionados à Ansiedade Infantil (SCARED) — 41 itens — Versão para crianças",
        "instrucoes": (
            "Abaixo há uma lista de afirmativas que descrevem como as pessoas se sentem. "
            "Leia cada uma delas e decida se ela é 'não verdadeira', 'às vezes verdadeira' "
            "ou 'verdadeira' em relação a você. Marque a resposta que parece descrever você "
            "nos últimos 3 meses."
        ),
        "opcoes": {"Não verdadeiro (0)": 0, "Às vezes verdadeiro (1)": 1, "Verdadeiro (2)": 2},
        "secoes": {
            "Itens 1–17": [
                "Quando estou com medo é difícil respirar.",
                "Tenho dor de cabeça quando estou na escola.",
                "Eu não gosto de estar com pessoas que não conheço direito.",
                "Fico com medo se durmo fora de casa.",
                "Preocupo-me em relação aos outros gostarem de mim.",
                "Quando estou assustado/a parece que vou desmaiar.",
                "Eu sou nervoso/a.",
                "Sigo meu pai ou minha mãe aonde quer que eles vão.",
                "As pessoas me dizem que eu pareço nervoso/a.",
                "Sinto-me nervoso/a com pessoas que não conheço direito.",
                "Tenho dor de estômago na escola.",
                "Quando me assusto, parece que vou enlouquecer.",
                "Preocupo-me em ter que dormir sozinho/a.",
                "Preocupo-me em ser tão bom/a quanto as outras crianças.",
                "Quando me assusto, parece que as coisas não são reais.",
                "Tenho pesadelos de que algo ruim aconteça com meus pais.",
                "Preocupo-me sobre ir à escola.",
            ],
            "Itens 18–41": [
                "Quando me assusto, meu coração bate rápido.",
                "Fico tremuloso/a.",
                "Tenho pesadelos de que algo ruim possa me acontecer.",
                "Eu me preocupo sobre as coisas darem certo para mim.",
                "Quando me assusto, suo bastante.",
                "Eu vivo preocupado/a.",
                "Fico muito assustado/a sem motivo algum.",
                "Fico com medo de ficar em casa sozinho/a.",
                "Tenho dificuldade para falar com pessoas que não conheço.",
                "Quando me assusto, parece que vou sufocar.",
                "As pessoas me dizem que eu me preocupo demais.",
                "Não gosto de estar longe da família.",
                "Tenho medo de ter crises de ansiedade (ou de pânico).",
                "Preocupo-me que algo ruim possa acontecer com meus pais.",
                "Sinto-me tímido/a com pessoas que não conheço direito.",
                "Preocupo-me com o que vai acontecer no futuro.",
                "Quando fico assustado/a, parece que vou vomitar.",
                "Preocupo-me com quão bem faço as coisas.",
                "Tenho medo de ir à escola.",
                "Preocupo-me com coisas que já aconteceram.",
                "Quando me assusto, fico tonto.",
                "Fico nervoso/a quando estou com outras crianças ou adultos e tenho que fazer alguma coisa com eles me olhando (ex: falar, ler, jogar alguma coisa, praticar algum esporte).",
                "Fico nervoso/a quando vou a festas, bailes ou qualquer lugar onde vai haver pessoas que não conheço.",
                "Sou tímido/a.",
            ],
        },
        "calculo": "scared",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE CÁLCULO
# ══════════════════════════════════════════════════════════════════════════════

def calcular_resultado(escala_key, respostas_dict):
    """Retorna dict com scores e interpretação clínica."""
    vals = list(respostas_dict.values())
    total = sum(vals)
    resultado = {"score_total": total, "interpretacao": [], "subescalas": {}}

    if escala_key == "SNAP-IV":
        des = vals[:9]
        hip = vals[9:18]
        tdo = vals[18:26] if len(vals) > 18 else []
        media_des = sum(des) / 9
        media_hip = sum(hip) / 9
        pos_des = sum(1 for v in des if v >= 2)
        pos_hip = sum(1 for v in hip if v >= 2)
        resultado["subescalas"] = {
            "Média Desatenção": round(media_des, 2),
            "Média Hiperatividade": round(media_hip, 2),
            "Sintomas positivos Desatenção (≥Bastante)": pos_des,
            "Sintomas positivos Hiperatividade (≥Bastante)": pos_hip,
        }
        if tdo:
            media_tdo = sum(tdo) / 8
            pos_tdo = sum(1 for v in tdo if v >= 2)
            resultado["subescalas"]["Média TDO"] = round(media_tdo, 2)
            resultado["subescalas"]["Sintomas positivos TDO (≥Bastante)"] = pos_tdo
            if pos_tdo >= 4:
                resultado["interpretacao"].append("⚠️ TDO: rastreio positivo (≥4 itens significativos)")
        if pos_des >= 6:
            resultado["interpretacao"].append("⚠️ Desatenção: rastreio positivo (≥6 itens significativos)")
        if pos_hip >= 6:
            resultado["interpretacao"].append("⚠️ Hiperatividade: rastreio positivo (≥6 itens significativos)")
        if media_des >= 1.2:
            resultado["interpretacao"].append(f"📊 Média desatenção ({media_des:.2f}) ≥ ponto de corte parental (1,2)")
        if media_hip >= 1.4:
            resultado["interpretacao"].append(f"📊 Média hiperatividade ({media_hip:.2f}) ≥ ponto de corte parental (1,4)")

    elif escala_key == "SDQ":
        # Subescalas SDQ (itens 1-based, invertidos: 7,11,14,17,21,25)
        invertidos = {7, 11, 14, 17, 21, 25}
        v = {}
        for i, val in enumerate(vals, 1):
            v[i] = (2 - val) if i in invertidos else val
        sintomas_emocionais = sum(v[i] for i in [3, 8, 13, 16, 24])
        prob_conduta = sum(v[i] for i in [5, 7, 12, 18, 22])
        hiperativ = sum(v[i] for i in [2, 10, 15, 21, 25])
        prob_pares = sum(v[i] for i in [6, 11, 14, 19, 23])
        prosocial = sum(v[i] for i in [1, 4, 9, 17, 20])
        dificuldades = sintomas_emocionais + prob_conduta + hiperativ + prob_pares
        resultado["subescalas"] = {
            "Sintomas Emocionais (0–10)": sintomas_emocionais,
            "Problemas de Conduta (0–10)": prob_conduta,
            "Hiperatividade (0–10)": hiperativ,
            "Problemas com Pares (0–10)": prob_pares,
            "Pró-social (0–10)": prosocial,
            "Total Dificuldades (0–40)": dificuldades,
        }
        resultado["score_total"] = dificuldades
        if dificuldades >= 17:
            resultado["interpretacao"].append("⚠️ Total dificuldades: faixa anormal (≥17)")
        elif dificuldades >= 14:
            resultado["interpretacao"].append("🟡 Total dificuldades: faixa limítrofe (14–16)")
        else:
            resultado["interpretacao"].append("✅ Total dificuldades: faixa normal (≤13)")

    elif escala_key == "PGSI":
        if total == 0:
            resultado["interpretacao"].append("✅ Sem problemas com jogo")
        elif total <= 2:
            resultado["interpretacao"].append("🟡 Baixo risco (1–2)")
        elif total <= 7:
            resultado["interpretacao"].append("🟠 Risco moderado (3–7)")
        else:
            resultado["interpretacao"].append("🔴 Jogo problemático (≥8)")

    elif escala_key == "CMRS-P":
        resultado["interpretacao"].append(
            "⚠️ Rastreio positivo (≥20 pontos)" if total >= 20
            else "✅ Abaixo do ponto de corte (<20)"
        )

    elif escala_key == "CY-BOCS":
        obs = vals[:5]
        comp = vals[5:]
        sub_obs = sum(obs)
        sub_comp = sum(comp)
        resultado["subescalas"] = {
            "Subtotal Obsessões (0–20)": sub_obs,
            "Subtotal Compulsões (0–20)": sub_comp,
        }
        resultado["score_total"] = sub_obs + sub_comp
        t = resultado["score_total"]
        if t <= 7:
            resultado["interpretacao"].append("✅ Subcrínico (0–7)")
        elif t <= 15:
            resultado["interpretacao"].append("🟡 Leve (8–15)")
        elif t <= 23:
            resultado["interpretacao"].append("🟠 Moderado (16–23)")
        elif t <= 31:
            resultado["interpretacao"].append("🔴 Grave (24–31)")
        else:
            resultado["interpretacao"].append("🔴 Muito grave (32–40)")

    elif escala_key == "TOD":
        nivel = {0: "✅ Nenhum", 1: "🟡 Leve", 2: "🟠 Moderado", 3: "🔴 Grave"}
        resultado["interpretacao"].append(nivel.get(total, str(total)))

    elif escala_key == "HQ-25":
        resultado["interpretacao"].append(
            "⚠️ Rastreio positivo para hikikomori (≥42)" if total >= 42
            else f"✅ Abaixo do ponto de corte (<42) — score: {total}"
        )

    elif escala_key == "RLI":
        resultado["interpretacao"].append(
            f"Índice contínuo: {total}/25. Scores mais altos = maior acúmulo de comportamentos de risco com loot boxes. Não há ponto de corte diagnóstico."
        )

    elif escala_key == "IGDT-10":
        # Escala original: 0=Nunca, 1=Às vezes, 2=Frequentemente
        # Para o score DSM-5: apenas "Frequentemente" (2) conta como critério positivo (1 ponto)
        # Itens 9 e 10 referem-se ao mesmo critério — combinados valem no máximo 1 ponto
        criterios = [1 if v == 2 else 0 for v in vals[:8]]
        criterio_9_10 = 1 if (len(vals) >= 10 and (vals[8] == 2 or vals[9] == 2)) else 0
        score_efetivo = sum(criterios) + criterio_9_10
        resultado["score_total"] = score_efetivo
        resultado["subescalas"] = {"Score DSM-5 (0–9)": score_efetivo}
        resultado["interpretacao"].append(
            "⚠️ Caso clinicamente relevante de acordo com DSM-5 (≥5)"
            if score_efetivo >= 5
            else f"✅ Abaixo do ponto de corte (<5) — score: {score_efetivo}"
        )

    elif escala_key == "SCARED":
        # Subescalas conforme pontos de corte do instrumento
        # Pânico/Sintomas Somáticos: itens 1,6,9,12,15,18,19,22,24,27,30,34,38 (índices 0-based: 0,5,8,11,14,17,18,21,23,26,29,33,37)
        panico_idx     = [0, 5, 8, 11, 14, 17, 18, 21, 23, 26, 29, 33, 37]
        # Ansiedade Generalizada: itens 5,7,14,21,23,28,33,35,37 (índices 0-based: 4,6,13,20,22,27,32,34,36)
        tag_idx        = [4, 6, 13, 20, 22, 27, 32, 34, 36]
        # Ansiedade de Separação: itens 4,8,13,16,20,25,29,31 (índices 0-based: 3,7,12,15,19,24,28,30)
        sep_idx        = [3, 7, 12, 15, 19, 24, 28, 30]
        # Ansiedade Social: itens 3,10,26,32,39,40,41 (índices 0-based: 2,9,25,31,38,39,40)
        social_idx     = [2, 9, 25, 31, 38, 39, 40]
        # Evitação Escolar: itens 2,11,17,36 (índices 0-based: 1,10,16,35)
        escolar_idx    = [1, 10, 16, 35]

        def sub(indices):
            return sum(vals[i] for i in indices if i < len(vals))

        s_panico  = sub(panico_idx)
        s_tag     = sub(tag_idx)
        s_sep     = sub(sep_idx)
        s_social  = sub(social_idx)
        s_escolar = sub(escolar_idx)

        resultado["subescalas"] = {
            "Pânico/Sintomas Somáticos (corte ≥7)": s_panico,
            "Ansiedade Generalizada (corte ≥9)": s_tag,
            "Ansiedade de Separação (corte ≥5)": s_sep,
            "Ansiedade Social (corte ≥8)": s_social,
            "Evitação Escolar (corte ≥3)": s_escolar,
        }

        if total >= 25:
            resultado["interpretacao"].append("⚠️ Score total ≥25: pode indicar Transtorno de Ansiedade (pontuações >30 são mais específicas)")
        else:
            resultado["interpretacao"].append(f"✅ Score total abaixo do ponto de corte (<25) — score: {total}")

        if s_panico >= 7:
            resultado["interpretacao"].append("⚠️ Pânico/Sintomas Somáticos: acima do ponto de corte (≥7)")
        if s_tag >= 9:
            resultado["interpretacao"].append("⚠️ Ansiedade Generalizada: acima do ponto de corte (≥9)")
        if s_sep >= 5:
            resultado["interpretacao"].append("⚠️ Ansiedade de Separação: acima do ponto de corte (≥5)")
        if s_social >= 8:
            resultado["interpretacao"].append("⚠️ Ansiedade Social: acima do ponto de corte (≥8)")
        if s_escolar >= 3:
            resultado["interpretacao"].append("⚠️ Evitação Escolar: acima do ponto de corte (≥3)")

    return resultado


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS DE API
# ══════════════════════════════════════════════════════════════════════════════

def listar_participantes():
    try:
        r = requests.get(f"{API_URL}/participantes", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def criar_participante(nome, idade, sexo, diagnostico):
    payload = {"nome": nome, "idade": idade, "sexo": sexo, "Diagnostico": diagnostico}
    return requests.post(f"{API_URL}/participantes", json=payload, timeout=5)

def criar_avaliacao(participante_id, respostas):
    payload = {"participanteId": participante_id, "respostas": respostas}
    return requests.post(f"{API_URL}/avaliacoes", json=payload, timeout=5)

def deletar_participante(participante_id):
    return requests.delete(f"{API_URL}/participantes/{participante_id}", timeout=5)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR – NAVEGAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

st.sidebar.title("🧠 LAPIA")
st.sidebar.caption("Sistema de Coleta de Dados Clínicos")
pagina = st.sidebar.radio(
    "Navegação",
    ["Cadastro de Participante", "Aplicar Escala", "Visualizar e Exportar"],
)
st.sidebar.divider()
st.sidebar.caption("Backend: `localhost:8080`")

# ══════════════════════════════════════════════════════════════════════════════
# TELA 1 – CADASTRO
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "Cadastro de Participante":
    st.title("Cadastro de Participante")
    st.caption("Preencha os dados do participante da pesquisa.")

    with st.form("form_cadastro"):
        nome = st.text_input("Nome completo")
        col1, col2 = st.columns(2)
        with col1:
            idade = st.number_input("Idade", min_value=1, max_value=120, step=1)
        with col2:
            sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
        diagnostico = st.text_input("Diagnóstico (se houver)", placeholder="Ex: TDAH, suspeita de TDAH…")
        submitted = st.form_submit_button("Cadastrar participante", type="primary")

    if submitted:
        if not nome.strip():
            st.error("Por favor, informe o nome do participante.")
        else:
            try:
                resp = criar_participante(nome.strip(), int(idade), sexo, diagnostico.strip())
                if resp.status_code == 201:
                    st.success(f"Participante **{nome}** cadastrado com sucesso!")
                    st.json(resp.json())
                else:
                    st.error(f"Erro ao cadastrar: {resp.status_code} – {resp.text}")
            except Exception as e:
                st.error(f"Não foi possível conectar ao backend: {e}")

    st.divider()
    st.subheader("Participantes cadastrados")
    participantes = listar_participantes()
    if participantes:
        df = pd.DataFrame(participantes)
        colunas = [c for c in ["id", "nome", "idade", "sexo", "Diagnostico"] if c in df.columns]
        st.dataframe(df[colunas], use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Excluir participante")
        st.warning(
            "⚠️ A exclusão remove o participante e **todas as avaliações associadas** permanentemente.",
            icon="🗑️",
        )
        opcoes_excluir = {f"{p['nome']} (ID {p['id']})": p["id"] for p in participantes}
        selecionado_excluir = st.selectbox(
            "Selecione o participante para excluir",
            list(opcoes_excluir.keys()),
            key="select_excluir",
        )
        id_excluir = opcoes_excluir[selecionado_excluir]

        # Confirmação em duas etapas para evitar exclusão acidental
        confirmar = st.checkbox(
            f'Confirmo que desejo excluir "{selecionado_excluir}" e todos os seus dados.',
            key="confirmar_exclusao",
        )
        if st.button("🗑️ Excluir participante", disabled=not confirmar, type="primary"):
            try:
                resp = deletar_participante(id_excluir)
                if resp.status_code in (200, 204):
                    st.success(f"Participante **{selecionado_excluir}** excluído com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro ao excluir: {resp.status_code} – {resp.text}")
            except Exception as e:
                st.error(f"Não foi possível conectar ao backend: {e}")
    else:
        st.info("Nenhum participante cadastrado ou backend inacessível.")

# ══════════════════════════════════════════════════════════════════════════════
# TELA 2 – APLICAR ESCALA
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "Aplicar Escala":
    st.title("Aplicar Escala Clínica")

    participantes = listar_participantes()
    if not participantes:
        st.warning("Nenhum participante encontrado. Cadastre um participante primeiro.")
        st.stop()

    col_p, col_e = st.columns(2)
    with col_p:
        opcoes_part = {f"{p['nome']} (ID {p['id']})": p["id"] for p in participantes}
        selecionado = st.selectbox("Participante", list(opcoes_part.keys()))
        participante_id = opcoes_part[selecionado]
    with col_e:
        escala_key = st.selectbox("Escala", list(ESCALAS.keys()))

    escala = ESCALAS[escala_key]
    st.info(f"**{escala['descricao']}**\n\n{escala['instrucoes']}", icon="📋")

    opcoes = escala["opcoes"]
    opcoes_labels = list(opcoes.keys())

    # Aviso especial para IGDT-10 (encoding diferente)
    if escala_key == "IGDT-10":
        st.warning(
            "⚠️ Nesta escala: 'Nunca' e 'Algumas vezes' = 0 pontos; 'Frequentemente' = 1 ponto (critério DSM-5).",
            icon="ℹ️",
        )

    respostas_form = {}
    questao_global = 1

    with st.form(f"form_{escala_key}"):
        for secao, questoes in escala["secoes"].items():
            st.subheader(secao)
            for questao in questoes:
                resposta_label = st.radio(
                    f"**{questao_global}.** {questao}",
                    options=opcoes_labels,
                    horizontal=True,
                    index=0,
                    key=f"q_{escala_key}_{questao_global}",
                )
                respostas_form[questao_global] = opcoes[resposta_label]
                questao_global += 1
            st.divider()

        submitted = st.form_submit_button("Salvar avaliação", type="primary")

    if submitted:
        # Lógica de inversão HQ-25
        respostas_finais = dict(respostas_form)
        if escala_key == "HQ-25":
            max_val = max(opcoes.values())
            for idx in escala.get("itens_invertidos", []):
                if idx in respostas_finais:
                    respostas_finais[idx] = max_val - respostas_finais[idx]

        resultado = calcular_resultado(escala_key, respostas_finais)

        # Monta payload para o backend
        payload_respostas = [
            {"numeroQuestao": num, "valor": val}
            for num, val in respostas_finais.items()
        ]

        try:
            resp = criar_avaliacao(participante_id, payload_respostas)
            if resp.status_code == 201:
                st.success("✅ Avaliação salva com sucesso!")
            else:
                st.warning(f"Backend retornou {resp.status_code} — os resultados abaixo foram calculados localmente.")
        except Exception:
            st.warning("Não foi possível conectar ao backend — os resultados abaixo foram calculados localmente.")

        # Exibe resultados
        st.divider()
        st.subheader("Resultado")
        col1, col2 = st.columns(2)
        col1.metric("Score Total", resultado["score_total"])

        if resultado["subescalas"]:
            col2.metric(
                list(resultado["subescalas"].keys())[0],
                list(resultado["subescalas"].values())[0],
            )
            if len(resultado["subescalas"]) > 1:
                st.divider()
                st.markdown("**Subescalas:**")
                cols = st.columns(min(len(resultado["subescalas"]), 3))
                for i, (k, v) in enumerate(resultado["subescalas"].items()):
                    cols[i % len(cols)].metric(k, v)

        st.divider()
        st.markdown("**Interpretação clínica:**")
        for linha in resultado["interpretacao"]:
            st.markdown(linha)

        st.caption(
            "⚕️ Esta avaliação é um instrumento de rastreio e não substitui avaliação clínica completa por profissional de saúde."
        )

# ══════════════════════════════════════════════════════════════════════════════
# TELA 3 – VISUALIZAR E EXPORTAR
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "Visualizar e Exportar":
    st.title("Visualizar e Exportar Dados")

    participantes = listar_participantes()
    if not participantes:
        st.warning("Nenhum participante encontrado.")
        st.stop()

    linhas = []
    for p in participantes:
        avaliacoes = p.get("avaliacoes", [])
        base = {
            "ID Participante": p["id"],
            "Nome": p.get("nome", ""),
            "Idade": p.get("idade", ""),
            "Sexo": p.get("sexo", ""),
            "Diagnóstico": p.get("Diagnostico", ""),
        }
        if not avaliacoes:
            linhas.append({**base, "ID Avaliação": None, "Data": None,
                           "Score Total": None, "Média Desatenção": None,
                           "Média Hiperatividade": None})
        else:
            for av in avaliacoes:
                linhas.append({
                    **base,
                    "ID Avaliação": av.get("id"),
                    "Data": av.get("data") or av.get("dataCriacao"),
                    "Score Total": av.get("pontuacaoSnapIV"),
                    "Média Desatenção": av.get("mediaDesatencao"),
                    "Média Hiperatividade": av.get("mediaHiperatividade"),
                })

    df = pd.DataFrame(linhas)
    st.subheader("Dados coletados")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Exportar")
    col1, col2 = st.columns(2)

    csv = df.to_csv(index=False).encode("utf-8")
    col1.download_button("⬇️ Baixar CSV", csv, "lapia_dados.csv", "text/csv",
                         use_container_width=True)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="LAPIA")
    col2.download_button("⬇️ Baixar Excel", buffer.getvalue(), "lapia_dados.xlsx",
                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                         use_container_width=True)