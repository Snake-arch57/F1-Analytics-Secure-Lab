import os
import psycopg2
from groq import Groq

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        database=os.getenv("POSTGRES_DB", "f1_analytics"),
        user=os.getenv("POSTGRES_USER", "f1_app"),
        password=os.getenv("POSTGRES_PASSWORD", "f1_local_dev_password")
    )

def init_chat_tables():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES chat_sessions(id) ON DELETE CASCADE,
                role VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro nas tabelas: {e}")

init_chat_tables()

def create_chat_session(title="Novo Chat"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO chat_sessions (title) VALUES (%s) RETURNING id;", (title,))
    session_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return session_id

def get_all_sessions():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title FROM chat_sessions ORDER BY created_at DESC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Converte para dicionário nativo do Python (Evita bug no Streamlit)
        return [{"id": r[0], "title": r[1]} for r in rows]
    except:
        return []

def get_chat_messages(session_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC;", (session_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Converte para dicionário nativo do Python
        return [{"role": r[0], "content": r[1]} for r in rows]
    except:
        return []

def save_message(session_id, role, content):
    if not session_id: return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s);", (session_id, role, content))
    conn.commit()
    cur.close()
    conn.close()

def get_ai_stream_response(user_prompt: str, session_id: int):
    context = ""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT team_name, season, avg_lap_time_seconds FROM team_performance LIMIT 5;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        context = "Dados recentes:\n" + "\n".join([f"{r[0]} ({r[1]}): {r[2]}s" for r in rows])
    except:
        pass

    history = get_chat_messages(session_id) if session_id else []
    messages = [{"role": "system", "content": f"Você é um assistente sobre F1. Contexto:\n{context}"}]
    
    for msg in history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": user_prompt})

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    try:
        completion = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=messages,
            temperature=0.7,
            stream=True
        )
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"⚠️ Erro Groq API: {str(e)}"
