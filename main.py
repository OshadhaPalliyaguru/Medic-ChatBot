import customtkinter as ctk 
from db import CovidDB 
from nlp_processor import CovidEngine 

class CovidApp(ctk.CTk): 
    def __init__(self): 
        super().__init__() 
        self.title("COVID-19 Support Centre - Admin-Mediated Model") 
        self.geometry("600x700") 
        self.db = CovidDB() 
        self.engine = CovidEngine() 
        self.learning_mode = False 
        self.last_unknown = "" 
        
        # UI: Chat Area 
        self.chat_display = ctk.CTkTextbox(self, width=560, height=400) 
        self.chat_display.pack(pady=20) 
        
        # UI: Input Area 
        self.user_input = ctk.CTkEntry(self, width=450, placeholder_text="Ask a COVID-19 question...") 
        self.user_input.pack(pady=10) 
        self.send_btn = ctk.CTkButton(self, text="Send", command=self.handle_message) 
        self.send_btn.pack() 
        
        # UI: Admin Panel Demo (Hidden in real apps, but good for Viva) 
        self.admin_btn = ctk.CTkButton(
            self, 
            text="Demo Admin: Approve All Pending",  
            fg_color="darkgreen", 
            command=self.demo_admin_approval
        ) 
        self.admin_btn.pack(pady=20) 

    def handle_message(self): 
        msg = self.user_input.get() 
        if not msg: 
            return 
        
        self.chat_display.insert("end", f"You: {msg}\n") 
        
        if self.learning_mode: 
            self.db.submit_for_review(self.last_unknown, msg) 
            self.chat_display.insert("end", "Bot: Thank you. Your suggestion is now 'Pending Review' by our medical staff.\n\n") 
            self.learning_mode = False 
        else: 
            res, is_learning = self.engine.get_response(msg, self.db) 
            self.chat_display.insert("end", f"Bot: {res}\n\n") 
            if is_learning: 
                self.learning_mode = True 
                self.last_unknown = msg 
         
        self.user_input.delete(0, "end") 
 
    def demo_admin_approval(self): 
        # Logic to simulate an admin promoting data to Tier 3 verified knowledge 
        cursor = self.db.conn.cursor() 
        cursor.execute("SELECT id FROM pending_reviews") 
        pending_ids = [row for row in cursor.fetchall()] 
        for pid in pending_ids: 
            self.db.approve_fact(pid[0]) 
        self.chat_display.insert("end", "SYSTEM: Admin has verified and promoted pending data to the Active Brain.\n\n") 
 
if __name__ == "__main__": 
    app = CovidApp() 
    app.mainloop()