import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import json
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import os

class ButceTakipUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("Kişisel Bütçe Takip Uygulaması")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Veritabanı bağlantısı
        self.veritabani_olustur()
        
        # Ana menü
        self.ana_menu_olustur()
        
        # Veri listesi
        self.veri_listesi_olustur()
        
        # İstatistikler
        self.istatistikler_olustur()
        
        # Verileri yükle
        self.verileri_yukle()
    
    def veritabani_olustur(self):
        """Veritabanı ve tabloları oluşturur"""
        self.conn = sqlite3.connect('butce_takip.db')
        self.cursor = self.conn.cursor()
        
        # Gelir tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gelirler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aciklama TEXT NOT NULL,
                miktar REAL NOT NULL,
                kategori TEXT,
                tarih TEXT NOT NULL
            )
        ''')
        
        # Gider tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS giderler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aciklama TEXT NOT NULL,
                miktar REAL NOT NULL,
                kategori TEXT,
                tarih TEXT NOT NULL
            )
        ''')
        
        # Bütçe hedefleri tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS butce_hedefleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kategori TEXT NOT NULL,
                hedef_miktar REAL NOT NULL,
                ay TEXT NOT NULL
            )
        ''')
        
        self.conn.commit()
    
    def ana_menu_olustur(self):
        """Ana menü çerçevesini oluşturur"""
        menu_frame = tk.Frame(self.root, bg='#2c3e50', height=50)
        menu_frame.pack(fill='x', padx=10, pady=5)
        menu_frame.pack_propagate(False)
        
        # Başlık
        baslik = tk.Label(menu_frame, text="💰 Kişisel Bütçe Takip Uygulaması", 
                         font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        baslik.pack(side='left', padx=10, pady=10)
        
        # Butonlar
        buton_frame = tk.Frame(menu_frame, bg='#2c3e50')
        buton_frame.pack(side='right', padx=10, pady=10)
        
        tk.Button(buton_frame, text="➕ Gelir Ekle", command=self.gelir_ekle_pencere,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buton_frame, text="➖ Gider Ekle", command=self.gider_ekle_pencere,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buton_frame, text="📊 Raporlar", command=self.raporlar_pencere,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(buton_frame, text="💾 Yedekle", command=self.yedekle,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
    
    def veri_listesi_olustur(self):
        """Veri listesi çerçevesini oluşturur"""
        liste_frame = tk.Frame(self.root, bg='white')
        liste_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Notebook (sekmeli arayüz)
        self.notebook = ttk.Notebook(liste_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Gelirler sekmesi
        gelir_frame = tk.Frame(self.notebook)
        self.notebook.add(gelir_frame, text="💰 Gelirler")
        
        # Gelir tablosu
        self.gelir_tree = ttk.Treeview(gelir_frame, columns=('Tarih', 'Açıklama', 'Kategori', 'Miktar'), show='headings')
        self.gelir_tree.heading('Tarih', text='Tarih')
        self.gelir_tree.heading('Açıklama', text='Açıklama')
        self.gelir_tree.heading('Kategori', text='Kategori')
        self.gelir_tree.heading('Miktar', text='Miktar (₺)')
        self.gelir_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Giderler sekmesi
        gider_frame = tk.Frame(self.notebook)
        self.notebook.add(gider_frame, text="💸 Giderler")
        
        # Gider tablosu
        self.gider_tree = ttk.Treeview(gider_frame, columns=('Tarih', 'Açıklama', 'Kategori', 'Miktar'), show='headings')
        self.gider_tree.heading('Tarih', text='Tarih')
        self.gider_tree.heading('Açıklama', text='Açıklama')
        self.gider_tree.heading('Kategori', text='Kategori')
        self.gider_tree.heading('Miktar', text='Miktar (₺)')
        self.gider_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    def istatistikler_olustur(self):
        """İstatistikler çerçevesini oluşturur"""
        istatistik_frame = tk.Frame(self.root, bg='#ecf0f1', height=150)
        istatistik_frame.pack(fill='x', padx=10, pady=5)
        istatistik_frame.pack_propagate(False)
        
        # İstatistik etiketleri
        self.toplam_gelir_label = tk.Label(istatistik_frame, text="Toplam Gelir: 0 ₺", 
                                          font=('Arial', 12, 'bold'), fg='#27ae60', bg='#ecf0f1')
        self.toplam_gelir_label.pack(side='left', padx=20, pady=20)
        
        self.toplam_gider_label = tk.Label(istatistik_frame, text="Toplam Gider: 0 ₺", 
                                          font=('Arial', 12, 'bold'), fg='#e74c3c', bg='#ecf0f1')
        self.toplam_gider_label.pack(side='left', padx=20, pady=20)
        
        self.net_durum_label = tk.Label(istatistik_frame, text="Net Durum: 0 ₺", 
                                       font=('Arial', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        self.net_durum_label.pack(side='left', padx=20, pady=20)
    
    def gelir_ekle_pencere(self):
        """Gelir ekleme penceresi"""
        pencere = tk.Toplevel(self.root)
        pencere.title("Gelir Ekle")
        pencere.geometry("400x300")
        pencere.configure(bg='#f0f0f0')
        
        # Form elemanları
        tk.Label(pencere, text="Gelir Ekle", font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=10)
        
        tk.Label(pencere, text="Açıklama:", bg='#f0f0f0').pack(pady=5)
        aciklama_entry = tk.Entry(pencere, width=30)
        aciklama_entry.pack(pady=5)
        
        tk.Label(pencere, text="Miktar (₺):", bg='#f0f0f0').pack(pady=5)
        miktar_entry = tk.Entry(pencere, width=30)
        miktar_entry.pack(pady=5)
        
        tk.Label(pencere, text="Kategori:", bg='#f0f0f0').pack(pady=5)
        kategori_combo = ttk.Combobox(pencere, values=['Maaş', 'Ek İş', 'Yatırım', 'Diğer'])
        kategori_combo.pack(pady=5)
        
        def kaydet():
            try:
                aciklama = aciklama_entry.get()
                miktar = float(miktar_entry.get())
                kategori = kategori_combo.get() or 'Diğer'
                tarih = datetime.now().strftime('%Y-%m-%d')
                
                if not aciklama or miktar <= 0:
                    messagebox.showerror("Hata", "Lütfen geçerli bilgiler girin!")
                    return
                
                self.cursor.execute('''
                    INSERT INTO gelirler (aciklama, miktar, kategori, tarih)
                    VALUES (?, ?, ?, ?)
                ''', (aciklama, miktar, kategori, tarih))
                self.conn.commit()
                
                messagebox.showinfo("Başarılı", "Gelir başarıyla eklendi!")
                self.verileri_yukle()
                pencere.destroy()
                
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli bir miktar girin!")
        
        tk.Button(pencere, text="Kaydet", command=kaydet, bg='#27ae60', fg='white', 
                 font=('Arial', 10, 'bold')).pack(pady=20)
    
    def gider_ekle_pencere(self):
        """Gider ekleme penceresi"""
        pencere = tk.Toplevel(self.root)
        pencere.title("Gider Ekle")
        pencere.geometry("400x300")
        pencere.configure(bg='#f0f0f0')
        
        # Form elemanları
        tk.Label(pencere, text="Gider Ekle", font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=10)
        
        tk.Label(pencere, text="Açıklama:", bg='#f0f0f0').pack(pady=5)
        aciklama_entry = tk.Entry(pencere, width=30)
        aciklama_entry.pack(pady=5)
        
        tk.Label(pencere, text="Miktar (₺):", bg='#f0f0f0').pack(pady=5)
        miktar_entry = tk.Entry(pencere, width=30)
        miktar_entry.pack(pady=5)
        
        tk.Label(pencere, text="Kategori:", bg='#f0f0f0').pack(pady=5)
        kategori_combo = ttk.Combobox(pencere, values=['Gıda', 'Ulaşım', 'Kira', 'Faturalar', 'Eğlence', 'Sağlık', 'Diğer'])
        kategori_combo.pack(pady=5)
        
        def kaydet():
            try:
                aciklama = aciklama_entry.get()
                miktar = float(miktar_entry.get())
                kategori = kategori_combo.get() or 'Diğer'
                tarih = datetime.now().strftime('%Y-%m-%d')
                
                if not aciklama or miktar <= 0:
                    messagebox.showerror("Hata", "Lütfen geçerli bilgiler girin!")
                    return
                
                self.cursor.execute('''
                    INSERT INTO giderler (aciklama, miktar, kategori, tarih)
                    VALUES (?, ?, ?, ?)
                ''', (aciklama, miktar, kategori, tarih))
                self.conn.commit()
                
                messagebox.showinfo("Başarılı", "Gider başarıyla eklendi!")
                self.verileri_yukle()
                pencere.destroy()
                
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli bir miktar girin!")
        
        tk.Button(pencere, text="Kaydet", command=kaydet, bg='#e74c3c', fg='white', 
                 font=('Arial', 10, 'bold')).pack(pady=20)
    
    def raporlar_pencere(self):
        """Raporlar penceresi"""
        pencere = tk.Toplevel(self.root)
        pencere.title("Raporlar")
        pencere.geometry("800x600")
        pencere.configure(bg='#f0f0f0')
        
        # Notebook
        notebook = ttk.Notebook(pencere)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Grafik sekmesi
        grafik_frame = tk.Frame(notebook)
        notebook.add(grafik_frame, text="📊 Grafikler")
        
        # Grafik oluştur
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Gider kategorileri pasta grafiği
        self.cursor.execute('''
            SELECT kategori, SUM(miktar) as toplam
            FROM giderler
            GROUP BY kategori
        ''')
        gider_verileri = self.cursor.fetchall()
        
        if gider_verileri:
            kategoriler = [veri[0] for veri in gider_verileri]
            miktarlar = [veri[1] for veri in gider_verileri]
            
            ax1.pie(miktarlar, labels=kategoriler, autopct='%1.1f%%')
            ax1.set_title('Gider Kategorileri')
        
        # Aylık gelir-gider çubuk grafiği
        self.cursor.execute('''
            SELECT strftime('%Y-%m', tarih) as ay,
                   SUM(CASE WHEN miktar > 0 THEN miktar ELSE 0 END) as gelir,
                   SUM(CASE WHEN miktar < 0 THEN ABS(miktar) ELSE 0 END) as gider
            FROM (
                SELECT tarih, miktar FROM gelirler
                UNION ALL
                SELECT tarih, -miktar FROM giderler
            )
            GROUP BY ay
            ORDER BY ay
        ''')
        aylik_veriler = self.cursor.fetchall()
        
        if aylik_veriler:
            aylar = [veri[0] for veri in aylik_veriler]
            gelirler = [veri[1] for veri in aylik_veriler]
            giderler = [veri[2] for veri in aylik_veriler]
            
            x = range(len(aylar))
            ax2.bar([i-0.2 for i in x], gelirler, width=0.4, label='Gelir', color='green')
            ax2.bar([i+0.2 for i in x], giderler, width=0.4, label='Gider', color='red')
            ax2.set_xlabel('Ay')
            ax2.set_ylabel('Miktar (₺)')
            ax2.set_title('Aylık Gelir-Gider')
            ax2.legend()
            ax2.set_xticks(x)
            ax2.set_xticklabels(aylar, rotation=45)
        
        canvas = FigureCanvasTkAgg(fig, grafik_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def yedekle(self):
        """Verileri yedekler"""
        try:
            dosya_adi = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if dosya_adi:
                # Verileri topla
                self.cursor.execute("SELECT * FROM gelirler")
                gelirler = self.cursor.fetchall()
                
                self.cursor.execute("SELECT * FROM giderler")
                giderler = self.cursor.fetchall()
                
                self.cursor.execute("SELECT * FROM butce_hedefleri")
                hedefler = self.cursor.fetchall()
                
                yedek_veri = {
                    'gelirler': gelirler,
                    'giderler': giderler,
                    'butce_hedefleri': hedefler,
                    'tarih': datetime.now().isoformat()
                }
                
                with open(dosya_adi, 'w', encoding='utf-8') as f:
                    json.dump(yedek_veri, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Başarılı", f"Veriler başarıyla yedeklendi: {dosya_adi}")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Yedekleme hatası: {str(e)}")
    
    def verileri_yukle(self):
        """Verileri listelerde gösterir ve istatistikleri günceller"""
        # Gelirleri yükle
        for item in self.gelir_tree.get_children():
            self.gelir_tree.delete(item)
        
        self.cursor.execute("SELECT tarih, aciklama, kategori, miktar FROM gelirler ORDER BY tarih DESC")
        gelirler = self.cursor.fetchall()
        
        for gelir in gelirler:
            self.gelir_tree.insert('', 'end', values=gelir)
        
        # Giderleri yükle
        for item in self.gider_tree.get_children():
            self.gider_tree.delete(item)
        
        self.cursor.execute("SELECT tarih, aciklama, kategori, miktar FROM giderler ORDER BY tarih DESC")
        giderler = self.cursor.fetchall()
        
        for gider in giderler:
            self.gider_tree.insert('', 'end', values=gider)
        
        # İstatistikleri güncelle
        self.cursor.execute("SELECT SUM(miktar) FROM gelirler")
        toplam_gelir = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute("SELECT SUM(miktar) FROM giderler")
        toplam_gider = self.cursor.fetchone()[0] or 0
        
        net_durum = toplam_gelir - toplam_gider
        
        self.toplam_gelir_label.config(text=f"Toplam Gelir: {toplam_gelir:.2f} ₺")
        self.toplam_gider_label.config(text=f"Toplam Gider: {toplam_gider:.2f} ₺")
        self.net_durum_label.config(text=f"Net Durum: {net_durum:.2f} ₺")

def main():
    root = tk.Tk()
    app = ButceTakipUygulamasi(root)
    root.mainloop()

if __name__ == "__main__":
    main() 