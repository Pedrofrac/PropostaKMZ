import tkinter as tk
import subprocess

def abrir_propostas():
    subprocess.Popen(['python', 'propostas.py'])

def abrir_clientes():
    subprocess.Popen(['python', 'clientes.py'])

# Criação da janela principal
root = tk.Tk()
root.title("Interface de Navegação")
root.geometry("400x200")  # Define o tamanho da janela (largura x altura)

# Botão para abrir clientes.py
btn_clientes = tk.Button(root, text="Abrir Clientes", command=abrir_clientes)
btn_clientes.pack(pady=20)  # Aumenta o espaço entre o botão e a borda da janela

# Botão para abrir propostas.py
btn_propostas = tk.Button(root, text="Abrir Propostas", command=abrir_propostas)
btn_propostas.pack(pady=20)  # Aumenta o espaço entre o botão e a borda da janela

# Inicia a interface
root.mainloop()
