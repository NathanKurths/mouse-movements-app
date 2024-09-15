import tkinter as tk
from tkinter import messagebox, filedialog
import pynput.mouse
import pynput.keyboard
import time
import os
import threading

# Lista para armazenar os movimentos
movements = []

def on_move(x, y):
    if recording:
        movements.append(('move', x, y, time.time() - start_time))

def on_click(x, y, button, pressed):
    if recording and pressed:
        movements.append(('click', x, y, time.time() - start_time))

def start_recording():
    global recording, start_time, mouse_listener
    if recording:
        messagebox.showinfo("Info", "Já está gravando.")
        return

    recording = True
    movements.clear()  # Limpa os movimentos anteriores
    start_time = time.time()
    
    # Cria e inicia o ouvinte do mouse
    mouse_listener = pynput.mouse.Listener(on_move=on_move, on_click=on_click)
    mouse_listener.start()
    
    status_label.config(text="Gravação em andamento...")
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    play_button.config(state=tk.DISABLED)
    stop_play_button.config(state=tk.DISABLED)

def stop_recording():
    global recording, mouse_listener
    if not recording:
        messagebox.showinfo("Info", "Não está gravando.")
        return
    
    recording = False
    mouse_listener.stop()  # Para o ouvinte do mouse

    # Salva os movimentos em um arquivo
    file_name = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="Salvar gravação")
    if file_name:
        with open(file_name, 'w') as f:
            for movement in movements:
                f.write(f'{movement}\n')
        status_label.config(text=f"Gravação salva em {file_name}.")
    else:
        status_label.config(text="Gravação cancelada.")

    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    play_button.config(state=tk.NORMAL)

def start_playback():
    global playing, stop_movement
    if playing:
        messagebox.showinfo("Info", "Já está reproduzindo.")
        return
    
    file_name = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")], title="Abrir gravação")
    if not file_name:
        return
    
    playing = True
    stop_movement = False
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.DISABLED)
    play_button.config(state=tk.DISABLED)
    stop_play_button.config(state=tk.NORMAL)
    
    # Executa a reprodução em uma thread separada
    threading.Thread(target=lambda: playback(file_name)).start()

def stop_playback():
    global playing
    playing = False
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.NORMAL)
    play_button.config(state=tk.NORMAL)
    stop_play_button.config(state=tk.DISABLED)

def playback(file_name):
    global playing, stop_movement
    mouse = pynput.mouse.Controller()
    keyboard_listener = pynput.keyboard.Listener(on_press=on_press)
    keyboard_listener.start()
    
    with open(file_name, 'r') as f:
        movements = [eval(line.strip()) for line in f.readlines()]

    start_time = movements[0][3]
    acceleration_factor = 5  

    for movement in movements:
        if stop_movement:  
            print("Movimentação interrompida.")
            break
        
        action, x, y, timestamp = movement
        delay = (timestamp - start_time) / acceleration_factor
        if delay > 0.01:
            time.sleep(delay)
        start_time = timestamp
        
        if action == 'move':
            mouse.position = (x, y)
        elif action == 'click':
            mouse.click(pynput.mouse.Button.left, 1)

    print("Reprodução finalizada.")
    keyboard_listener.stop()

def on_press(key):
    global stop_movement
    try:
        if key.char == 'q':  
            stop_movement = True
    except AttributeError:
        pass

# Criação da interface gráfica
root = tk.Tk()
root.title("Mouse Recorder")

recording = False
playing = False
stop_movement = False
start_time = 0
mouse_listener = None

# Configuração dos widgets
start_button = tk.Button(root, text="Iniciar Gravação", command=start_recording)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Parar Gravação", command=stop_recording, state=tk.DISABLED)
stop_button.pack(pady=10)

play_button = tk.Button(root, text="Iniciar Reprodução", command=start_playback, state=tk.NORMAL)
play_button.pack(pady=10)

stop_play_button = tk.Button(root, text="Parar Reprodução", command=stop_playback, state=tk.DISABLED)
stop_play_button.pack(pady=10)

status_label = tk.Label(root, text="Clique em 'Iniciar Gravação' para começar.")
status_label.pack(pady=10)

# Executa o loop principal da interface gráfica
root.mainloop()
