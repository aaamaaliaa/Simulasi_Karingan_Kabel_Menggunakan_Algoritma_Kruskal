import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import folium
import webbrowser
import os

class KruskalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Simulasi Jaringan Listrik Tanjung Selor ⚡")
        self.root.configure(bg="#e6f2ff")
        self.edges = []
        self.nodes = set()
        self.coordinates = {}
        self.latest_mst = []
        self.setup_coordinates()
        self.setup_gui()

    def setup_coordinates(self):
        self.coordinates = {
            "Gardu Kantor Bupati": (2.8339, 117.3665),
            "Gardu Bandara Tanjung Harapan": (2.8448, 117.3755),
            "Gardu Jembatan Kayan I": (2.8355, 117.3631),
            "Gardu RSUD dr. H. Soemarno": (2.8372, 117.3679),
            "Gardu Pelabuhan Kayan II": (2.8387, 117.3617)
        }

    def setup_gui(self):
        style = ttk.Style()
        style.configure("TFrame", background="#e6f2ff")
        style.configure("TLabel", background="#e6f2ff", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TCombobox", padding=5)

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Judul aplikasi
        ttk.Label(main_frame, text="⚡ Simulasi Jaringan Listrik Tanjung Selor ⚡",
                  font=("Segoe UI", 14, "bold"), background="#e6f2ff", foreground="#003366")\
            .grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # Pilihan gardu
        ttk.Label(main_frame, text="🔌 Pilih Gardu 1:").grid(row=1, column=0, sticky="w")
        self.combo1 = ttk.Combobox(main_frame, values=list(self.coordinates.keys()), state="readonly", width=35)
        self.combo1.grid(row=2, column=0)

        ttk.Label(main_frame, text="🔌 Pilih Gardu 2:").grid(row=1, column=1, sticky="w")
        self.combo2 = ttk.Combobox(main_frame, values=list(self.coordinates.keys()), state="readonly", width=35)
        self.combo2.grid(row=2, column=1)

        # Input jarak
        ttk.Label(main_frame, text="📏 Masukkan Jarak (meter):").grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.weight_entry = ttk.Entry(main_frame, width=40)
        self.weight_entry.grid(row=4, column=0, columnspan=2, pady=(0, 10))

        # Tombol tambah dan hapus
        ttk.Button(main_frame, text="➕ Tambah Koneksi", command=self.add_edge).grid(row=5, column=0, pady=5, sticky="w")
        ttk.Button(main_frame, text="🗑️ Hapus Semua", command=self.clear_edges).grid(row=5, column=1, pady=5, sticky="e")

        # List koneksi
        ttk.Label(main_frame, text="📡 Daftar Koneksi Gardu:").grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.edge_listbox = tk.Listbox(main_frame, width=70, height=5, bg="#ffffff", fg="#333333", font=("Segoe UI", 9))
        self.edge_listbox.grid(row=7, column=0, columnspan=2, pady=(0, 10))

        # Tombol kruskal dan peta
        ttk.Button(main_frame, text="📊 Jalankan Algoritma Kruskal", command=self.run_kruskal).grid(row=8, column=0, columnspan=2, pady=5)
        ttk.Button(main_frame, text="🗺️ Tampilkan Peta Interaktif", command=self.show_map).grid(row=9, column=0, columnspan=2, pady=(0, 10))

        # Hasil analisis
        ttk.Label(main_frame, text="📈 Hasil Analisis MST:").grid(row=10, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.result_text = tk.Text(main_frame, width=70, height=8, font=("Consolas", 10), bg="#f9f9f9", fg="#333333")
        self.result_text.grid(row=11, column=0, columnspan=2, pady=(0, 10))
        self.result_text.insert(tk.END, "Grafik akan muncul setelah algoritma dijalankan")
        self.result_text.config(state='disabled')

        # Grafik
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().grid(row=12, column=0, columnspan=2, pady=5)

    def add_edge(self):
        node1 = self.combo1.get()
        node2 = self.combo2.get()
        try:
            weight = float(self.weight_entry.get())
            if not node1 or not node2 or node1 == node2:
                raise ValueError("Pilih dua gardu berbeda.")
            if (node1, node2, weight) in self.edges or (node2, node1, weight) in self.edges:
                messagebox.showinfo("Info", "Koneksi sudah ada.")
                return
            self.edges.append((node1, node2, weight))
            self.edge_listbox.insert(tk.END, f"🔗 {node1} - {node2}: {weight:.2f} meter")
            self.weight_entry.delete(0, tk.END)
        except:
            messagebox.showerror("Error", "Masukkan jarak yang valid.")

    def clear_edges(self):
        self.edges.clear()
        self.nodes.clear()
        self.latest_mst.clear()
        self.edge_listbox.delete(0, tk.END)
        self.result_text.config(state='normal')
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "Grafik akan muncul setelah algoritma dijalankan")
        self.result_text.config(state='disabled')
        self.ax.clear()
        self.canvas.draw()

    def find(self, parent, i):
        if parent[i] != i:
            parent[i] = self.find(parent, parent[i])
        return parent[i]

    def union(self, parent, rank, x, y):
        root_x = self.find(parent, x)
        root_y = self.find(parent, y)
        if rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        elif rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        else:
            parent[root_y] = root_x
            rank[root_x] += 1

    def kruskal(self):
        self.nodes = set()
        for u, v, _ in self.edges:
            self.nodes.update([u, v])

        result = []
        self.edges.sort(key=lambda x: x[2])
        parent = {node: node for node in self.nodes}
        rank = {node: 0 for node in self.nodes}

        for u, v, w in self.edges:
            x = self.find(parent, u)
            y = self.find(parent, v)
            if x != y:
                result.append((u, v, w))
                self.union(parent, rank, x, y)
            if len(result) == len(self.nodes) - 1:
                break
        return result

    def run_kruskal(self):
        if not self.edges:
            messagebox.showinfo("Info", "Tambahkan koneksi terlebih dahulu.")
            return

        mst_edges = self.kruskal()
        self.latest_mst = mst_edges
        total_all = sum(w for _, _, w in self.edges)
        total_mst = sum(w for _, _, w in mst_edges)
        efisiensi = 100 * (1 - total_mst / total_all) if total_all else 0

        output = f"Total Semua Koneksi: {total_all:.2f} meter\n"
        output += f"Total Panjang Kabel MST: {total_mst:.2f} meter\n"
        output += f"Efisiensi: {efisiensi:.2f}%\n\n"
        output += "Rute MST:\n"
        output += "\n".join([f"{u} → {v} ({w:.2f} meter)" for u, v, w in mst_edges])

        self.result_text.config(state='normal')
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, output)
        self.result_text.config(state='disabled')

        self.draw_graph(mst_edges)

    def draw_graph(self, mst_edges):
        self.ax.clear()
        G = nx.Graph()
        G.add_nodes_from(self.nodes)
        G.add_weighted_edges_from(self.edges)
        pos = {node: (self.coordinates[node][1], self.coordinates[node][0]) for node in self.nodes}

        nx.draw_networkx_edges(G, pos, edgelist=[(u, v) for u, v, _ in self.edges], edge_color='gray', style='dotted', ax=self.ax)
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v) for u, v, _ in mst_edges], edge_color='red', width=2, ax=self.ax)
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=700, ax=self.ax)
        edge_labels = {(u, v): f"{w:.0f}m" for u, v, w in self.edges}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=self.ax)
        self.ax.set_title("Graf Jaringan Listrik")
        self.canvas.draw()

    def show_map(self):
        if not self.latest_mst:
            messagebox.showinfo("Info", "Jalankan algoritma terlebih dahulu.")
            return

        latitudes = [v[0] for v in self.coordinates.values()]
        longitudes = [v[1] for v in self.coordinates.values()]
        m = folium.Map(location=[sum(latitudes)/len(latitudes), sum(longitudes)/len(longitudes)], zoom_start=15)

        for node, coord in self.coordinates.items():
            folium.Marker(coord, popup=node, icon=folium.Icon(color='blue')).add_to(m)

        for u, v, w in self.edges:
            folium.PolyLine([self.coordinates[u], self.coordinates[v]], color='gray', weight=2).add_to(m)
        for u, v, w in self.latest_mst:
            folium.PolyLine([self.coordinates[u], self.coordinates[v]], color='red', weight=5).add_to(m)

        m.save("tanjung_selor_map.html")
        webbrowser.open(f"file://{os.path.abspath('tanjung_selor_map.html')}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KruskalApp(root)
    root.mainloop()
