import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import uuid

from database_manager import DatabaseManager

class ReceitAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ReceitAÍ Caderno de Receitas Inteligente")
        self.root.geometry("1000x700")

        self.db_manager = DatabaseManager()

        self.style = ttk.Style() 

        # Simulates Firebase configuration and authentication (Beacause i might try to use it in the future)
        self.app_id = globals().get('__app_id', 'default-app-id')
        self.firebase_config = json.loads(globals().get('__firebase_config', '{}'))
        self.user_id = None 

        self._initialize_firebase()
        
        self._create_notebook()

        
        self.style.theme_use('clam') # 'clam' is a good default theme for ttk, less frontend stuff for me
        
        self.root.config(bg=self.style.lookup('TFrame', 'background', default='SystemButtonFace')) 
        
        # I had lots of trouble with the colors, so I set them all to black and white forcibly
        self.style.configure('TEntry', fieldbackground='white', foreground='black')
        self.style.configure('TCombobox', fieldbackground='white', foreground='black')
        self.style.configure('TLabel', foreground='black')
        self.style.configure('Treeview', foreground='black') 
        self.style.configure('Treeview.Heading', foreground='black') 


    def _initialize_firebase(self): # This took so long i made the Ai make some DEBUG messages for me. I will leave them in portuguese
        """
        Firebase initialization simulation.
        In a real application, this would connect to Firebase and authenticate the user. (Part of the API would enter here)
        """
        print("Inicializando Firebase (simulado)...")
        initial_auth_token = globals().get('__initial_auth_token', None)

        if initial_auth_token:
            self.user_id = str(uuid.uuid4())
            print(f"Usuário autenticado (simulado via token): {self.user_id}")
        else:
            self.user_id = str(uuid.uuid4()) #simulates an anonymous user
            print(f"Usuário anônimo (simulado): {self.user_id}")
        
        print(f"App ID: {self.app_id}")
        print(f"Firebase Config: {self.firebase_config}")

    def _create_notebook(self):
        """Creates the main notebook with tabs for recipe registration, search, and logs."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(padx=10, pady=10, fill="both", expand=True)

        self._create_recipe_registration_tab()
        self._create_recipe_search_tab()
        self._create_logs_tab()

    def _create_recipe_registration_tab(self):
        """New recipe tab here."""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Cadastrar Receita")

        # Rows and columns configuration
        frame.columnconfigure(1, weight=1)
        for i in range(8):
            frame.rowconfigure(i, weight=1)

        # Receipe Name camp
        ttk.Label(frame, text="Nome da Receita:").grid(row=0, column=0, sticky="w", pady=5)
        self.recipe_name_entry = ttk.Entry(frame)
        self.recipe_name_entry.grid(row=0, column=1, sticky="ew", pady=5)

        # Time of Preparation amp
        ttk.Label(frame, text="Tempo de Preparo (min):").grid(row=1, column=0, sticky="w", pady=5)
        self.prep_time_entry = ttk.Entry(frame)
        self.prep_time_entry.grid(row=1, column=1, sticky="ew", pady=5)

        # Dificulty camp
        ttk.Label(frame, text="Dificuldade:").grid(row=2, column=0, sticky="w", pady=5)
        self.difficulty_combobox = ttk.Combobox(frame, values=["Fácil", "Médio", "Difícil"])
        self.difficulty_combobox.grid(row=2, column=1, sticky="ew", pady=5)
        self.difficulty_combobox.set("Médio") # Valor padrão

        # Categories camp
        ttk.Label(frame, text="Categoria:").grid(row=3, column=0, sticky="w", pady=5)
        self.category_entry = ttk.Entry(frame)
        self.category_entry.grid(row=3, column=1, sticky="ew", pady=5)

        # Tags camp
        # Tags are optional, so we don't set a default value (they don't have an impact in this version of the app)

        ttk.Label(frame, text="Tags (separadas por vírgula):").grid(row=4, column=0, sticky="w", pady=5)
        self.tags_entry = ttk.Entry(frame)
        self.tags_entry.grid(row=4, column=1, sticky="ew", pady=5)

        # Ingredients
        ttk.Label(frame, text="Ingredientes um por linha Exemplo -->\nIndique 'unidades' 'medida' 'de' 'ingrediente' \n   2 unidades de ovos \n   1 colher de farinha \n   300 mg de leite ").grid(row=5, column=0, sticky="nw", pady=5)
        self.ingredients_text = scrolledtext.ScrolledText(frame, height=8, wrap=tk.WORD)
        self.ingredients_text.grid(row=5, column=1, sticky="nsew", pady=5)

        # Preparation Instructions
        ttk.Label(frame, text="Modo de Preparo:").grid(row=6, column=0, sticky="nw", pady=5)
        self.instructions_text = scrolledtext.ScrolledText(frame, height=10, wrap=tk.WORD)
        self.instructions_text.grid(row=6, column=1, sticky="nsew", pady=5)

        # Save button
        ttk.Button(frame, text="Salvar Receita", command=self._save_recipe).grid(row=7, column=0, columnspan=2, pady=10)

    def _save_recipe(self):
        """This will save the recipe to the database.""" # I used strip to remove user input errors
        name = self.recipe_name_entry.get().strip()
        prep_time_str = self.prep_time_entry.get().strip()
        difficulty = self.difficulty_combobox.get().strip()
        category = self.category_entry.get().strip()
        tags = self.tags_entry.get().strip()
        instructions = self.instructions_text.get("1.0", tk.END).strip()
        ingredients_raw = self.ingredients_text.get("1.0", tk.END).strip()

        print(f"DEBUG _save_recipe: Nome da receita capturado: '{name}'") # Debug messages written by Ai in some other parts too

        if not name or not instructions or not ingredients_raw:
            messagebox.showwarning("Campos Faltando", "Nome da receita, ingredientes e modo de preparo são obrigatórios.")
            return

        prep_time = None
        if prep_time_str:
            try:
                prep_time = int(prep_time_str)
            except ValueError:
                messagebox.showwarning("Entrada Inválida", "Tempo de preparo deve ser um número inteiro.")
                return

        ingredients_list = []
        for line in ingredients_raw.split('\n'):
            line = line.strip()
            if not line:
                continue

            # I hope the user will write the ingredients in the format "quantidade unidade de ingrediente" 1 colher de açúcar, 2 ovos, etc.
            parts = line.split(' de ', 1)
            if len(parts) == 2:
                qty_unit = parts[0].strip()
                ingredient_name = parts[1].strip() # Here is where the ingredient name is stored
                
                # This splits the quantity and unit, if they exist
                # For example, "1 colher de sopa" will be split into "1 colher"
                qty_parts = qty_unit.split(' ', 1)
                quantity = qty_parts[0].strip() if qty_parts else ''
                unit = qty_parts[1].strip() if len(qty_parts) > 1 else ''
            else:
                quantity = ''
                unit = ''
                ingredient_name = line # If the line doesn't contain "de", we assume it's just the ingredient name

            ingredients_list.append({'name': ingredient_name, 'quantity': quantity, 'unit': unit}) # Here we create a dictionary for each ingredient with its name, quantity and unit
        
        if self.db_manager.add_recipe(name, prep_time, difficulty, category, instructions, tags, ingredients_list):
            messagebox.showinfo("Sucesso", "Receita cadastrada com sucesso!")
            self._clear_recipe_form()
            self._refresh_recipe_search_results() # Refresh the search results after adding a new recipe
        else:
            messagebox.showerror("Erro", "Erro ao cadastrar receita. Verifique o console para mais detalhes.")

    def _clear_recipe_form(self):
        """After saving a recipe, this will clear the form fields."""
        self.recipe_name_entry.delete(0, tk.END)
        self.prep_time_entry.delete(0, tk.END)
        self.difficulty_combobox.set("Médio")
        self.category_entry.delete(0, tk.END)
        self.tags_entry.delete(0, tk.END)
        self.ingredients_text.delete("1.0", tk.END)
        self.instructions_text.delete("1.0", tk.END)

    def _create_recipe_search_tab(self):
        """Recipe search tab here."""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Buscar Receitas")

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1) # This treeview took long, but works now

        # Search Filters
        ttk.Label(frame, text="Ingredientes (separados por vírgula):").grid(row=0, column=0, sticky="w", pady=5)
        self.search_ingredients_entry = ttk.Entry(frame)
        self.search_ingredients_entry.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Tempo Máximo (min):").grid(row=1, column=0, sticky="w", pady=5)
        self.search_prep_time_entry = ttk.Entry(frame)
        self.search_prep_time_entry.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Categoria:").grid(row=2, column=0, sticky="w", pady=5)
        self.search_category_entry = ttk.Entry(frame)
        self.search_category_entry.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Dificuldade:").grid(row=3, column=0, sticky="w", pady=5)
        self.search_difficulty_combobox = ttk.Combobox(frame, values=["", "Fácil", "Médio", "Difícil"])
        self.search_difficulty_combobox.grid(row=3, column=1, sticky="ew", pady=5)
        self.search_difficulty_combobox.set("") # Default value is empty, meaning no filter. Everything shows up

        ttk.Button(frame, text="Buscar", command=self._perform_recipe_search).grid(row=4, column=0, columnspan=2, pady=10)

        # Search Results Treeview
        self.recipe_results_tree = ttk.Treeview(frame, columns=("Nome", "Tempo", "Dificuldade", "Categoria"), show="headings")
        self.recipe_results_tree.heading("Nome", text="Nome")
        self.recipe_results_tree.heading("Tempo", text="Tempo (min)")
        self.recipe_results_tree.heading("Dificuldade", text="Dificuldade")
        self.recipe_results_tree.heading("Categoria", text="Categoria")
        
        # Setting the column widths and alignment (Should work in most viewports)
        self.recipe_results_tree.column("Nome", width=250, anchor="w")
        self.recipe_results_tree.column("Tempo", width=80, anchor="center")
        self.recipe_results_tree.column("Dificuldade", width=100, anchor="center")
        self.recipe_results_tree.column("Categoria", width=150, anchor="w")


        self.recipe_results_tree.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=10)
        
        # Scrollbar for Treeview (Thanks to the Ai for this one, I was having trouble with it)
        tree_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.recipe_results_tree.yview)
        tree_scrollbar.grid(row=5, column=2, sticky="ns")
        self.recipe_results_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.recipe_results_tree.bind("<Double-1>", self._show_recipe_details)
        
        ttk.Button(frame, text="Ver Detalhes da Receita", command=self._show_recipe_details).grid(row=6, column=0, columnspan=2, pady=5)

        self._refresh_recipe_search_results() # Show all recipes initially

    def _perform_recipe_search(self):
        """Performs the recipe search based on the filters provided by the user."""
        ingredients = self.search_ingredients_entry.get().strip()
        max_prep_time = self.search_prep_time_entry.get().strip()
        category = self.search_category_entry.get().strip()
        difficulty = self.search_difficulty_combobox.get().strip()

        filtered_recipes = self.db_manager.filter_recipes(ingredients, max_prep_time, category, difficulty)
        self._display_recipe_results(filtered_recipes)
        
        search_description = f"Ingredientes: {ingredients}, Tempo Máx: {max_prep_time}, Categoria: {category}, Dificuldade: {difficulty}"
        self.db_manager.log_action("Busca de Receita", search_description)


    def _refresh_recipe_search_results(self):
        """Refreshes the recipe search results by fetching all recipes from the database."""
        all_recipes = self.db_manager.get_all_recipes()
        self._display_recipe_results(all_recipes)

    def _display_recipe_results(self, recipes):
        """Cleans the Treeview and displays the search results."""
        for item in self.recipe_results_tree.get_children():
            self.recipe_results_tree.delete(item)

        for recipe in recipes:
            # More debug messages to help me understand the flow
            print(f"DEBUG _display_recipe_results: Inserindo '{recipe['name']}' na Treeview para recipe_id={recipe['recipe_id']}.")
            self.recipe_results_tree.insert("", tk.END, iid=recipe['recipe_id'],
                                           values=(recipe['name'], recipe['prep_time'], recipe['difficulty'], recipe['category']))

    def _show_recipe_details(self, event=None):
        """Shows the details of the selected recipe in a new window for editing.""" # Update implemented
        selected_item = self.recipe_results_tree.selection()
        print(f"DEBUG _show_recipe_details: Itens selecionados na Treeview: {selected_item}")

        if not selected_item:
            messagebox.showwarning("Nenhuma Receita Selecionada", "Por favor, selecione uma receita na lista para ver os detalhes.")
            return

        recipe_id = int(selected_item[0]) 
        print(f"DEBUG _show_recipe_details: ID da receita selecionada: {recipe_id}")
        
        all_recipes = self.db_manager.get_all_recipes()
        selected_recipe = next((r for r in all_recipes if r['recipe_id'] == recipe_id), None)
        print(f"DEBUG _show_recipe_details: Receita encontrada no banco de dados: {selected_recipe}")


        if selected_recipe:
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Editar Receita: {selected_recipe['name']}")
            details_window.geometry("600x600") # Setting a fixed size for the details window
            details_window.transient(self.root)
            details_window.grab_set()

            details_frame = ttk.Frame(details_window, padding="10", style='TFrame') 
            details_frame.pack(fill="both", expand=True)
            details_window.config(bg=self.style.lookup('TFrame', 'background', default='SystemButtonFace'))

            details_frame.columnconfigure(1, weight=1)
            details_frame.rowconfigure(5, weight=1) # Instructions row
            details_frame.rowconfigure(4, weight=1) # Ingredients row
            # Setting the background color for the Entry widgets, they need to be set manually
            default_entry_bg = self.style.lookup('TEntry', 'fieldbackground', default='white')
            default_entry_fg = self.style.lookup('TEntry', 'foreground', default='black')
            
            # This is the details form, where the user can edit the recipe
            ttk.Label(details_frame, text="Nome:", style='TLabel').grid(row=0, column=0, sticky="w", pady=2)
            self.edit_name_entry = ttk.Entry(details_frame, style='TEntry')
            self.edit_name_entry.grid(row=0, column=1, sticky="ew", pady=2)
            self.edit_name_entry.insert(0, selected_recipe['name'])

            ttk.Label(details_frame, text="Tempo de Preparo (min):", style='TLabel').grid(row=1, column=0, sticky="w", pady=2)
            self.edit_prep_time_entry = ttk.Entry(details_frame, style='TEntry')
            self.edit_prep_time_entry.grid(row=1, column=1, sticky="ew", pady=2)
            self.edit_prep_time_entry.insert(0, str(selected_recipe['prep_time']) if selected_recipe['prep_time'] else "")

            ttk.Label(details_frame, text="Dificuldade:", style='TLabel').grid(row=2, column=0, sticky="w", pady=2)
            self.edit_difficulty_combobox = ttk.Combobox(details_frame, values=["Fácil", "Médio", "Difícil"], style='TCombobox')
            self.edit_difficulty_combobox.grid(row=2, column=1, sticky="ew", pady=2)
            self.edit_difficulty_combobox.set(selected_recipe['difficulty'])

            ttk.Label(details_frame, text="Categoria:", style='TLabel').grid(row=3, column=0, sticky="w", pady=2)
            self.edit_category_entry = ttk.Entry(details_frame, style='TEntry')
            self.edit_category_entry.grid(row=3, column=1, sticky="ew", pady=2)
            self.edit_category_entry.insert(0, selected_recipe['category'])

            ttk.Label(details_frame, text="Tags (separadas por vírgula):", style='TLabel').grid(row=4, column=0, sticky="w", pady=2)
            self.edit_tags_entry = ttk.Entry(details_frame, style='TEntry')
            self.edit_tags_entry.grid(row=4, column=1, sticky="ew", pady=2)
            self.edit_tags_entry.insert(0, selected_recipe['tags'])
            # Ingredients and Instructions text areas --> took way more time then expected to implement
            ttk.Label(details_frame, text="Ingredientes (um por linha):", style='TLabel').grid(row=5, column=0, sticky="nw", pady=2)
            self.edit_ingredients_text = scrolledtext.ScrolledText(details_frame, height=8, wrap=tk.WORD, bg=default_entry_bg, fg=default_entry_fg)
            self.edit_ingredients_text.grid(row=5, column=1, sticky="nsew", pady=2)
            self.edit_ingredients_text.insert(tk.END, "\n".join(selected_recipe['ingredients']))

            ttk.Label(details_frame, text="Modo de Preparo:", style='TLabel').grid(row=6, column=0, sticky="nw", pady=2)
            self.edit_instructions_text = scrolledtext.ScrolledText(details_frame, height=10, wrap=tk.WORD, bg=default_entry_bg, fg=default_entry_fg)
            self.edit_instructions_text.grid(row=6, column=1, sticky="nsew", pady=2)
            self.edit_instructions_text.insert(tk.END, selected_recipe['instructions'])

            # Buttons for saving or canceling the edit
            button_frame = ttk.Frame(details_window, style='TFrame')
            button_frame.pack(pady=10)

            ttk.Button(button_frame, text="Salvar Alterações", command=lambda: self._save_edited_recipe(recipe_id, details_window)).pack(side=tk.LEFT, padx=5)
            # This button will delete the recipe, but only after confirmation
            ttk.Button(button_frame, text="Excluir Receita", command=lambda: self._delete_recipe(recipe_id, details_window)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancelar", command=details_window.destroy).pack(side=tk.LEFT, padx=5)

            self.db_manager.log_action("Ver Detalhes da Receita", f"ID: {recipe_id}, Nome: {selected_recipe['name']}")
        else:
            messagebox.showerror("Erro", "Não foi possível carregar os detalhes da receita.")

    def _save_edited_recipe(self, recipe_id, details_window):
        """Saves the edited recipe details to the database.""" # Strip used again
        name = self.edit_name_entry.get().strip()
        prep_time_str = self.edit_prep_time_entry.get().strip()
        difficulty = self.edit_difficulty_combobox.get().strip()
        category = self.edit_category_entry.get().strip()
        tags = self.edit_tags_entry.get().strip()
        instructions = self.edit_instructions_text.get("1.0", tk.END).strip()
        ingredients_raw = self.edit_ingredients_text.get("1.0", tk.END).strip()

        if not name or not instructions or not ingredients_raw:
            messagebox.showwarning("Campos Faltando", "Nome da receita, ingredientes e modo de preparo são obrigatórios.")
            return

        prep_time = None
        if prep_time_str:
            try:
                prep_time = int(prep_time_str)
            except ValueError:
                messagebox.showwarning("Entrada Inválida", "Tempo de preparo deve ser um número inteiro.")
                return
        
        ingredients_list = [] # This is the same thing from up there. 1 colher de açúcar.
        for line in ingredients_raw.split('\n'):
            line = line.strip()
            if not line:
                continue

            parts = line.split(' de ', 1)
            if len(parts) == 2:
                qty_unit = parts[0].strip()
                ingredient_name = parts[1].strip()
                qty_parts = qty_unit.split(' ', 1)
                quantity = qty_parts[0].strip() if qty_parts else ''
                unit = qty_parts[1].strip() if len(qty_parts) > 1 else ''
            else:
                quantity = ''
                unit = ''
                ingredient_name = line

            ingredients_list.append({'name': ingredient_name, 'quantity': quantity, 'unit': unit})

        if self.db_manager.update_recipe(recipe_id, name, prep_time, difficulty, category, instructions, tags, ingredients_list):
            messagebox.showinfo("Sucesso", "Receita atualizada com sucesso!")
            details_window.destroy() # Fucking destroys the details window after saving
            self._refresh_recipe_search_results() # Refresh the search results after updating a recipe
        else:
            messagebox.showerror("Erro", "Erro ao atualizar receita. Verifique o console para mais detalhes.")

    def _delete_recipe(self, recipe_id, details_window):
        """Deletes the selected recipe after confirmation."""
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir esta receita? Ela parece tão gostosa..."):
            if self.db_manager.delete_recipe(recipe_id):
                messagebox.showinfo("Sucesso", "Receita excluída com sucesso! Você não vai mais poder fazer essa delícia...")
                details_window.destroy() # Fucking destroys the details window after saving
                self._refresh_recipe_search_results() # Refresh the search results after deleting a recipe
            else:
                messagebox.showerror("Erro", "Ocorreu um erro ao excluir a receita.")


    def _create_logs_tab(self):
        """Logs tab here."""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Logs do Usuário")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.logs_tree = ttk.Treeview(frame, columns=("Timestamp", "Tipo de Ação", "Descrição"), show="headings")
        self.logs_tree.heading("Timestamp", text="Carimbo de Data/Hora")
        self.logs_tree.heading("Tipo de Ação", text="Tipo de Ação")
        self.logs_tree.heading("Descrição", text="Descrição")

        self.logs_tree.column("Timestamp", width=180, anchor="w") #anchor="w" aligns the text to the left e is right
        self.logs_tree.column("Tipo de Ação", width=150, anchor="w")
        self.logs_tree.column("Descrição", width=400, anchor="w")

        self.logs_tree.grid(row=0, column=0, sticky="nsew", pady=10)

        log_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.logs_tree.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.logs_tree.configure(yscrollcommand=log_scrollbar.set)

        ttk.Button(frame, text="Atualizar Logs", command=self._refresh_logs).grid(row=1, column=0, columnspan=2, pady=10)

        self._refresh_logs() # Initial load of logs

    def _refresh_logs(self):
        """Refreshes the logs displayed in the logs tab. Treeview"""
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)

        logs = self.db_manager.get_logs()
        for log in logs:
            self.logs_tree.insert("", tk.END, values=log)

    def on_closing(self):
        """Handles the window closing event to ensure the database connection is closed properly.""" # Thanks to the Gemini here, i forgot that existed
        self.db_manager.close()
        self.root.destroy()
