import tkinter as tk
from tkinter import filedialog, messagebox, font
import os
import webbrowser
import tempfile

class EditeurHTML:
    def __init__(self, root):
        self.root = root
        self.root.title("Éditeur HTML")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f0ede8")

        self.fichier_actuel = None
        self.modifie = False

        self._construire_interface()
        self._raccourcis()

    def _construire_interface(self):
        # ── Barre d'outils ──
        barre = tk.Frame(self.root, bg="#2c2c2c", pady=6)
        barre.pack(fill="x")

        style_btn = dict(bg="#444", fg="white", relief="flat", padx=12, pady=4,
                         font=("Segoe UI", 9), cursor="hand2", activebackground="#555", activeforeground="white")

        tk.Button(barre, text="📂 Ouvrir", command=self.ouvrir, **style_btn).pack(side="left", padx=4)
        tk.Button(barre, text="💾 Enregistrer", command=self.enregistrer, **style_btn).pack(side="left", padx=4)
        tk.Button(barre, text="💾 Enregistrer sous…", command=self.enregistrer_sous, **style_btn).pack(side="left", padx=4)
        tk.Button(barre, text="🌐 Prévisualiser", command=self.previsualiser, **style_btn).pack(side="left", padx=4)

        self.label_fichier = tk.Label(barre, text="Aucun fichier ouvert", bg="#2c2c2c",
                                      fg="#aaa", font=("Segoe UI", 9))
        self.label_fichier.pack(side="left", padx=16)

        # ── Rechercher / Remplacer ──
        barre2 = tk.Frame(self.root, bg="#e8e4de", pady=5)
        barre2.pack(fill="x")

        tk.Label(barre2, text="Rechercher :", bg="#e8e4de", font=("Segoe UI", 9)).pack(side="left", padx=(10, 4))
        self.champ_recherche = tk.Entry(barre2, width=28, font=("Segoe UI", 9))
        self.champ_recherche.pack(side="left", padx=4)

        tk.Label(barre2, text="Remplacer par :", bg="#e8e4de", font=("Segoe UI", 9)).pack(side="left", padx=(10, 4))
        self.champ_remplacer = tk.Entry(barre2, width=28, font=("Segoe UI", 9))
        self.champ_remplacer.pack(side="left", padx=4)

        style_btn2 = dict(bg="#c0392b", fg="white", relief="flat", padx=10, pady=2,
                          font=("Segoe UI", 9), cursor="hand2", activebackground="#a82d22", activeforeground="white")
        tk.Button(barre2, text="Suivant", command=self.chercher_suivant, **style_btn2).pack(side="left", padx=4)
        tk.Button(barre2, text="Remplacer", command=self.remplacer_un, **style_btn2).pack(side="left", padx=4)
        tk.Button(barre2, text="Tout remplacer", command=self.remplacer_tout, **style_btn2).pack(side="left", padx=4)

        self.label_resultat = tk.Label(barre2, text="", bg="#e8e4de", fg="#666", font=("Segoe UI", 9))
        self.label_resultat.pack(side="left", padx=10)

        # ── Zone de texte ──
        cadre_texte = tk.Frame(self.root, bg="#f0ede8")
        cadre_texte.pack(fill="both", expand=True, padx=0, pady=0)

        # Numéros de lignes
        self.numeros = tk.Text(cadre_texte, width=5, bg="#e0dbd4", fg="#888",
                               font=("Consolas", 11), state="disabled",
                               relief="flat", padx=6, pady=4, cursor="arrow")
        self.numeros.pack(side="left", fill="y")

        scrollbar = tk.Scrollbar(cadre_texte)
        scrollbar.pack(side="right", fill="y")

        self.texte = tk.Text(cadre_texte, font=("Consolas", 11), bg="white", fg="#1a1510",
                             relief="flat", padx=10, pady=4, undo=True,
                             yscrollcommand=self._scroll_sync, wrap="none",
                             insertbackground="#c0392b", selectbackground="#f9ece9",
                             selectforeground="#1a1510")
        self.texte.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self._scroll_both)

        # Scrollbar horizontale
        scrollbar_h = tk.Scrollbar(self.root, orient="horizontal", command=self.texte.xview)
        scrollbar_h.pack(fill="x")
        self.texte.config(xscrollcommand=scrollbar_h.set)

        # Barre de statut
        self.statut = tk.Label(self.root, text="Prêt", bg="#2c2c2c", fg="#aaa",
                               font=("Segoe UI", 8), anchor="w", padx=10)
        self.statut.pack(fill="x", side="bottom")

        # Événements
        self.texte.bind("<<Modified>>", self._on_modifie)
        self.texte.bind("<KeyRelease>", self._maj_numeros)
        self.texte.bind("<MouseWheel>", self._maj_numeros)
        self.champ_recherche.bind("<Return>", lambda e: self.chercher_suivant())
        self.root.protocol("WM_DELETE_WINDOW", self._quitter)

        self._maj_numeros()

    def _scroll_sync(self, *args):
        self.numeros.yview_moveto(args[0])
        # scrollbar sera appelée via yscrollcommand normal

    def _scroll_both(self, *args):
        self.texte.yview(*args)
        self.numeros.yview(*args)

    def _raccourcis(self):
        self.root.bind("<Control-o>", lambda e: self.ouvrir())
        self.root.bind("<Control-s>", lambda e: self.enregistrer())
        self.root.bind("<Control-z>", lambda e: self.texte.edit_undo())
        self.root.bind("<Control-y>", lambda e: self.texte.edit_redo())
        self.root.bind("<Control-f>", lambda e: self.champ_recherche.focus())

    def _on_modifie(self, event=None):
        if self.texte.edit_modified():
            self.modifie = True
            titre = f"● {os.path.basename(self.fichier_actuel)}" if self.fichier_actuel else "● Sans titre"
            self.root.title(f"{titre} — Éditeur HTML")
            self.texte.edit_modified(False)

    def _maj_numeros(self, event=None):
        self.numeros.config(state="normal")
        self.numeros.delete("1.0", "end")
        nb_lignes = int(self.texte.index("end-1c").split(".")[0])
        self.numeros.insert("1.0", "\n".join(str(i) for i in range(1, nb_lignes + 1)))
        self.numeros.config(state="disabled")
        self.statut.config(text=f"Lignes : {nb_lignes}  |  Fichier : {self.fichier_actuel or 'non enregistré'}")

    def ouvrir(self):
        if self.modifie and not self._confirmer_abandon():
            return
        chemin = filedialog.askopenfilename(
            title="Ouvrir un fichier HTML",
            filetypes=[("Fichiers HTML", "*.html *.htm"), ("Tous les fichiers", "*.*")]
        )
        if not chemin:
            return
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()
        self.texte.delete("1.0", "end")
        self.texte.insert("1.0", contenu)
        self.fichier_actuel = chemin
        self.modifie = False
        self.root.title(f"{os.path.basename(chemin)} — Éditeur HTML")
        self.label_fichier.config(text=os.path.basename(chemin), fg="white")
        self._maj_numeros()

    def enregistrer(self):
        if not self.fichier_actuel:
            self.enregistrer_sous()
            return
        self._sauvegarder(self.fichier_actuel)

    def enregistrer_sous(self):
        chemin = filedialog.asksaveasfilename(
            title="Enregistrer sous…",
            defaultextension=".html",
            filetypes=[("Fichiers HTML", "*.html"), ("Tous les fichiers", "*.*")]
        )
        if not chemin:
            return
        self._sauvegarder(chemin)
        self.fichier_actuel = chemin
        self.label_fichier.config(text=os.path.basename(chemin), fg="white")

    def _sauvegarder(self, chemin):
        contenu = self.texte.get("1.0", "end-1c")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
        self.modifie = False
        self.root.title(f"{os.path.basename(chemin)} — Éditeur HTML")
        self.statut.config(text=f"✓ Enregistré : {chemin}")

    def previsualiser(self):
        contenu = self.texte.get("1.0", "end-1c")
        tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
        tmp.write(contenu)
        tmp.close()
        webbrowser.open(f"file:///{tmp.name}")

    def chercher_suivant(self):
        terme = self.champ_recherche.get()
        if not terme:
            return
        self.texte.tag_remove("trouve", "1.0", "end")
        self.texte.tag_config("trouve", background="#fff3b0")
        start = self.texte.search(terme, "insert+1c", "end", nocase=True)
        if not start:
            start = self.texte.search(terme, "1.0", "end", nocase=True)
        if start:
            end = f"{start}+{len(terme)}c"
            self.texte.tag_add("trouve", start, end)
            self.texte.mark_set("insert", end)
            self.texte.see(start)
            self.label_resultat.config(text="✓ Trouvé", fg="#2ecc71")
        else:
            self.label_resultat.config(text="Introuvable", fg="#e74c3c")

    def remplacer_un(self):
        terme = self.champ_recherche.get()
        remplacement = self.champ_remplacer.get()
        if not terme:
            return
        start = self.texte.search(terme, "insert", "end", nocase=True)
        if not start:
            start = self.texte.search(terme, "1.0", "end", nocase=True)
        if start:
            end = f"{start}+{len(terme)}c"
            self.texte.delete(start, end)
            self.texte.insert(start, remplacement)
            self.texte.mark_set("insert", f"{start}+{len(remplacement)}c")
            self.label_resultat.config(text="✓ Remplacé", fg="#2ecc71")
        else:
            self.label_resultat.config(text="Introuvable", fg="#e74c3c")

    def remplacer_tout(self):
        terme = self.champ_recherche.get()
        remplacement = self.champ_remplacer.get()
        if not terme:
            return
        contenu = self.texte.get("1.0", "end-1c")
        nb = contenu.lower().count(terme.lower())
        if nb == 0:
            self.label_resultat.config(text="Introuvable", fg="#e74c3c")
            return
        import re
        nouveau = re.sub(re.escape(terme), remplacement, contenu, flags=re.IGNORECASE)
        self.texte.delete("1.0", "end")
        self.texte.insert("1.0", nouveau)
        self.label_resultat.config(text=f"✓ {nb} remplacement(s)", fg="#2ecc71")
        self._maj_numeros()

    def _confirmer_abandon(self):
        return messagebox.askyesno("Modifications non enregistrées",
                                   "Des modifications non enregistrées seront perdues. Continuer ?")

    def _quitter(self):
        if self.modifie and not self._confirmer_abandon():
            return
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = EditeurHTML(root)
    root.mainloop()
