import streamlit as st
import json
import pandas as pd
import requests
import base64
import os
import uuid
import time

from datetime import datetime

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
# =============== CONFIGURAÇÃO GITHUB =================
# =====================================================

def get_config_value(key, default=""):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


GITHUB_TOKEN = get_config_value("GITHUB_TOKEN")
GITHUB_OWNER = get_config_value("GITHUB_OWNER")
GITHUB_REPO = get_config_value("GITHUB_REPO")
GITHUB_BRANCH = get_config_value("GITHUB_BRANCH", "main")
GITHUB_DATA_PATH = get_config_value(
    "GITHUB_DATA_PATH",
    "data/applications.json"
)

GITHUB_API_VERSION = "2022-11-28"

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

    "Time Sylvanas (Mítico Soft)": {
        "leader": "Grilo",
        "ilvl_min": 276,

        "rules": """
**🏹 TIME SYLVANAS (MÍTICO SOFT)**

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
# ====================== GITHUB API ===================
# =====================================================

def github_is_configured():
    return all([
        GITHUB_TOKEN,
        GITHUB_OWNER,
        GITHUB_REPO,
        GITHUB_BRANCH,
        GITHUB_DATA_PATH
    ])


def github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION
    }


def github_file_url():
    return (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/contents/{GITHUB_DATA_PATH}"
    )


def normalize_core_name(core_name):

    if core_name == "Time Baine (Mítico Soft)":
        return "Time Sylvanas (Mítico Soft)"

    return core_name


def normalize_application(app):

    app.setdefault("id", str(uuid.uuid4()))
    app.setdefault("timestamp", datetime.now().isoformat())
    app.setdefault("character_name", "")
    app.setdefault("realm", "")
    app.setdefault("class_name", "")
    app.setdefault("role", "")
    app.setdefault("offspec", "Não")
    app.setdefault("specs", [])
    app.setdefault("ilvl", 0)
    app.setdefault("experience", "")
    app.setdefault("discord", "")
    app.setdefault("logs_link", "")
    app.setdefault("cores", [])
    app.setdefault("motivation", "")
    app.setdefault("status", "Pendente")

    app["cores"] = [
        normalize_core_name(core)
        for core in safe_list(app.get("cores", []))
    ]

    app["specs"] = safe_list(app.get("specs", []))

    return app


def load_applications_from_github():

    if not github_is_configured():
        return [], None, "GitHub não configurado."

    try:

        response = requests.get(
            github_file_url(),
            headers=github_headers(),
            params={
                "ref": GITHUB_BRANCH
            },
            timeout=20
        )

        if response.status_code == 404:
            return [], None, None

        if response.status_code != 200:
            return [], None, response.text

        data = response.json()

        sha = data.get("sha")

        encoded_content = data.get("content", "")

        decoded_content = base64.b64decode(
            encoded_content
        ).decode("utf-8")

        if decoded_content.strip() == "":
            return [], sha, None

        applications = json.loads(decoded_content)

        if not isinstance(applications, list):
            applications = []

        applications = [
            normalize_application(app)
            for app in applications
            if isinstance(app, dict)
        ]

        return applications, sha, None

    except Exception as e:
        return [], None, str(e)


def save_applications_to_github(applications, sha=None, message="Atualizar aplicações"):

    if not github_is_configured():
        return False, "GitHub não configurado."

    try:

        applications = [
            normalize_application(app)
            for app in applications
            if isinstance(app, dict)
        ]

        content_string = json.dumps(
            applications,
            ensure_ascii=False,
            indent=2
        )

        encoded_content = base64.b64encode(
            content_string.encode("utf-8")
        ).decode("utf-8")

        payload = {
            "message": message,
            "content": encoded_content,
            "branch": GITHUB_BRANCH
        }

        if sha:
            payload["sha"] = sha

        response = requests.put(
            github_file_url(),
            headers=github_headers(),
            json=payload,
            timeout=20
        )

        if response.status_code in [200, 201]:
            return True, None

        return False, response.text

    except Exception as e:
        return False, str(e)


def save_new_application(new_application):

    for attempt in range(3):

        applications, sha, error = load_applications_from_github()

        if error:
            return False, error

        for app in applications:

            same_character = (
                str(app.get("character_name", "")).strip().lower()
                == str(new_application.get("character_name", "")).strip().lower()
            )

            same_realm = (
                str(app.get("realm", "")).strip().lower()
                == str(new_application.get("realm", "")).strip().lower()
            )

            if same_character and same_realm:

                status = app.get("status", "Pendente")

                return (
                    False,
                    f"duplicate::{status}"
                )

        applications.append(
            normalize_application(new_application)
        )

        ok, save_error = save_applications_to_github(
            applications,
            sha,
            message=f"Nova aplicação: {new_application.get('character_name', '')}"
        )

        if ok:
            return True, None

        if "409" in str(save_error) or "sha" in str(save_error).lower():
            time.sleep(1)
            continue

        return False, save_error

    return False, "Conflito ao salvar no GitHub. Tente enviar novamente."


def update_status(app_id, new_status):

    for attempt in range(3):

        applications, sha, error = load_applications_from_github()

        if error:
            return False, error

        found = False

        for app in applications:

            if str(app.get("id")) == str(app_id):
                app["status"] = new_status
                found = True
                break

        if not found:
            return False, "Aplicação não encontrada."

        ok, save_error = save_applications_to_github(
            applications,
            sha,
            message=f"Atualizar status: {app_id} -> {new_status}"
        )

        if ok:
            return True, None

        if "409" in str(save_error) or "sha" in str(save_error).lower():
            time.sleep(1)
            continue

        return False, save_error

    return False, "Conflito ao atualizar status. Tente novamente."


# =====================================================
# ====================== HELPERS ======================
# =====================================================

def reset_specs():

    for specs in classes_data.values():

        for spec in specs:

            key = f"spec_{spec}"

            if key in st.session_state:
                st.session_state[key] = False


def safe_json_list(value):

    try:

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            return json.loads(value)

        return []

    except:
        return []


def safe_list(value):

    if isinstance(value, list):
        return value

    if isinstance(value, str):

        if value.strip() == "":
            return []

        try:
            parsed = json.loads(value)

            if isinstance(parsed, list):
                return parsed

            return [str(parsed)]

        except:
            return [value]

    return []


def applications_to_dataframe(applications):

    normalized_apps = [
        normalize_application(app)
        for app in applications
    ]

    df = pd.DataFrame(normalized_apps)

    expected_columns = [
        "id",
        "timestamp",
        "character_name",
        "realm",
        "class_name",
        "role",
        "offspec",
        "specs",
        "ilvl",
        "experience",
        "discord",
        "logs_link",
        "cores",
        "motivation",
        "status"
    ]

    for col in expected_columns:

        if col not in df.columns:
            df[col] = ""

    return df[expected_columns]


# =====================================================
# ====================== SESSION ======================
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "open_expander" not in st.session_state:
    st.session_state.open_expander = None

# =====================================================
# ====================== HEADER =======================
# =====================================================

st.title("☕ CAFÉ COM BATATINHA")
st.caption("Guilda • WoW Midnight")

if not github_is_configured():

    st.error(
        "❌ GitHub não configurado. Configure os secrets do Streamlit antes de usar o app."
    )

    st.code("""
GITHUB_TOKEN = "seu_token_github"
GITHUB_OWNER = "seu_usuario_ou_org"
GITHUB_REPO = "nome_do_repositorio"
GITHUB_BRANCH = "main"
GITHUB_DATA_PATH = "data/applications.json"
""", language="toml")

    st.stop()

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
                    "Realm *",
                    placeholder="Ex: Area-52"
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

            st.markdown("### 🛡️ Core Desejado")

            core_placeholder = "Selecione um core"

            core_options = [
                core_placeholder
            ] + list(cores_info.keys())

            selected_core_option = st.radio(
                "Escolha apenas um core *",
                options=core_options,
                index=0
            )

            selected_cores = []

            if selected_core_option != core_placeholder:

                selected_cores = [
                    selected_core_option
                ]

                selected_core_info = cores_info[selected_core_option]

                with st.expander(
                    f"Regras do {selected_core_option} • Líder: {selected_core_info['leader']}",
                    expanded=True
                ):

                    st.caption(
                        f"Ilvl mínimo: {selected_core_info['ilvl_min']}+"
                    )

                    st.markdown(selected_core_info["rules"])

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
                    or not realm
                    or not classe
                    or len(selected_specs) == 0
                    or not discord
                    or len(selected_cores) == 0
                ):

                    st.error(
                        "❌ Preencha todos os campos obrigatórios."
                    )

                else:

                    new_application = {
                        "id": str(uuid.uuid4()),
                        "timestamp": datetime.now().isoformat(),
                        "character_name": name.strip(),
                        "realm": realm.strip(),
                        "class_name": classe,
                        "role": role,
                        "offspec": offspec,
                        "specs": selected_specs,
                        "ilvl": int(ilvl),
                        "experience": experience,
                        "discord": discord.strip(),
                        "logs_link": logs_link.strip(),
                        "cores": selected_cores,
                        "motivation": motivation.strip(),
                        "status": "Pendente"
                    }

                    ok, error = save_new_application(new_application)

                    if ok:

                        st.success(
                            "✅ Aplicação enviada com sucesso!"
                        )

                        st.balloons()

                    else:

                        if str(error).startswith("duplicate::"):

                            status_atual = str(error).replace(
                                "duplicate::",
                                ""
                            )

                            st.error(
                                f"❌ Já existe uma aplicação para esse personagem nesse realm. "
                                f"Status atual: {status_atual}."
                            )

                        else:

                            st.error(
                                f"❌ Erro ao salvar no GitHub: {error}"
                            )

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

        applications, sha, load_error = load_applications_from_github()

        if load_error:

            st.error(
                f"❌ Erro ao carregar aplicações do GitHub: {load_error}"
            )

            st.stop()

        df = applications_to_dataframe(applications)

        if df.empty:

            st.info(
                "Nenhuma aplicação encontrada."
            )

        else:

            df_display = df.copy()

            df_display["timestamp"] = pd.to_datetime(
                df_display["timestamp"],
                errors="coerce"
            ).dt.strftime("%d/%m/%Y %H:%M")

            df_display["specs"] = df_display["specs"].apply(
                lambda x: ", ".join(safe_list(x))
            )

            df_display["cores"] = df_display["cores"].apply(
                lambda x: ", ".join(
                    normalize_core_name(core)
                    for core in safe_list(x)
                )
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
                        "Core",
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
                    safe_list(row["specs"])
                )

                cores = ", ".join(
                    normalize_core_name(core)
                    for core in safe_list(row["cores"])
                )

                role = (
                    row["role"]
                    if row["role"]
                    else "Não informado"
                )

                offspec = (
                    row["offspec"]
                    if row["offspec"]
                    else "Não"
                )

                app_id = row["id"]

                expander_key = f"exp_{app_id}"

                with st.expander(
                    f"{row['character_name']} • "
                    f"{row['class_name']} "
                    f"({specs}) • "
                    f"{role} • "
                    f"Core: {cores} • "
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
                            f"**Core:** {cores}"
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
                            key=f"approve_{app_id}",
                            width="stretch"
                        ):

                            st.session_state["open_expander"] = expander_key

                            ok, error = update_status(
                                app_id,
                                "Aprovado"
                            )

                            if not ok:
                                st.error(error)
                            else:
                                st.rerun()

                    with b2:

                        if st.button(
                            "❌ Rejeitar",
                            key=f"reject_{app_id}",
                            width="stretch"
                        ):

                            st.session_state["open_expander"] = expander_key

                            ok, error = update_status(
                                app_id,
                                "Rejeitado"
                            )

                            if not ok:
                                st.error(error)
                            else:
                                st.rerun()

                    with b3:

                        if st.button(
                            "⏳ Pendente",
                            key=f"pending_{app_id}",
                            width="stretch"
                        ):

                            st.session_state["open_expander"] = expander_key

                            ok, error = update_status(
                                app_id,
                                "Pendente"
                            )

                            if not ok:
                                st.error(error)
                            else:
                                st.rerun()

# =====================================================
# ====================== FOOTER =======================
# =====================================================

st.sidebar.caption(
    "☕ Café com Batatinha • WoW Midnight"
)
