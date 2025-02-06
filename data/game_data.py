import random
import tkinter as tk

game_settings = {
    "min_number": 1,
    "max_number": 100,
    "max_attempts": 10,
    "instructions": "Guess the number between 1 and 100. You have 10 attempts."
}

def generate_target():
    return random.randint(game_settings["min_number"], game_settings["max_number"])

def start_guess_game(root, icon_path):
    game_window = tk.Toplevel(root)
    game_window.title("Guess the Number")
    game_window.geometry("400x300")
    game_window.resizable(False, False)
    try:
        game_window.iconbitmap(icon_path)
    except Exception:
        pass

    min_number = game_settings["min_number"]
    max_number = game_settings["max_number"]
    max_attempts = game_settings["max_attempts"]
    instructions = game_settings["instructions"]

    target_number = generate_target()
    attempts_left = [max_attempts]

    header_frame = tk.Frame(game_window)
    header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

    content_frame = tk.Frame(game_window)
    content_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    content_frame.columnconfigure(0, weight=1)

    button_frame = tk.Frame(game_window)
    button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)

    footer_frame = tk.Frame(game_window)
    footer_frame.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")

    instruction_label = tk.Label(
        header_frame,
        text=instructions,
        font=("Arial", 12),
        wraplength=380,
        justify="center"
    )
    instruction_label.pack(fill="x")

    attempts_label = tk.Label(
        header_frame,
        text=f"Attempts left: {attempts_left[0]}",
        font=("Arial", 12)
    )
    attempts_label.pack(pady=5)

    guess_entry = tk.Entry(content_frame, font=("Arial", 12))
    guess_entry.grid(row=0, column=0, sticky="ew")
    
    feedback_label = tk.Label(content_frame, text="", font=("Arial", 12))
    feedback_label.grid(row=1, column=0, pady=5, sticky="ew")

    def check_guess():
        guess = guess_entry.get().strip()
        if not guess.isdigit():
            feedback_label.config(text="Please enter a valid number.")
            return

        guess_int = int(guess)
        if guess_int < min_number or guess_int > max_number:
            feedback_label.config(text=f"Guess must be between {min_number} and {max_number}.")
            return

        if attempts_left[0] <= 0:
            feedback_label.config(text="No attempts left. Game over!")
            return

        attempts_left[0] -= 1
        attempts_label.config(text=f"Attempts left: {attempts_left[0]}")

        if guess_int < target_number:
            feedback_label.config(text="Too low!")
        elif guess_int > target_number:
            feedback_label.config(text="Too high!")
        else:
            feedback_label.config(text="Congratulations! You guessed it!")
            guess_entry.config(state="disabled")
            submit_button.config(state="disabled")
            return

        if attempts_left[0] == 0:
            feedback_label.config(text=f"Game over! The number was {target_number}.")
            guess_entry.config(state="disabled")
            submit_button.config(state="disabled")

    def restart_game():
        nonlocal target_number
        target_number = generate_target()
        attempts_left[0] = max_attempts
        attempts_label.config(text=f"Attempts left: {attempts_left[0]}")
        feedback_label.config(text="")
        guess_entry.config(state="normal")
        submit_button.config(state="normal")
        guess_entry.delete(0, tk.END)

    submit_button = tk.Button(
        button_frame,
        text="Submit Guess",
        command=check_guess,
        font=("Arial", 12)
    )
    submit_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

    restart_button = tk.Button(
        button_frame,
        text="Restart Game",
        command=restart_game,
        font=("Arial", 12)
    )
    restart_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    guess_entry.focus_set()
