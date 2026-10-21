import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class ConversorCore:
    HISTORICO_FILE = "historico_conversoes.json"

    @staticmethod
    def celsius_para_fahrenheit(celsius):
        return (celsius * 9/5) + 32

    @staticmethod
    def fahrenheit_para_celsius(fahrenheit):
        return (fahrenheit - 32) * 5/9

    @staticmethod
    def metros_para_km(metros):
        return metros / 1000

    @classmethod
    def salvar_no_historico(cls, tipo, de_unidade, para_unidade, valor_original, valor_convertido):
        log = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "tipo": tipo,
            "conversao": f"{valor_original} {de_unidade} ➔ {valor_convertido:.2f} {para_unidade}"
        }
        
        historico = cls.listar_historico()
        historico.append(log)
        
        try:
            with open(cls.HISTORICO_FILE, "w", encoding="utf-8") as f:
                json.dump(historico, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")

    @classmethod
    def listar_historico(cls):
        if not os.path.exists(cls.HISTORICO_FILE):
            return []
        try:
            with open(cls.HISTORICO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []


class ConversorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor Centralizado Empresarial")
        self.root.geometry("600x450")
        self.root.minsize(500, 400)
        
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        
        self.criar_aba_temperatura()
        self.criar_aba_medidas()
        self.criar_aba_historico()
        
        
        self.notebook.bind("<<NotebookTabChanged>>", self.atualizar_aba_historico)

    def criar_aba_temperatura(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text="🌡️ Temperatura")
        
        
        ttk.Label(aba, text="Valor:", font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=15, sticky="w")
        self.entry_temp = ttk.Entry(aba, width=15, font=("Arial", 11))
        self.entry_temp.grid(row=0, column=1, padx=10, pady=15, sticky="w")
        
        self.combo_temp = ttk.Combobox(aba, values=["Celsius para Fahrenheit", "Fahrenheit para Celsius"], state="readonly", width=25)
        self.combo_temp.current(0)
        self.combo_temp.grid(row=0, column=2, padx=10, pady=15)
        
        btn_converter = ttk.Button(aba, text="Converter", command=self.processar_temperatura)
        btn_converter.grid(row=1, column=1, pady=10)
        
        self.lbl_resultado_temp = ttk.Label(aba, text="Resultado: -", font=("Arial", 12, "bold"), foreground="blue")
        self.lbl_resultado_temp.grid(row=2, column=0, columnspan=3, pady=20)

    def processar_temperatura(self):
        try:
            valor = float(self.entry_temp.get())
            opcao = self.combo_temp.get()
            
            if opcao == "Celsius para Fahrenheit":
                res = ConversorCore.celsius_para_fahrenheit(valor)
                ConversorCore.salvar_no_historico("Temperatura", "°C", "°F", valor, res)
                self.lbl_resultado_temp.config(text=f"Resultado: {res:.2f} °F")
            else:
                res = ConversorCore.fahrenheit_para_celsius(valor)
                ConversorCore.salvar_no_historico("Temperatura", "°F", "°C", valor, res)
                self.lbl_resultado_temp.config(text=f"Resultado: {res:.2f} °C")
                
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, digite um número válido.")

    def criar_aba_medidas(self):
        aba = ttk.Frame(self.notebook)
        self.notebook.add(aba, text=" Medidas")
        
        ttk.Label(aba, text="Metros (m):", font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=15)
        self.entry_metros = ttk.Entry(aba, width=15, font=("Arial", 11))
        self.entry_metros.grid(row=0, column=1, padx=10, pady=15)
        
        btn_converter = ttk.Button(aba, text="Converter para Km", command=self.processar_medidas)
        btn_converter.grid(row=0, column=2, padx=10, pady=15)
        
        self.lbl_resultado_medidas = ttk.Label(aba, text="Resultado: -", font=("Arial", 12, "bold"), foreground="green")
        self.lbl_resultado_medidas.grid(row=1, column=0, columnspan=3, pady=20)

    def processar_medidas(self):
        try:
            valor = float(self.entry_metros.get())
            if valor < 0:
                raise ValueError("Medidas lineares não podem ser negativas.")
                
            res = ConversorCore.metros_para_km(valor)
            ConversorCore.salvar_no_historico("Distância", "m", "km", valor, res)
            self.lbl_resultado_medidas.config(text=f"Resultado: {res:.4f} km")
        except ValueError as e:
            msg = str(e) if "negativas" in str(e) else "Por favor, digite uma distância válida."
            messagebox.showerror("Erro de Entrada", msg)

    def criar_aba_historico(self):
        self.aba_hist = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_hist, text=" Histórico")
        
        
        colunas = ("data", "tipo", "conversao")
        self.tree = ttk.Treeview(self.aba_hist, columns=colunas, show="headings")
        self.tree.heading("data", text="Data/Hora")
        self.tree.heading("tipo", text="Tipo de Conversão")
        self.tree.heading("conversao", text="Operação")
        
        self.tree.column("data", width=130)
        self.tree.column("tipo", width=120)
        self.tree.column("conversao", width=250)
        
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

    def atualizar_aba_historico(self, event):
       
        aba_atual = self.notebook.tab(self.notebook.select(), "text")
        if "Histórico" in aba_atual:
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
           
            for item in ConversorCore.listar_historico():
                self.tree.insert("", "end", values=(item["data"], item["tipo"], item["conversao"]))


if __name__ == "__main__":
    root = tk.Tk()
    app = ConversorApp(root)
    root.mainloop()
