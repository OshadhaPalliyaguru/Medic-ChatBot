import sqlite3 
from datetime import datetime 

class CovidDB: 
    def __init__(self, db_path='covid_data.db'): 
        self.conn = sqlite3.connect(db_path) 
        self.create_table() 

    def create_table(self): 
        cursor = self.conn.cursor() 
        cursor.execute('''CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY, 
            user_query TEXT NOT NULL, 
            bot_response TEXT NOT NULL, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP 
        )''') 
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS learned_facts (
            id INTEGER PRIMARY KEY, 
            pattern TEXT NOT NULL, 
            response TEXT NOT NULL 
        )''') 
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS pending_reviews (
            id INTEGER PRIMARY KEY, 
            user_query TEXT NOT NULL, 
            user_suggestion TEXT NOT NULL 
        )''') 
        self.conn.commit() 

    def submit_for_review(self, user_query, user_suggestion): 
        cursor = self.conn.cursor() 
        cursor.execute('''INSERT INTO pending_reviews (user_query, user_suggestion) VALUES (?, ?)''', (user_query, user_suggestion)) 
        self.conn.commit() 

    def log_chat(self, user_query, bot_response): 
        cursor = self.conn.cursor() 
        cursor.execute('''INSERT INTO history (user_query, bot_response) VALUES (?, ?)''', (user_query, bot_response)) 
        self.conn.commit() 

    def add_learned_fact(self, pattern, response): 
        cursor = self.conn.cursor() 
        cursor.execute('''INSERT INTO learned_facts (pattern, response) VALUES (?, ?)''', (pattern, response)) 
        self.conn.commit() 

    def get_all_learned_facts(self): 
        """Fetch all learned facts so the NLP engine can apply similarity matching.""" 
        cursor = self.conn.cursor() 
        cursor.execute("SELECT pattern, response FROM learned_facts") 
        return cursor.fetchall() 

    def get_all_pending_reviews(self): 
        cursor = self.conn.cursor() 
        cursor.execute("SELECT id, user_query, user_suggestion FROM pending_reviews") 
        return cursor.fetchall() 

    def delete_pending_review(self, review_id): 
        cursor = self.conn.cursor() 
        cursor.execute("DELETE FROM pending_reviews WHERE id=?", (review_id,)) 
        self.conn.commit() 

    def get_all_learned_facts_with_ids(self): 
        cursor = self.conn.cursor() 
        cursor.execute("SELECT id, pattern, response FROM learned_facts") 
        return cursor.fetchall() 

    def update_learned_fact(self, fact_id, pattern, response): 
        cursor = self.conn.cursor() 
        cursor.execute("UPDATE learned_facts SET pattern=?, response=? WHERE id=?", (pattern, response, fact_id)) 
        self.conn.commit() 

    def delete_learned_fact(self, fact_id): 
        cursor = self.conn.cursor() 
        cursor.execute("DELETE FROM learned_facts WHERE id=?", (fact_id,)) 
        self.conn.commit() 

    def approve_fact(self, review_id): 
        cursor = self.conn.cursor() 
        cursor.execute("SELECT user_query, user_suggestion FROM pending_reviews WHERE id=?", (review_id,)) 
        row = cursor.fetchone() 
        if row: 
            pattern, response = row 
            self.add_learned_fact(pattern, response) 
            cursor.execute("DELETE FROM pending_reviews WHERE id=?", (review_id,)) 
            self.conn.commit() 
