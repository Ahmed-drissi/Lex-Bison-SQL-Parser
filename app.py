import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess
import os
import re

ENGINE_PATH = "./sql_engine"


class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        self.delete("all")
        if not self.textwidget:
            return

        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, fill="#888888", font=("Courier", 12))
            i = self.textwidget.index(f"{i}+1line")


class SQLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Parser GUI")
        self.root.geometry("1000x750")

        # --- Top Frame: Controls ---
        ctrl_frame = tk.Frame(root)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(ctrl_frame, text="Load .sql File", command=self.load_file).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Export to File", command=self.export_file, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Run Queries", command=self.run_queries, bg="green", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)

        # --- Middle Frame: Input with Line Numbers ---
        tk.Label(root, text="Input Queries (separate with ;):").pack(anchor=tk.W, padx=10)

        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.linenumbers = TextLineNumbers(input_frame, width=35, bg="#f0f0f0")
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)

        self.txt_input = tk.Text(input_frame, wrap=tk.NONE, font=("Courier", 12), undo=True)
        self.txt_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(input_frame, command=self.txt_input.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_input.config(yscrollcommand=self.sync_scroll(scrollbar))

        self.linenumbers.attach(self.txt_input)

        for event in ("<KeyRelease>", "<MouseWheel>", "<Button-1>", "<Configure>", "<Return>", "<BackSpace>"):
            self.txt_input.bind(event, self.linenumbers.redraw)

        # Input highlight tags
        self.txt_input.tag_config("error_tag", background="#ffe6e6")
        self.txt_input.tag_config("error_token", foreground="#cc0000", background="#ffd0d0", font=("Courier", 12, "bold"))
        self.txt_input.tag_config("highlight_line", background="#ffff99")

        # --- Bottom Frame: Output Console ---
        tk.Label(root, text="Output / Errors (Click error to jump to line):").pack(anchor=tk.W, padx=10)

        self.txt_output = scrolledtext.ScrolledText(
            root, height=12, font=("Courier", 14), bg="#1e1e1e", fg="#ffffff"
        )
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.txt_output.tag_config("success", foreground="#00ff00")
        self.txt_output.tag_config("clickable_error", foreground="#ff4444", underline=True)
        self.txt_output.tag_config("expected_hint", foreground="#ffcc00")

        self.txt_output.tag_bind("clickable_error", "<Enter>", lambda e: self.txt_output.config(cursor="hand2"))
        self.txt_output.tag_bind("clickable_error", "<Leave>", lambda e: self.txt_output.config(cursor=""))

    def sync_scroll(self, scrollbar):
        def wrapper(*args):
            scrollbar.set(*args)
            self.linenumbers.redraw()
        return wrapper

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt")])
        if filepath:
            with open(filepath, "r", encoding="utf-8") as file:
                self.txt_input.delete("1.0", tk.END)
                self.txt_input.insert(tk.END, file.read())
                self.linenumbers.redraw()

    def export_file(self):
        content = self.txt_input.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Empty", "There is no text to export!")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt")],
            title="Export Queries to File"
        )

        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(content)
                messagebox.showinfo("Success", f"File saved successfully to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def clear_all(self):
        self.txt_input.delete("1.0", tk.END)
        self.txt_output.delete("1.0", tk.END)
        self.txt_input.tag_remove("error_tag", "1.0", tk.END)
        self.txt_input.tag_remove("error_token", "1.0", tk.END)
        self.txt_input.tag_remove("highlight_line", "1.0", tk.END)
        self.linenumbers.redraw()

    def goto_line(self, event):
        index = self.txt_output.index(f"@{event.x},{event.y}")
        tags = self.txt_output.tag_names(index)
        for tag in tags:
            if tag.startswith("link_"):
                line_num = tag.split("_", 1)[1]
                self.txt_input.see(f"{line_num}.0")
                self.txt_input.mark_set("insert", f"{line_num}.0")
                self.txt_input.focus_set()
                self.txt_input.tag_remove("highlight_line", "1.0", tk.END)
                self.txt_input.tag_add("highlight_line", f"{line_num}.0", f"{line_num}.end")
                self.root.after(1500, lambda: self.txt_input.tag_remove("highlight_line", "1.0", tk.END))
                break

    def highlight_token_in_line(self, line_num, token):
        if not token or not token.strip():
            self.txt_input.tag_add("error_tag", f"{line_num}.0", f"{line_num}.end")
            return

        line_text = self.txt_input.get(f"{line_num}.0", f"{line_num}.end")

        # exact match
        col = line_text.find(token)
        if col == -1:
            # case-insensitive fallback
            col = line_text.lower().find(token.lower())

        if col != -1:
            start = f"{line_num}.{col}"
            end = f"{line_num}.{col + len(token)}"
            self.txt_input.tag_add("error_tag", f"{line_num}.0", f"{line_num}.end")
            self.txt_input.tag_add("error_token", start, end)
        else:
            self.txt_input.tag_add("error_tag", f"{line_num}.0", f"{line_num}.end")

    def parse_error_line(self, raw_line):
        """
        Expected stderr format from yacc:
            ERROR|<lineno>|<message> at '<token>'
        """
        if not raw_line.startswith("ERROR|"):
            return None

        parts = raw_line.split("|", 2)
        if len(parts) < 3:
            return None

        line_num = parts[1].strip()
        rest = parts[2].strip()

        token = ""
        base_msg = rest
        expected_hint = ""

        # Extract token after: at '...'
        m = re.search(r"\bat\s+'([^']*)'\s*$", rest)
        if m:
            token = m.group(1)
            base_msg = rest[:m.start()].rstrip(" ,")

        # Extract expected clause in bison verbose message
        # e.g. "syntax error, unexpected IDENTIFIER, expecting FROM or COMMA"
        exp_idx = base_msg.find(", expecting")
        if exp_idx != -1:
            expected_hint = base_msg[exp_idx + 2:].strip()   # "expecting ..."
            base_msg = base_msg[:exp_idx].strip()            # before expecting

        def humanize(msg):
            msg = msg.replace("$end", "end of input")
            replacements = {
                "IDENTIFIER": "identifier",
                "NUMBER": "number",
                "STRING": "string literal",
                "SEMICOLON": "';'",
                "LPAREN": "'('",
                "RPAREN": "')'",
                "COMMA": "','",
                "EQUAL": "'='",
                "ASTERISK": "'*'",
            }
            for k, v in replacements.items():
                msg = re.sub(rf"\b{k}\b", v, msg)
            return msg

        return line_num, token, humanize(base_msg), humanize(expected_hint)

    def run_queries(self):
        self.txt_output.delete("1.0", tk.END)
        self.txt_input.tag_remove("error_tag", "1.0", tk.END)
        self.txt_input.tag_remove("error_token", "1.0", tk.END)
        self.txt_input.tag_remove("highlight_line", "1.0", tk.END)

        queries = self.txt_input.get("1.0", tk.END)
        if not queries.strip():
            return

        if not os.path.exists(ENGINE_PATH):
            self.txt_output.insert(tk.END, f"Cannot find '{ENGINE_PATH}'. Compile C code first.\n")
            return

        try:
            process = subprocess.Popen(
                [ENGINE_PATH],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout_data, stderr_data = process.communicate(input=queries)

            # Show success/info output from yacc (IMPORTANT)
            if stdout_data and stdout_data.strip():
                for line in stdout_data.splitlines():
                    self.txt_output.insert(tk.END, line + "\n", "success")

            # Show errors
            if stderr_data and stderr_data.strip():
                for raw_line in stderr_data.splitlines():
                    parsed = self.parse_error_line(raw_line.strip())

                    if parsed:
                        line_num, token, base_msg, expected_hint = parsed

                        # Highlight token/line in input
                        self.highlight_token_in_line(line_num, token)

                        # Clickable output line
                        link_tag = f"link_{line_num}"
                        self.txt_output.tag_config(link_tag)
                        self.txt_output.tag_bind(link_tag, "<Button-1>", self.goto_line)

                        if token:
                            msg = f"➤ ERROR at line {line_num}: {base_msg} (got: '{token}')\n"
                        else:
                            msg = f"➤ ERROR at line {line_num}: {base_msg}\n"

                        self.txt_output.insert(tk.END, msg, ("clickable_error", link_tag))

                        if expected_hint:
                            self.txt_output.insert(tk.END, f"   ↳ {expected_hint}\n", "expected_hint")
                    else:
                        self.txt_output.insert(tk.END, raw_line + "\n")

            # If absolutely no output
            if (not stdout_data or not stdout_data.strip()) and (not stderr_data or not stderr_data.strip()):
                self.txt_output.insert(tk.END, "No output.\n")

        except Exception as e:
            self.txt_output.insert(tk.END, f"Application Error: {str(e)}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = SQLApp(root)
    root.mainloop()
