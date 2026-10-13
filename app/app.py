import os
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core import Project, additions, files, read


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('APK Lens — cod și modificări între versiuni')
        self.geometry('1280x800')
        self.project = Project(Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'APK Lens' / 'project')
        self.events = queue.Queue()
        self.rows = []
        self.comparison_mode = False
        self.paths = {}
        self.busy = False
        bundled = Path(__file__).resolve().parent / 'tools' / 'jadx' / 'bin' / 'jadx.bat'
        self.jadx = tk.StringVar(value=str(bundled) if bundled.exists() else ('jadx.bat' if os.name == 'nt' else 'jadx'))
        self.query = tk.StringVar()
        self.sort = tk.StringVar(value='Fișier + linie')
        self.only_code = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value='Importă versiunile în ordine cronologică. Selectează veche → nouă pentru comparație.')
        toolbar = ttk.Frame(self, padding=8)
        toolbar.pack(fill='x')
        ttk.Label(toolbar, text='JADX:').pack(side='left')
        ttk.Entry(toolbar, textvariable=self.jadx, width=45).pack(side='left', padx=5)
        ttk.Button(toolbar, text='Alege JADX', command=self.choose_jadx).pack(side='left')
        self.import_button = ttk.Button(toolbar, text='Importă APK', command=self.import_apk)
        self.import_button.pack(side='left', padx=8)
        self.old = ttk.Combobox(toolbar, state='readonly', width=22)
        self.old.pack(side='left')
        ttk.Label(toolbar, text=' → ').pack(side='left')
        self.new = ttk.Combobox(toolbar, state='readonly', width=22)
        self.new.pack(side='left')
        self.compare_button = ttk.Button(toolbar, text='Compară', command=self.compare)
        self.compare_button.pack(side='left', padx=8)
        filters = ttk.Frame(self, padding=8)
        filters.pack(fill='x')
        ttk.Label(filters, text='Filtru cale / cod:').pack(side='left')
        ttk.Entry(filters, textvariable=self.query, width=40).pack(side='left', padx=5)
        ttk.Checkbutton(filters, text='Doar Java / Kotlin', variable=self.only_code, command=self.render).pack(side='left')
        sorter = ttk.Combobox(filters, textvariable=self.sort, state='readonly', values=['Fișier + linie', 'Cele mai multe adăugiri'], width=25)
        sorter.pack(side='left', padx=8)
        sorter.bind('<<ComboboxSelected>>', lambda _: self.render())
        ttk.Button(filters, text='Exportă CSV', command=self.export).pack(side='left')
        self.query.trace_add('write', lambda *_: self.render())
        pane = ttk.Panedwindow(self, orient='horizontal')
        pane.pack(fill='both', expand=True, padx=8)
        self.tree = ttk.Treeview(pane, columns=('line', 'code'), show='tree headings')
        self.tree.heading('#0', text='Fișier')
        self.tree.heading('line', text='Linie')
        self.tree.heading('code', text='Cod adăugat / modificat')
        self.tree.column('#0', width=250)
        self.tree.column('line', width=55, stretch=False)
        self.tree.column('code', width=300)
        self.tree.bind('<<TreeviewSelect>>', self.open_row)
        pane.add(self.tree, weight=1)
        frame = ttk.Frame(pane)
        self.code = tk.Text(frame, wrap='none', font=('Consolas', 11), bg='#16202b', fg='#e0e8ef', insertbackground='white')
        scroll = ttk.Scrollbar(frame, command=self.code.yview)
        horizontal = ttk.Scrollbar(frame, orient='horizontal', command=self.code.xview)
        self.code.configure(yscrollcommand=scroll.set, xscrollcommand=horizontal.set)
        scroll.pack(side='right', fill='y')
        horizontal.pack(side='bottom', fill='x')
        self.code.pack(fill='both', expand=True)
        self.code.tag_configure('added', background='#245a3b')
        self.code.configure(state='disabled')
        pane.add(frame, weight=2)
        ttk.Label(self, textvariable=self.status, padding=8).pack(fill='x')
        self.refresh_versions()
        self.new.bind('<<ComboboxSelected>>', lambda _: self.browse())
        self.after(100, self.poll)

    def choose_jadx(self):
        path = filedialog.askopenfilename(title='Selectează jadx.bat din folderul bin al JADX')
        if path:
            self.jadx.set(path)

    def refresh_versions(self):
        names = [f'{i+1}. {v["label"]}' for i, v in enumerate(self.project.versions)]
        self.old['values'] = self.new['values'] = names
        if names:
            self.new.current(len(names)-1)
            self.old.current(max(0, len(names)-2))
            self.browse()

    def background(self, work, done):
        if self.busy:
            return
        self.busy = True
        self.import_button.configure(state='disabled')
        self.compare_button.configure(state='disabled')
        self.old.configure(state='disabled')
        self.new.configure(state='disabled')
        def run():
            try:
                self.events.put((done, work(), None))
            except Exception as error:
                self.events.put((done, None, str(error)))
        threading.Thread(target=run, daemon=True).start()

    def poll(self):
        try:
            done, result, error = self.events.get_nowait()
            self.busy = False
            self.import_button.configure(state='normal')
            self.compare_button.configure(state='normal')
            self.old.configure(state='readonly')
            self.new.configure(state='readonly')
            if error:
                self.status.set('Operația a eșuat.')
                messagebox.showerror('Eroare', error)
            else:
                done(result)
        except queue.Empty:
            pass
        self.after(100, self.poll)

    def import_apk(self):
        path = filedialog.askopenfilename(filetypes=[('Android APK', '*.apk')])
        if path:
            executable = self.jadx.get()
            self.status.set('Decompilare în curs… poate dura câteva minute.')
            self.background(lambda: self.project.decompile(path, executable, Path(path).stem), lambda _: self.import_done())

    def import_done(self):
        self.refresh_versions()
        self.status.set('APK importat. Selectează două versiuni și apasă Compară.')

    def browse(self):
        if self.new.current() < 0:
            return
        self.current_root = self.project.directory(self.project.versions[self.new.current()])
        self.rows = []
        self.comparison_mode = False
        self.paths = files(self.current_root)
        self.clear_code()
        self.render()

    def compare(self):
        a, b = self.old.current(), self.new.current()
        if a < 0 or b <= a:
            messagebox.showinfo('Versiuni', 'Selectează o versiune veche și una importată ulterior.')
            return
        older = self.project.directory(self.project.versions[a])
        newer = self.project.directory(self.project.versions[b])
        self.status.set('Compar codul decompilat…')
        self.background(lambda: (newer, additions(older, newer)), self.compared)

    def compared(self, result):
        self.current_root, self.rows = result
        self.comparison_mode = True
        self.paths = files(self.current_root)
        self.clear_code()
        self.render()
        self.status.set(f'{len(self.rows)} linii adăugate / modificate. Verde = adăugare față de versiunea selectată; data autorului nu este disponibilă.')

    def filtered(self, name, text=''):
        return (not self.only_code.get() or Path(name).suffix in ('.java', '.kt')) and self.query.get().casefold() in (name + ' ' + text).casefold()

    def render(self):
        self.tree.delete(*self.tree.get_children())
        self.lookup = {}
        counts = {}
        for row in self.rows:
            counts[row.file] = counts.get(row.file, 0) + 1
        rows = [r for r in self.rows if self.filtered(r.file, r.text)]
        rows.sort(key=lambda r: ((-counts[r.file], r.file, r.line) if self.sort.get() == 'Cele mai multe adăugiri' else (r.file, r.line)))
        if self.comparison_mode:
            for row in rows:
                item = self.tree.insert('', 'end', text=row.file, values=(row.line, row.text))
                self.lookup[item] = (row.file, row.line)
        else:
            for name in sorted(self.paths):
                if self.filtered(name, read(self.paths[name]) if self.query.get() else ''):
                    item = self.tree.insert('', 'end', text=name)
                    self.lookup[item] = (name, 1)

    def clear_code(self):
        self.code.configure(state='normal')
        self.code.delete('1.0', 'end')
        self.code.configure(state='disabled')

    def open_row(self, _):
        selection = self.tree.selection()
        if not selection:
            return
        name, line = self.lookup[selection[0]]
        source = read(self.paths[name]).splitlines()
        self.code.configure(state='normal')
        self.code.delete('1.0', 'end')
        self.code.insert('1.0', '\n'.join(f'{i:5}  {text}' for i, text in enumerate(source, 1)))
        for row in self.rows:
            if row.file == name:
                self.code.tag_add('added', f'{row.line}.0', f'{row.line}.end')
        self.code.see(f'{line}.0')
        self.code.configure(state='disabled')

    def export(self):
        import csv
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if path:
            with open(path, 'w', encoding='utf-8-sig', newline='') as target:
                writer = csv.writer(target)
                writer.writerow(['file', 'line', 'code'])
                for item in self.tree.get_children():
                    name, line = self.lookup[item]
                    source = read(self.paths[name]).splitlines()
                    writer.writerow([name, line, source[line-1] if source else ''])


if __name__ == '__main__':
    App().mainloop()
