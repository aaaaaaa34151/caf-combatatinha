import streamlit as st
import sqlite3
import json
import pandas as pd
from datetime import datetime

# =====================================================
# ====================== DATABASE =====================
# =====================================================

def init_db():

    conn = sqlite3.connect("applications.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            character_name TEXT,
            realm TEXT,
            class_name TEXT,
            role TEXT,
            offspec TEXT,
            specs TEXT,
            ilvl INTEGER,
            experience TEXT,
            discord TEXT,
            logs_link TEXT,
            cores TEXT,
            motivation TEXT,
            status TEXT DEFAULT 'Pendente'
        )
    """)

    try:
        c.execute("ALTER TABLE applications ADD COLUMN role TEXT")
    except:
        pass

    try:
        c.execute("ALTER TABLE applications ADD COLUMN offspec TEXT")
    except:
        pass

    conn.commit()
    conn.close()

init_db()

# =====================================================
# ====================== CLASSES ======================
# =====================================================

classes_data = {

    "Cavaleiro da Morte": [
        "Sangue",
        "Gelo",
        "Profano"
    ],

    "Caçador de Demônios": [
        "Devourer",
        "Caos",
        "Vingança"
    ],

    "Druida": [
        "Equilíbrio",
        "Feral",
        "Guardião",
        "Restauração"
    ],

    "Conjurante": [
        "Aprimoramento",
        "Devastação",
        "Preservação"
    ],

    "Caçador": [
        "Domínio das Feras",
        "Precisão",
        "Sobrevivência"
    ],

    "Mago": [
        "Arcano",
        "Fogo",
        "Gélido"
    ],

    "Monge": [
        "Mestre Cervejeiro",
        "Tecelão da Névoa",
        "Andarilho do Vento"
    ],

    "Paladino": [
        "Sagrado",
        "Retribuição",
        "Proteção"
    ],

    "Sacerdote": [
        "Disciplina",
        "Sagrado",
        "Sombra"
    ],

    "Ladino": [
        "Assassinato",
        "Fora-da-Lei",
        "Subterfúgio"
    ],

    "Xamã": [
        "Elemental",
        "Aperfeiçoamento",
        "Restauração"
    ],

    "Bruxo": [
        "Suplício",
        "Demonologia",
        "Destruição"
    ],

    "Guerreiro": [
        "Armas",
        "Fúria",
        "Proteção"
    ]
}

# =====================================================
# ====================== CORES ========================
# =====================================================

cores_info = {

    "Time Garrosh (Mítico Hardcore)": {
        "leader": "Mortalos",
        "ilvl_min": 280,

        "rules": """
**🏆 TIME GARROSH (MÍTICO HARDCORE)**

**Objetivo:**  
Conquistar Cutting Edge.

---

### 📅 Dias e Horários
- Quartas e Quintas-feiras
- 20h30 às 22h30
- Pode estender até 30 minutos

---

### 📜 Regras de Conduta

• Respeito e boa convivência são fundamentais para manter um ambiente agradável e produtivo para todos.

• Cobranças entre jogadores não serão permitidas. Qualquer feedback ou cobrança será feito exclusivamente pelo Raid Leader ou pela Diretoria.

• Zero toxicidade. Não serão toleradas ofensas, provocações ou atitudes que prejudiquem o grupo.

---

### ✅ Requisitos Mínimos

• Item Level mínimo: 280.

• Gemas no nível máximo e encantamentos no nível máximo em todos os equipamentos relevantes.

• A presença é de extrema importância para o progresso do Core e para o alcance dos nossos objetivos.

• Atrasos ou faltas devem ser comunicados com antecedência, sempre que possível.

• O sistema de loot será realizado via RCLootCouncil, utilizando um sistema de pontuação para garantir uma distribuição justa e transparente dos itens.
"""
    },

    "Time Baine (Mítico Soft)": {
        "leader": "Grilo",
        "ilvl_min": 276,

        "rules": """
**🦗 TIME BAINE (MÍTICO SOFT)**

**Filosofia:**  
Progressão consistente sem virar obrigação.  
Queremos matar bosses míticos mantendo o ambiente saudável.

---

### 📅 Dias e Horários
- Quartas e Quintas-feiras
- 20h00 às 22h00
- Pode haver extensão se todos concordarem

---

### 📜 Regras Principais
- Presença mínima: 75-80%
- Avisar falta com antecedência
- Preparação obrigatória
  - Encantos
  - Gemas
  - Consumíveis
  - Estratégia
- Comunicação limpa durante as pulls
- Loot por upgrade / bis
- Erros são corrigidos, não humilhados
"""
    },

    "Time Dragonetinhos (Heroico)": {
        "leader": "Sakiv",
        "ilvl_min": 270,

        "rules": """
**🐉 TIME DRAGONETINHOS (HEROICO)**

Core Heroico focado em:
- Diversão
- Aprendizado
- Loot

Ambiente descontraído para progressão.
"""
    },

    "Time Café com Açúcar (Heroico)": {
        "leader": "Klebrimbor",
        "ilvl_min": 270,

        "rules": """
**☕ TIME CAFÉ COM AÇÚCAR (HEROICO)**

Core Heroico leve e agradável.

Ideal para quem quer:
- Jogar relaxado
- Fazer progressão
- Manter qualidade sem pressão excessiva
"""
    }
}

# =====================================================
# ====================== FUNCTIONS ====================
# =====================================================

def update_status(app_id, new_status):

    conn = sqlite3.connect("applications.db")
    c = conn.cursor()

    c.execute(
        "UPDATE applications SET status = ? WHERE id = ?",
        (new_status, app_id)
    )

    conn.commit()
    conn.close()


def reset_specs():

    for specs in classes_data.values():

        for spec in specs:

            key = f"spec_{spec}"

            if key in st.session_state:
                st.session_state[key] = False


def safe_json_list(value):

    try:
        return json.loads(value)
    except:
        return []


# =====================================================
# ====================== CONFIG =======================
# =====================================================

st.set_page_config(
    page_title="Café com Batatinha",
    page_icon="☕",
    layout="wide"
)

# =====================================================
# ====================== STYLE ========================
# =====================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 95vw;
}

div[data-testid="stExpander"] {
    border-radius: 12px;
    border: 1px solid #333333;
}

div[data-testid="stDataFrame"] {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# ====================== SESSION ======================
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =====================================================
# ====================== HEADER =======================
# =====================================================

st.title("☕ CAFÉ COM BATATINHA")
st.caption("Guilda • WoW Midnight")

pagina = st.sidebar.selectbox(
    "Escolha a página",
    [
        "📝 Formulário de Aplicação",
        "🔐 Painel Admin"
    ]
)

# =====================================================
# ====================== FORM PAGE ====================
# =====================================================

if pagina == "📝 Formulário de Aplicação":

    st.subheader("📝 Aplicação")

    with st.container(border=True):

        classe = st.selectbox(
            "Classe *",
            options=list(classes_data.keys()),
            key="classe_select",
            on_change=reset_specs
        )

        with st.form("form_aplicacao"):

            col1, col2 = st.columns(2)

            with col1:

                name = st.text_input(
                    "Nome do Personagem *"
                )

                realm = st.text_input(
                    "Realm",
                    value="Azralon"
                )

            with col2:

                ilvl = st.number_input(
                    "Item Level *",
                    min_value=260,
                    max_value=700,
                    value=280
                )

            st.divider()

            st.markdown("### ⚔️ Especializações")

            selected_specs = []

            spec_cols = st.columns(2)

            specs = classes_data.get(classe, [])

            for index, spec in enumerate(specs):

                with spec_cols[index % 2]:

                    if st.checkbox(
                        spec,
                        key=f"spec_{spec}"
                    ):
                        selected_specs.append(spec)

            st.divider()

            role = st.selectbox(
                "Função Principal *",
                [
                    "DPS",
                    "Healer",
                    "Tank"
                ]
            )

            offspec = st.selectbox(
                "Tem Off Spec?",
                [
                    "Não",
                    "DPS",
                    "Healer",
                    "Tank"
                ]
            )

            experience = st.selectbox(
                "Experiência em Raids Endgame *",
                [
                    "Menos de 1 ano",
                    "1-3 anos",
                    "3-6 anos",
                    "Mais de 6 anos (Veterano)"
                ]
            )

            discord = st.text_input(
                "Discord *"
            )

            logs_link = st.text_input(
                "Raider.IO ou WarcraftLogs"
            )

            st.divider()

            st.markdown("### 🛡️ Cores Disponíveis")

            selected_cores = []

            for core_name, info in cores_info.items():

                with st.expander(
                    f"{core_name} • Líder: {info['leader']}"
                ):

                    st.caption(
                        f"Ilvl mínimo: {info['ilvl_min']}+"
                    )

                    st.markdown(info["rules"])

                    if st.checkbox(
                        f"Aplicar para {core_name}",
                        key=core_name
                    ):
                        selected_cores.append(core_name)

            st.divider()

            motivation = st.text_area(
                "Motivação",
                placeholder=(
                    "Exemplo:\n"
                    "Jogo WoW desde Legion, tenho experiência em raid mítica, "
                    "sou pontual, gosto de progressão e procuro uma guilda "
                    "ativa para jogar Midnight."
                )
            )

            submit = st.form_submit_button(
                "🚀 ENVIAR APLICAÇÃO",
                width="stretch",
                type="primary"
            )

            if submit:

                if (
                    not name
                    or not classe
                    or len(selected_specs) == 0
                    or not discord
                    or len(selected_cores) == 0
                ):

                    st.error(
                        "❌ Preencha todos os campos obrigatórios."
                    )

                else:

                    conn = sqlite3.connect(
                        "applications.db"
                    )

                    c = conn.cursor()

                    c.execute("""
                        INSERT INTO applications (
                            timestamp,
                            character_name,
                            realm,
                            class_name,
                            role,
                            offspec,
                            specs,
                            ilvl,
                            experience,
                            discord,
                            logs_link,
                            cores,
                            motivation
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        name,
                        realm,
                        classe,
                        role,
                        offspec,
                        json.dumps(selected_specs),
                        ilvl,
                        experience,
                        discord,
                        logs_link,
                        json.dumps(selected_cores),
                        motivation
                    ))

                    conn.commit()
                    conn.close()

                    st.success(
                        "✅ Aplicação enviada com sucesso!"
                    )

                    st.balloons()

# =====================================================
# ====================== ADMIN PAGE ===================
# =====================================================

elif pagina == "🔐 Painel Admin":

    if not st.session_state.logged_in:

        st.subheader("🔐 Login Administrativo")

        with st.container(border=True):

            user = st.text_input(
                "Usuário",
                value="admin"
            )

            pwd = st.text_input(
                "Senha",
                type="password"
            )

            if st.button(
                "Entrar",
                type="primary",
                width="stretch"
            ):

                if (
                    user == "admin"
                    and pwd == "BilbosBulos23"
                ):

                    st.session_state.logged_in = True
                    st.rerun()

                else:

                    st.error(
                        "Usuário ou senha incorretos."
                    )

    else:

        top_col1, top_col2 = st.columns([8, 2])

        with top_col1:
            st.subheader("📋 Painel Administrativo")

        with top_col2:

            if st.button(
                "🚪 Sair",
                width="stretch"
            ):

                st.session_state.logged_in = False
                st.rerun()

        conn = sqlite3.connect("applications.db")

        df = pd.read_sql_query(
            "SELECT * FROM applications ORDER BY timestamp DESC",
            conn
        )

        conn.close()

        if df.empty:

            st.info(
                "Nenhuma aplicação encontrada."
            )

        else:

            df_display = df.copy()

            df_display["timestamp"] = pd.to_datetime(
                df_display["timestamp"]
            ).dt.strftime("%d/%m/%Y %H:%M")

            df_display["specs"] = df_display["specs"].apply(
                lambda x: ", ".join(safe_json_list(x))
                if isinstance(x, str)
                else ""
            )

            df_display["cores"] = df_display["cores"].apply(
                lambda x: ", ".join(safe_json_list(x))
                if isinstance(x, str)
                else ""
            )

            df_display["role"] = df_display["role"].fillna("Não informado")
            df_display["offspec"] = df_display["offspec"].fillna("Não")

            aprovados = len(
                df[df["status"] == "Aprovado"]
            )

            rejeitados = len(
                df[df["status"] == "Rejeitado"]
            )

            pendentes = len(
                df[df["status"] == "Pendente"]
            )

            m1, m2, m3 = st.columns(3)

            m1.metric("Pendentes", pendentes)
            m2.metric("Aprovados", aprovados)
            m3.metric("Rejeitados", rejeitados)

            st.divider()

            st.markdown("### 📄 Aplicações")

            st.dataframe(
                df_display[
                    [
                        "timestamp",
                        "character_name",
                        "class_name",
                        "specs",
                        "role",
                        "offspec",
                        "ilvl",
                        "cores",
                        "status"
                    ]
                ],
                width="stretch",
                hide_index=True,
                column_config={
                    "timestamp": st.column_config.TextColumn(
                        "Data",
                        width="medium"
                    ),
                    "character_name": st.column_config.TextColumn(
                        "Personagem",
                        width="medium"
                    ),
                    "class_name": st.column_config.TextColumn(
                        "Classe",
                        width="medium"
                    ),
                    "specs": st.column_config.TextColumn(
                        "Especialização",
                        width="medium"
                    ),
                    "role": st.column_config.TextColumn(
                        "Função",
                        width="small"
                    ),
                    "offspec": st.column_config.TextColumn(
                        "Off Spec",
                        width="small"
                    ),
                    "ilvl": st.column_config.NumberColumn(
                        "Ilvl",
                        width="small"
                    ),
                    "cores": st.column_config.TextColumn(
                        "Cores",
                        width="medium"
                    ),
                    "status": st.column_config.TextColumn(
                        "Status",
                        width="small"
                    ),
                }
            )

            st.divider()

            st.markdown("### 🔎 Detalhes")

            for _, row in df.iterrows():

                specs = ", ".join(
                    safe_json_list(row["specs"])
                )

                cores = ", ".join(
                    safe_json_list(row["cores"])
                )

                role = (
                    row["role"]
                    if row["role"]
                    else "Não informado"
                )

                offspec = (
                    row["offspec"]
                    if "offspec" in row
                    and row["offspec"]
                    else "Não"
                )

                expander_key = f"exp_{row['id']}"

                with st.expander(
                    f"{row['character_name']} • "
                    f"{row['class_name']} "
                    f"({specs}) • "
                    f"{role} • "
                    f"{row['status']}",
                    expanded=(
                        st.session_state.get("open_expander")
                        == expander_key
                    )
                ):

                    info1, info2 = st.columns(2)

                    with info1:

                        st.write(
                            f"**Nome do Personagem:** {row['character_name']}"
                        )

                        st.write(
                            f"**Realm:** {row['realm']}"
                        )

                        st.write(
                            f"**Classe:** {row['class_name']}"
                        )

                        st.write(
                            f"**Item Level:** {row['ilvl']}"
                        )

                        st.write(
                            f"**Especializações:** {specs}"
                        )

                        st.write(
                            f"**Função:** {role}"
                        )

                        st.write(
                            f"**Off Spec:** {offspec}"
                        )

                        st.write(
                            f"**Discord:** {row['discord']}"
                        )

                    with info2:

                        st.write(
                            f"**Experiência:** "
                            f"{row['experience']}"
                        )

                        st.write(
                            f"**Cores:** {cores}"
                        )

                        st.write(
                            f"**Logs:** "
                            f"{row['logs_link'] or 'Não informado'}"
                        )

                    st.markdown("### ✍️ Motivação")

                    st.write(
                        row["motivation"]
                        if row["motivation"]
                        else "Não informado"
                    )

                    st.divider()

                    b1, b2, b3 = st.columns(3)

                    with b1:

                        if st.button(
                            "✅ Aprovar",
                            key=f"approve_{row['id']}",
                            width="stretch"
                        ):

                            st.session_state["open_expander"] = expander_key

                            update_status(
                                row["id"],
                                "Aprovado"
                            )

                            st.rerun()

                    with b2:

                        if st.button(
                            "❌ Rejeitar",
                            key=f"reject_{row['id']}",
                            width="stretch"
                        ):

                            st.session_state["open_expander"] = expander_key

                            update_status(
                                row["id"],
                                "Rejeitado"
                            )

                            st.rerun()

                    with b3:

                        if st.button(
                            "⏳ Pendente",
                            key=f"pending_{row['id']}",
                            width="stretch"
                        ):

                            st.session_state["open_expander"] = expander_key

                            update_status(
                                row["id"],
                                "Pendente"
                            )

                            st.rerun()

# =====================================================
# ====================== FOOTER =======================
# =====================================================

st.sidebar.caption(
    "☕ Café com Batatinha • WoW Midnight"
)
