import sqlite3
from tkinter import messagebox
from datetime import datetime

class DatabaseManager:
    
    def __init__(self, db_name="receitas.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Connects to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível conectar ao banco de dados: {e}")

    def _create_tables(self):
        """Create table if not exists."""
        try:
            # Recipes Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipes (
                    recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    prep_time INTEGER,
                    difficulty TEXT,
                    category TEXT,
                    instructions TEXT,
                    tags TEXT
                )
            ''')

            # Ingredients Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ingredients (
                    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')

            # Made a junction table to handle recipes and ingredients (n-n) 
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipe_ingredients (
                    recipe_id INTEGER,
                    ingredient_id INTEGER,
                    quantity TEXT,
                    unit TEXT,
                    PRIMARY KEY (recipe_id, ingredient_id),
                    FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id) ON DELETE CASCADE,
                    FOREIGN KEY (ingredient_id) REFERENCES ingredients (ingredient_id) ON DELETE CASCADE
                )
            ''')

            # Logs Table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    description TEXT
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível criar as tabelas: {e}")

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def log_action(self, action_type, description=""):
        """Logs user actions in the database registration."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("INSERT INTO user_logs (timestamp, action_type, description) VALUES (?, ?, ?)",
                                (timestamp, action_type, description))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao registrar log: {e}")

    def get_logs(self):
        """Get logs function."""
        try:
            self.cursor.execute("SELECT timestamp, action_type, description FROM user_logs ORDER BY timestamp DESC")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao buscar logs: {e}")
            return []

    def add_recipe(self, name, prep_time, difficulty, category, instructions, tags, ingredients_list):
        """
        Recipe registration function. I used a list of dictionaries to handle the ingredients,
        where each dictionary contains 'name', 'quantity', and 'unit'. (Null values are allowed for quantity and unit).
        """
        try:
            self.cursor.execute("INSERT INTO recipes (name, prep_time, difficulty, category, instructions, tags) VALUES (?, ?, ?, ?, ?, ?)",
                                (name, prep_time, difficulty, category, instructions, tags))
            recipe_id = self.cursor.lastrowid

            for ingredient in ingredients_list:
                ingredient_name = ingredient.get('name', '').strip().lower()
                quantity = ingredient.get('quantity', '')
                unit = ingredient.get('unit', '')

                if not ingredient_name:
                    continue

                # Verifies if the ingredient already exists in the ingredients table
                self.cursor.execute("SELECT ingredient_id FROM ingredients WHERE name = ?", (ingredient_name,))
                result = self.cursor.fetchone()
                if result:
                    ingredient_id = result[0]
                else:
                    self.cursor.execute("INSERT INTO ingredients (name) VALUES (?)", (ingredient_name,))
                    ingredient_id = self.cursor.lastrowid

                # Links the recipe with the ingredient in the junction table
                self.cursor.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit) VALUES (?, ?, ?, ?)",
                                    (recipe_id, ingredient_id, quantity, unit))
            self.conn.commit()
            self.log_action("Receita Cadastrada", f"Nome: {name}")
            return True
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Erro de Cadastro", f"Erro de integridade ao adicionar receita: {e}. Verifique se o ingrediente não está duplicado.")
            return False
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao adicionar receita: {e}")
            return False

    def update_recipe(self, recipe_id, name, prep_time, difficulty, category, instructions, tags, ingredients_list):
        """
        Update a recipe by its ID. The ingredients_list is a list of dictionaries.
        """
        try:
            self.cursor.execute("""
                UPDATE recipes SET
                name = ?, prep_time = ?, difficulty = ?, category = ?, instructions = ?, tags = ?
                WHERE recipe_id = ?
            """, (name, prep_time, difficulty, category, instructions, tags, recipe_id))

            # Remove all existing ingredients for this recipe
            self.cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))

            # Add all
            for ingredient in ingredients_list:
                ingredient_name = ingredient.get('name', '').strip().lower()
                quantity = ingredient.get('quantity', '')
                unit = ingredient.get('unit', '')

                if not ingredient_name:
                    continue

                self.cursor.execute("SELECT ingredient_id FROM ingredients WHERE name = ?", (ingredient_name,))
                result = self.cursor.fetchone()
                if result:
                    ingredient_id = result[0]
                else:
                    self.cursor.execute("INSERT INTO ingredients (name) VALUES (?)", (ingredient_name,))
                    ingredient_id = self.cursor.lastrowid

                self.cursor.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit) VALUES (?, ?, ?, ?)",
                                    (recipe_id, ingredient_id, quantity, unit))
            self.conn.commit()
            self.log_action("Receita Atualizada", f"ID: {recipe_id}, Nome: {name}")
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao atualizar receita: {e}")
            return False

    def delete_recipe(self, recipe_id):
        """
        Delete a recipe by its ID.
        Deletes the recipe and all associated ingredients in the junction table.
        """
        try:
            # Get the recipe name before deleting
            self.cursor.execute("SELECT name FROM recipes WHERE recipe_id = ?", (recipe_id,))
            result = self.cursor.fetchone()
            name = result[0] if result else ""
            self.log_action("Receita Excluída", f"ID: {recipe_id}, Nome: {name}")
            # Delete the recipe and all associated ingredients
            self.cursor.execute("DELETE FROM recipes WHERE recipe_id = ?", (recipe_id,))
            self.conn.commit()
            
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao excluir receita: {e}")
            return False

    def get_all_recipes(self):
        """Get all recipes function."""
        try:
            self.cursor.execute("SELECT recipe_id, name, prep_time, difficulty, category, instructions, tags FROM recipes")
            recipes_data = self.cursor.fetchall()

            all_recipes = []
            for recipe in recipes_data:
                recipe_id, name, prep_time, difficulty, category, instructions, tags = recipe
                ingredients = []
                self.cursor.execute('''
                    SELECT i.name, ri.quantity, ri.unit
                    FROM recipe_ingredients ri
                    JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
                    WHERE ri.recipe_id = ?
                ''', (recipe_id,))
                ingredients_data = self.cursor.fetchall()
                for ing_name, ing_quantity, ing_unit in ingredients_data:
                    # Format the ingredient string hopefully in the form "quantidade unidade de ingrediente"
                    ingredient_formatted = ""
                    if ing_quantity:
                        ingredient_formatted += ing_quantity + " "
                    if ing_unit:
                        ingredient_formatted += ing_unit + " "
                    if ing_name:
                        ingredient_formatted += "de " + ing_name
                    ingredients.append(ingredient_formatted.strip())

                all_recipes.append({
                    'recipe_id': recipe_id,
                    'name': name,
                    'prep_time': prep_time,
                    'difficulty': difficulty,
                    'category': category,
                    'instructions': instructions,
                    'tags': tags,
                    'ingredients': ingredients
                }) # Append the recipe dictionary to the list
            return all_recipes
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao buscar todas as receitas: {e}")
            return []

    def filter_recipes(self, ingredients_input, max_prep_time, category, difficulty):
        """
        Filters recipes based on ingredients, maximum preparation time, category, and difficulty.
        """
        ingredients_list = [ing.strip().lower() for ing in ingredients_input.split(',') if ing.strip()]
        
        # DEBUG: Print the processed ingredients list
        print(f"DEBUG filter_recipes: Ingredientes processados: {ingredients_list}")

        query = """ 
            SELECT r.recipe_id, r.name, r.prep_time, r.difficulty, r.category, r.instructions, r.tags
            FROM recipes r
        """ # Query to select recipes
        
        conditions = []
        params = []

        # Adds conditions based on the provided filters
        if category:
            conditions.append("r.category LIKE ?")
            params.append(f"%{category}%")
        if difficulty:
            conditions.append("r.difficulty LIKE ?")
            params.append(f"%{difficulty}%")
        if max_prep_time:
            try:
                max_time = int(max_prep_time)
                conditions.append("r.prep_time <= ?")
                params.append(max_time)
            except ValueError:
                pass # If max_prep_time is not a valid integer, we ignore this condition so it doesnt break everything

        # If there are ingredients to filter, we create a subquery to count matched ingredients
        if ingredients_list:
            ingredient_placeholders = ','.join(['?' for _ in ingredients_list])
            ingredient_subquery = f"""
                SELECT ri.recipe_id, COUNT(DISTINCT ri.ingredient_id) as matched_ingredients
                FROM recipe_ingredients ri
                JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
                WHERE i.name IN ({ingredient_placeholders})
                GROUP BY ri.recipe_id
            """
            # This subquery counts how many of the specified ingredients are in each recipe. 
            query += f" JOIN ({ingredient_subquery}) AS sub ON r.recipe_id = sub.recipe_id"
            conditions.append(f"sub.matched_ingredients >= ?")
            params.extend(ingredients_list) # Adiciona os nomes dos ingredientes aos parâmetros
            params.append(len(ingredients_list)) # Adiciona a contagem de ingredientes aos parâmetros

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # DEBUG: Print the final query and parameters
        print(f"DEBUG filter_recipes: Query final: {query}")
        print(f"DEBUG filter_recipes: Parâmetros finais: {params}")

        try:
            self.cursor.execute(query, tuple(params))
            recipes_data = self.cursor.fetchall()

            filtered_recipes = []
            for recipe in recipes_data:
                recipe_id, name, prep_time, difficulty, category, instructions, tags = recipe
                ingredients = []
                self.cursor.execute('''
                    SELECT i.name, ri.quantity, ri.unit
                    FROM recipe_ingredients ri
                    JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
                    WHERE ri.recipe_id = ?
                ''', (recipe_id,))
                ingredients_data = self.cursor.fetchall()
                for ing_name, ing_quantity, ing_unit in ingredients_data:
                    ingredient_formatted = ""
                    if ing_quantity:
                        ingredient_formatted += ing_quantity + " "
                    if ing_unit:
                        ingredient_formatted += ing_unit + " "
                    if ing_name:
                        ingredient_formatted += "de " + ing_name
                    ingredients.append(ingredient_formatted.strip())
                
                filtered_recipes.append({
                    'recipe_id': recipe_id,
                    'name': name,
                    'prep_time': prep_time,
                    'difficulty': difficulty,
                    'category': category,
                    'instructions': instructions,
                    'tags': tags,
                    'ingredients': ingredients
                })
            return filtered_recipes
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao filtrar receitas: {e}")
            return [] # Empty list if an error occurs