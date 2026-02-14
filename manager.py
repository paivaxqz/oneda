import sqlite3
import asyncio
import subprocess
import sys
import time
import os

DB_NAME = "database.db"
BOT_SCRIPT = "main.py"

# Dicionário para rastrear processos ativos: {user_id: process_obj}
active_processes = {}

def get_active_bots():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT user_id, discord_token, category_ids, response_msg FROM bots WHERE is_active = 1")
    bots = c.fetchall()
    conn.close()
    return bots

def start_bot_process(user_id, token, categories, message):
    env = os.environ.copy()
    env["DISCORD_TOKEN"] = token
    env["CATEGORY_ID"] = categories
    env["RESPONSE_MSG"] = message
    
    # Inicia o processo isolado
    print(f"[+] Iniciando Bot do User ID {user_id}...")
    proc = subprocess.Popen([sys.executable, BOT_SCRIPT], env=env)
    return proc

def stop_bot_process(user_id):
    if user_id in active_processes:
        print(f"[-] Parando Bot do User ID {user_id}...")
        proc = active_processes[user_id]
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        del active_processes[user_id]

def main():
    print("[*] Manager Iniciado. Monitorando banco de dados...")
    while True:
        try:
            current_active_bots = get_active_bots()
            active_ids = {bot['user_id'] for bot in current_active_bots}
            
            # 1. Inicia novos bots
            for bot in current_active_bots:
                uid = bot['user_id']
                if uid not in active_processes:
                    proc = start_bot_process(uid, bot['discord_token'], bot['category_ids'], bot['response_msg'])
                    active_processes[uid] = proc
                elif active_processes[uid].poll() is not None: 
                    # Se o processo morreu, reinicia
                    print(f"[!] Bot {uid} caiu. Reiniciando...")
                    proc = start_bot_process(uid, bot['discord_token'], bot['category_ids'], bot['response_msg'])
                    active_processes[uid] = proc

            # 2. Para bots que foram desativados
            ids_to_stop = []
            for uid in active_processes:
                if uid not in active_ids:
                    ids_to_stop.append(uid)
            
            for uid in ids_to_stop:
                stop_bot_process(uid)
                
            time.sleep(5) # Verifica a cada 5 segundos
            
        except Exception as e:
            print(f"[ERROR] Manager Loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
