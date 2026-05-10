import streamlit as st
import sqlite3
import json
import pandas as pd
from datetime import datetime

# ====================== BANCO DE DADOS ======================
def init_db():
    conn = sqlite3.connect('applications.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    character_name TEXT,
                    realm TEXT,
                    class_name TEXT,
                    specs TEXT,
                    ilvl INTEGER,
                    experience TEXT,
                    discord TEXT,
                    logs_link TEXT,
                    cores TEXT,
                    motivation TEXT,
                    status TEXT DEFAULT "Pendente"
                 )''')
    conn.commit()
    conn.close()

init_db()

# ====================== DADOS ======================
classes_data = {
    "Guerreiro": ["Armas", "Fúria", "Proteção"],
    "Paladino": ["Sagrado", "Proteção", "Retribuição"],
    "Caçador": ["Mestre das Bestas", "Atirador", "Sobrevivência"],
    "Ladino": ["Assassinato", "Combate", "Sutis"],
    "Sacerdote": ["Disciplina", "Sagrado", "Sombra"],
    "Xamã": ["Elemental", "Aperfeiçoamento", "Restauração"],
    "Mago": ["Arcano", "Fogo", "Gelo"],
    "Bruxo": ["Suplício", "Demonologia", "Destruição"],
    "Monge": ["Cervejeiro", "Tecelão da Névoa", "Andarilho do Vento"],
    "Cavaleiro da Morte": ["Sangue", "Gélido", "Profano"],
    "Caçador de Demônios": ["Devastação", "Vingança"],
    "Druida": ["Equilíbrio", "Feral", "Guardião", "Restauração"],
    "Evocador": ["Devastação", "Preservação", "Aumento"]
}

cores_info = {
    "Time Garrosh (Mítico Hardcore)": {
        "leader": "Mortalos",
        "ilvl_min": 280,
        "rules": "**🏆 TIME GARROSH (MÍTICO HARDCORE)**\n\nFoco em Cutting Edge • Quartas e Quintas 20h30-22h30"
    },
    "Time Baine (Mítico Soft)": {
        "leader": "Grilo",
        "ilvl_min": 276,
        "rules": "**🦗 TIME BAINE (MÍTICO SOFT)**\n\nProgressão consistente • Quartas e Quintas 20h-22h"
    },
    "Time Dragonetinhos (Heroico)": {
        "leader": "Sakiv",
        "ilvl_min": 270,
        "rules": "Core Heroico descontraído e divertido"
    },
    "Time Café com Açúcar (Heroico)": {
        "leader": "Klebrimbor",
        "ilvl_min": 270,
        "rules": "Core Heroico leve e agradável"
    }
}

# ====================== ATUALIZAR STATUS ======================
def update_status(app_id, new_status):
    conn = sqlite3.connect('applications.db')
    c = conn.cursor()
    c.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
    conn.commit()
    conn.close()

# ====================== INTERFACE ======================
st.set_page_config(page_title="Café com Batatinha", page_icon="☕", layout="centered")

st.title("☕ CAFÉ COM BATATINHA")
st.subheader("Guilda • WoW Midnight")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

pagina = st.sidebar.selectbox("Escolha a página", ["📝 Formulário de Aplicação", "🔐 Painel Admin"])

# ====================== FORMULÁRIO ======================
if pagina == "📝 Formulário de Aplicação":
    st.write("### Preencha sua aplicação")

    with st.form("form_aplicacao"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nome do Personagem *")
            realm = st.text_input("Realm", value="Azralon")
        with col2:
            ilvl = st.number_input("Item Level Atual *", min_value=260, max_value=700, value=280)

        classe = st.selectbox("Classe *", options=list(classes_data.keys()))
        selected_specs = [spec for spec in classes_data[classe] if st.checkbox(spec)]

        experience = st.selectbox("Sua Experiência em Raids Endgame *", 
                                  ["Menos de 1 ano", "1-3 anos", "3-6 anos", "Mais de 6 anos (Veterano)"])

        discord = st.text_input("Discord * (ex: seuuser#1234)")
        logs_link = st.text_input("Link Raider.IO ou WarcraftLogs")

        st.write("### Cores Disponíveis")
        selected_cores = []
        for core_name, info in cores_info.items():
            with st.expander(f"**{core_name}** — Líder: {info['leader']}"):
                st.caption(f"**Ilvl mínimo:** {info['ilvl_min']}+")
                st.markdown(info['rules'])
                if st.checkbox(f"Quero aplicar para {core_name}", key=core_name):
                    selected_cores.append(core_name)

        motivation = st.text_area("Motivação")

        if st.form_submit_button("ENVIAR APLICAÇÃO", type="primary"):
            if not name or not classe or len(selected_specs) == 0 or not discord or len(selected_cores) == 0:
                st.error("❌ Preencha todos os campos obrigatórios!")
            else:
                conn = sqlite3.connect('applications.db')
                c = conn.cursor()
                c.execute('''INSERT INTO applications 
                            (timestamp, character_name, realm, class_name, specs, ilvl, experience, discord, logs_link, cores, motivation)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (datetime.now().isoformat(), name, realm, classe,
                          json.dumps(selected_specs), ilvl, experience, discord, logs_link,
                          json.dumps(selected_cores), motivation))
                conn.commit()
                conn.close()
                st.success("✅ Aplicação enviada com sucesso!")
                st.balloons()

# ====================== PAINEL ADMIN ======================
elif pagina == "🔐 Painel Admin":
    if not st.session_state.logged_in:
        st.title("🔐 Login - Painel Administrativo")
        col1, col2 = st.columns(2)
        with col1:
            user = st.text_input("Usuário", value="admin")
        with col2:
            pwd = st.text_input("Senha", type="password")

        if st.button("Entrar", type="primary"):
            if user == "admin" and pwd == "BilbosBulos23":
                st.session_state.logged_in = True
                st.success("Login realizado!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")
    else:
        st.title("🔐 Painel Administrativo")
        if st.button("🚪 Sair"):
            st.session_state.logged_in = False
            st.rerun()

        conn = sqlite3.connect('applications.db')
        df = pd.read_sql_query("SELECT * FROM applications ORDER BY timestamp DESC", conn)
        conn.close()

        if df.empty:
            st.info("Nenhuma aplicação ainda.")
        else:
            st.subheader("📋 Aplicações Recebidas")
            df_display = df.copy()
            df_display['timestamp'] = pd.to_datetime(df_display['timestamp']).dt.strftime('%d/%m/%Y %H:%M')
            df_display['cores'] = df_display['cores'].apply(lambda x: ', '.join(json.loads(x)) if isinstance(x, str) else '')

            st.dataframe(df_display[['timestamp', 'character_name', 'class_name', 'ilvl', 'cores', 'status']], 
                       use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("🔍 Detalhes e Ações Individuais")
            st.caption("**Clique duas vezes nas opções para confirmar a seleção**")

            for _, row in df.iterrows():
                with st.expander(f"📌 {row['character_name']} — {row['class_name']} ({row['ilvl']} ilvl) | {row['status']}"):
                    st.write(f"**Discord:** {row['discord']}")
                    st.write(f"**Experiência:** {row['experience']}")
                    st.write(f"**Cores:** {', '.join(json.loads(row['cores']))}")
                    st.write(f"**Logs:** {row['logs_link'] or 'Não informado'}")
                    st.write("**Motivação:**")
                    st.write(row.get('motivation', 'Não informado'))

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✅ Aprovar", key=f"ap_{row['id']}"):
                            update_status(row['id'], "Aprovado")
                            st.success(f"{row['character_name']} foi Aprovado!")
                    with col2:
                        if st.button("❌ Rejeitar", key=f"rej_{row['id']}"):
                            update_status(row['id'], "Rejeitado")
                            st.error(f"{row['character_name']} foi Rejeitado!")
                    with col3:
                        if st.button("⏳ Pendente", key=f"pen_{row['id']}"):
                            update_status(row['id'], "Pendente")
                            st.warning("Voltou para Pendente")

st.sidebar.caption("Café com Batatinha • WoW Midnight")