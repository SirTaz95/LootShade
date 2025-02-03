import sys
import os
import json
import time
import random
import requests
import pstats
import cProfile
from io import StringIO
from PIL import Image, ImageTk
from PIL import Image, ImageOps
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import webbrowser
from data.npc_data import npc_data
from data.theme_data import theme_data

GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfG9fj7YkLGRuihTsyGJy7-enFaWi4la_uizAm3MfaR_rrh2Q/formResponse"
BUG_DESCRIPTION_ID = "entry.1319961271"

CONFIG_FILE = "config.json"

start_time = time.time()
print("Starting up...")
time.sleep(2)

def profile_script():
    if not config.get("enable_profiling", False):
        root.mainloop()
        return

    print("Profiling enabled...")
    profiler = cProfile.Profile()
    
    with profiler:
        root.mainloop()

    with open("profile_output.txt", "w") as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.strip_dirs().sort_stats("cumulative").print_stats()

    print("Profiling complete, results saved to profile_output.txt.")

def restart_application():
    python = sys.executable
    os.execl(python, python, *sys.argv)
    
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_config():
    default_config = {
        "show_info_window": True,
        "world": "F2P",
        "show_members_items": True,
        "show_drops_as_fraction": False,
        "theme": "OSWiki: Day",
        "enable_profiling": False
    }

    user_config_path = os.path.join(os.getenv('APPDATA'), 'LootShade', CONFIG_FILE)

    if os.path.exists(user_config_path):
        try:
            with open(user_config_path, "r") as file:
                config = json.load(file)
                if isinstance(config, dict):
                    return {**default_config, **config}
        except (json.JSONDecodeError, IOError):
            print("Warning: User config.json is corrupted. Resetting to defaults.")

    config_path = resource_path(CONFIG_FILE)
    try:
        with open(config_path, "r") as file:
            config = json.load(file)
            if isinstance(config, dict):
                return {**default_config, **config}
    except (json.JSONDecodeError, IOError):
        print("Warning: Could not load packaged config.json. Using defaults.")

    return default_config

def save_config(config):
    user_config_path = os.path.join(os.getenv('APPDATA'), 'LootShade', CONFIG_FILE)
    os.makedirs(os.path.dirname(user_config_path), exist_ok=True)
    
    try:
        with open(user_config_path, "w") as file:
            json.dump(config, file, indent=4)
        print(f"Config saved to: {user_config_path}")
    except IOError:
        print("Error: Unable to save config.json.")

import tkinter as tk
from tkinter import ttk

def show_info_window(force=False):
    config = load_config()
    
    if not force and not config.get("show_info_window", True):
        return

    info_window = tk.Toplevel(root)
    info_window.title("Welcome to LootShade")
    info_window.geometry("420x260")
    info_window.resizable(False, False)
    info_window.iconbitmap(icon_path)
    info_window.configure(bg="#2c2f33")

    text_frame = tk.Frame(info_window, bg="#2c2f33")
    text_frame.pack(expand=True, fill="both", padx=10, pady=(10, 5))

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")

    info_text = tk.Text(
        text_frame,
        wrap="word",
        font=("Arial", 12),
        padx=12,
        pady=12,
        height=8,
        width=50,
        borderwidth=0,
        bg="#3b3e42",
        fg="white",
        relief="flat",
        yscrollcommand=scrollbar.set
    )
    info_text.pack(expand=True, fill="both", side="left")
    scrollbar.config(command=info_text.yview)

    info_text.insert("end", "Welcome to LootShade!\n\n", "header")
    info_text.insert("end", "Looking for help?\n", "bold")
    info_text.insert("end", "Click 'Help' from the menu bar where you can find the README, FAQ & a discord link.\n\n")
    info_text.insert("end", "Find a bug?\n", "bold")
    info_text.insert("end", "Under 'Help' you can also find the option to submit a bug. Feel free to use this to leave feedback as well.\n\n")
    info_text.insert("end", "Correct World selected?\n", "bold")
    info_text.insert("end", "Some NPCs drop different items depending on whether you are on a members' world or not. In the menu bar, you should find 'World'. Make your selection (f2p/p2p) to see the correct drops.\n\n")
    info_text.insert("end", "Enable Profiling?\n", "bold")
    info_text.insert("end", "Only turn this on if you feel like LootShade is running poorly. It will create (profile_output.txt) and place it in the same location as LootShade. It can be found under 'Settings'.\n\n")
    info_text.insert("end", "Welcome screen\n", "bold")
    info_text.insert("end", "If you choose to hide this window from opening at startup but want to see it again, you can always reopen it under 'Help' by clicking 'Show Info Window'.\n\n")

    info_text.tag_configure("header", font=("Arial", 20, "bold"), justify="center", foreground="#f8c471")
    info_text.tag_configure("bold", font=("Arial", 14, "bold"), foreground="#aed6f1")
    info_text.tag_configure("normal", font=("Arial", 10), foreground="white")

    info_text.config(state="disabled")

    show_again_var = tk.BooleanVar(value=config.get("show_info_window", True))

    def toggle_show_again():
        config["show_info_window"] = show_again_var.get()
        save_config(config)

    show_again_checkbox = tk.Checkbutton(
        info_window,
        text="Show this window on startup",
        variable=show_again_var,
        command=toggle_show_again,
        bg="#2c2f33",
        fg="white",
        selectcolor="#44474c",
        activebackground="#3b3e42",
        font=("Arial", 10)
    )
    show_again_checkbox.pack(pady=5)

    close_button = tk.Button(
        info_window,
        text="OK",
        command=info_window.destroy,
        font=("Arial", 12, "bold"),
        bg="#4caf50",
        fg="white",
        relief="flat",
        padx=10,
        pady=5
    )
    close_button.pack(pady=10)

def force_show_info_window():
    show_info_window(force=True)

def send_bug_report():
    bug_description = bug_entry.get("1.0", tk.END).strip()
    if not bug_description:
        messagebox.showerror("Error", "Bug description cannot be empty!")
        return

    data = {BUG_DESCRIPTION_ID: bug_description}

    try:
        response = requests.post(GOOGLE_FORM_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})

        if response.status_code == 200 or response.status_code == 204:
            messagebox.showinfo("Success", "Bug report submitted successfully!")
            bug_entry.delete("1.0", tk.END)
            bug_window.destroy()
        else:
            messagebox.showerror("Error", f"Failed to submit bug report: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"Error submitting bug report:\n{e}")

import tkinter as tk
from tkinter import ttk

def report_bug():
    global bug_window
    bug_window = tk.Toplevel(root)
    bug_window.title("Report Bug")
    bug_window.geometry("400x225")  
    bug_window.resizable(False, False)
    bug_window.iconbitmap(icon_path)
    
    frame = ttk.Frame(bug_window, padding=10)
    frame.grid(row=0, column=0, sticky="nsew")
    
    ttk.Label(frame, text="Describe the bug:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
    
    global bug_entry
    bug_entry = tk.Text(frame, height=8, width=45, wrap="word")
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=bug_entry.yview)
    bug_entry.config(yscrollcommand=scrollbar.set)
    
    bug_entry.grid(row=1, column=0, sticky="nsew")
    scrollbar.grid(row=1, column=1, sticky="ns")
    
    button_frame = ttk.Frame(frame)
    button_frame.grid(row=2, column=0, columnspan=2, pady=10)
    
    submit_button = ttk.Button(button_frame, text="Submit", command=send_bug_report)
    submit_button.pack(side="left", padx=5)
    
    close_button = ttk.Button(button_frame, text="Cancel", command=bug_window.destroy)
    close_button.pack(side="left", padx=5)
    
    bug_window.grid_columnconfigure(0, weight=1)
    bug_window.grid_rowconfigure(1, weight=1)

rarity_conversion = {
    "0.39%": "0.5/128", "1.95%": "2.5/128", "5.86%": "7.5/128",
    "0.00%": "0/128", "0.78%": "1/128", "1.56%": "2/128", "2.34%": "3/128", "3.13%": "4/128",
    "3.91%": "5/128", "4.69%": "6/128", "5.47%": "7/128", "6.25%": "8/128", "7.03%": "9/128",
    "7.81%": "10/128", "8.59%": "11/128", "9.38%": "12/128", "10.16%": "13/128", "10.94%": "14/128",
    "11.72%": "15/128", "12.5%": "16/128", "13.28%": "17/128", "14.06%": "18/128", "14.84%": "19/128",
    "15.63%": "20/128", "16.41%": "21/128", "17.19%": "22/128", "17.97%": "23/128", "18.75%": "24/128",
    "19.53%": "25/128", "20.31%": "26/128", "21.09%": "27/128", "21.88%": "28/128", "22.66%": "29/128",
    "23.44%": "30/128", "24.22%": "31/128", "25%": "32/128", "25.78%": "33/128", "26.56%": "34/128",
    "27.34%": "35/128", "28.13%": "36/128", "28.91%": "37/128", "29.69%": "38/128", "30.47%": "39/128",
    "31.25%": "40/128", "32.03%": "41/128", "32.81%": "42/128", "33.59%": "43/128", "34.38%": "44/128",
    "35.16%": "45/128", "35.94%": "46/128", "36.72%": "47/128", "37.5%": "48/128", "38.28%": "49/128",
    "39.06%": "50/128", "39.84%": "51/128", "40.63%": "52/128", "41.41%": "53/128", "42.19%": "54/128",
    "43.75%": "56/128", "44.53%": "57/128", "45.31%": "58/128", "46.09%": "59/128", "46.88%": "60/128",
    "47.66%": "61/128", "48.44%": "62/128", "49.22%": "63/128", "50%": "64/128", "100.00%": "128/128"
}

def format_rarity(rarity):
    if rarity == "100.00%" or rarity == "100%" or rarity_conversion.get(rarity) == "128/128":
        return "Always"

    if show_frac_var.get():
        return rarity_conversion.get(rarity, rarity)

    return rarity

sort_order = {}

def sort_treeview(treeview, column_index):
    items = list(treeview.get_children())

    def get_sort_value(item):
        value = treeview.item(item)['values'][column_index]

        if not isinstance(value, str):
            return value

        order_desc = sort_order.get(column_index, False)

        if value == "Always":
            return float('inf') if order_desc else float('+inf')

        # Handle fractions like "0/128" and "1.5/128"
        if '/' in value:
            try:
                numerator, denominator = value.split('/')
                numerator = float(numerator)  # Support floating-point numerators
                denominator = float(denominator)  # Support floating-point denominators
                return numerator / denominator
            except ValueError:
                return float('-inf') if order_desc else float('inf')

        try:
            # Handle percentages (remove % and convert to float)
            return float(value.strip('%')) if value.endswith('%') else float(value)
        except ValueError:
            return float('-inf') if order_desc else float('inf')

    order = sort_order.get(column_index, False)
    items.sort(key=get_sort_value, reverse=order)
    sort_order[column_index] = not order

    for index, item in enumerate(items):
        treeview.move(item, '', index)

def show_drops(event):
    if not npc_listbox.curselection():
        return

    selected_index = npc_listbox.curselection()[0]
    try:
        selected_npc, selected_world_entry, _ = npc_listbox_data[selected_index]
        npc_name = selected_npc
        npc_id = selected_world_entry['id']
    except ValueError:
        messagebox.showerror("Error", "Invalid NPC selection format. Please reselect an NPC.")
        return

    drop_listbox.delete(*drop_listbox.get_children())
    selected_world = world_var.get().lower()

    if npc_name in npc_data:
        drops = []
        for world_entry in npc_data[npc_name]:
            if world_entry['id'] == npc_id:
                drops = world_entry.get(selected_world, [])
                break

        if drops:
            for drop in drops:
                item_name = f"★ {drop['item']}" if drop.get('members', False) else drop['item']
                formatted_rarity = format_rarity(drop.get('rarity', "N/A"))
                drop_listbox.insert("", "end", values=(item_name, drop.get('qty', 1), formatted_rarity))
        else:
            drop_listbox.insert("", "end", values=("No drops available", "", ""))
    else:
        drop_listbox.insert("", "end", values=("No drops available", "", ""))

def toggle_rarity_display():
    config["show_drops_as_fraction"] = show_frac_var.get()
    save_config(config)
    refresh_drops()

def search_items():
    search_term = search_entry.get().lower()
    search_results.delete(*search_results.get_children())
    selected_world = world_var.get().lower()

    if not search_term:
        return

    results_found = False

    for npc, worlds in npc_data.items():
        hide_drop_tables = config.get("hide_drop_tables", False)

        if hide_drop_tables and npc.startswith("\u25C4"):
            continue  

        for world_entry in worlds:
            if selected_world in world_entry:
                for drop in world_entry[selected_world]:
                    if hide_drop_tables and drop['item'].startswith("\u25C4"):
                        continue
                    
                    if search_term in drop['item'].lower() and (show_members_var.get() or not drop['members']):
                        item_name = f"★ {drop['item']}" if drop['members'] else drop['item']
                        formatted_rarity = format_rarity(drop.get('rarity', "N/A"))

                        if npc.startswith("\u25C4") and not hide_drop_tables:
                            npc_display_name = f"{npc}"
                        else:
                            for level_entry in world_entry.get("levels", []):
                                npc_level = level_entry.get("lvl", "N/A")
                                npc_display_name = f"{npc} (lvl-{npc_level})"
                                
                        search_results.insert("", "end", values=(npc_display_name, item_name, drop['qty'], formatted_rarity))
                        results_found = True

    if not results_found:
        search_results.insert("", "end", values=("No results found", "", "", ""))

def refresh_drops():
    if npc_listbox.curselection():
        show_drops(None)
    if search_entry.get().strip():
        search_items()

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

theme_settings = {
    "background_color": "#ffffff",
    "foreground_color": "#000000",
    "treeview_bg": "#ffffff",
    "treeview_fg": "#000000",
    "treeview_heading_bg": "#e0e0e0",
    "treeview_heading_fg": "#000000",
    "img_bg_color": "#ffffff",
    "rgb_colors": {
        "background_color": hex_to_rgb("#ffffff"),
        "foreground_color": hex_to_rgb("#000000"),
        "treeview_bg": hex_to_rgb("#ffffff"),
        "treeview_fg": hex_to_rgb("#000000"),
        "treeview_heading_bg": hex_to_rgb("#e0e0e0"),
        "treeview_heading_fg": hex_to_rgb("#000000"),
        "img_bg_color": hex_to_rgb("#ffffff"),
    }
}
image_cache = {}

def load_images_optimized(folder_name):
    global image_cache
    if folder_name in image_cache:
        return image_cache[folder_name]
    images = {}
    for filename in os.listdir(folder_name):
        if filename.endswith((".jpg", ".png")):
            img = Image.open(os.path.join(folder_name, filename))
            img.thumbnail((150, 200), Image.Resampling.LANCZOS)
            images[filename] = ImageTk.PhotoImage(img)
    image_cache[folder_name] = images
    return images

def load_images(folder_name):
    global image_cache
    folder_path = os.path.join(os.path.dirname(__file__), folder_name)
    images = {}
    display_name_map = {}

    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                img_path = os.path.join(folder_path, filename)
                img = Image.open(img_path).convert("RGBA")
                images[filename] = img
                display_name = os.path.splitext(filename)[0]
                display_name_map[display_name] = filename

    except FileNotFoundError:
        print(f"Error: Folder '{folder_name}' not found.")

    image_cache = images
    return images, display_name_map

config = load_config()

def update_world():
    config["world"] = world_var.get()
    save_config(config)
    refresh_drops()

def toggle_theme():
    global theme_settings, image_cache
    current_theme = theme_var.get()
    config["theme"] = current_theme
    save_config(config)

    theme_settings = theme_data.get(current_theme, theme_data["OSWiki: Day"])

    npc_listbox.config(bg=theme_settings["treeview_bg"])
    image_label.config(bg=theme_settings["img_bg_color"])
    
    root.tk_setPalette(
        background=theme_settings["background_color"],
        foreground=theme_settings["foreground_color"],
        activeBackground=theme_settings["treeview_heading_bg"],
        activeForeground=theme_settings["treeview_heading_fg"],
    )

    style.theme_use("clam")
    style.configure(
        "Treeview",
        background=theme_settings["treeview_bg"],
        foreground=theme_settings["treeview_fg"],
        fieldbackground=theme_settings["treeview_bg"],
    )
    style.configure(
        "Treeview.Heading",
        background=theme_settings["treeview_heading_bg"],
        foreground=theme_settings["treeview_heading_fg"],
    )

    if npc_listbox.curselection():
        display_image(None)
    else:
        global placeholder_image
        placeholder_image = create_placeholder_image()
        image_label.config(image=placeholder_image)
        image_label.image = placeholder_image

def toggle_show_members():
    config["show_members_items"] = show_members_var.get()
    save_config(config)
    refresh_drops()

def toggle_hide_guardians():
    config["hide_guardians"] = hide_guardians_var.get()
    save_config(config)
    update_npc_list()
    search_items()

def toggle_hide_drop_tables():
    config["hide_drop_tables"] = hide_drop_tables_var.get()
    save_config(config)
    update_npc_list()
    search_items()

def update_npc_list():
    npc_listbox.delete(0, tk.END)
    
    for npc, world_entry, npc_id in npc_listbox_data:
        if config.get("hide_guardians", False) and npc.startswith("\u2022"):  # ◄
            continue
        if config.get("hide_drop_tables", False) and npc.startswith("\u25C4"):  # •
            continue
        
        npc_listbox.insert(tk.END, npc)

def resize_panes():
    total_width = root.winfo_width()
    frame1_width = total_width // 6
    frame2_width = total_width // 6
    frame3_width = total_width - (frame1_width + frame2_width)

    top_paned_window.paneconfig(npc_listbox_frame, minsize=frame1_width, width=frame1_width)
    top_paned_window.paneconfig(image_frame, minsize=frame2_width, width=frame2_width)
    top_paned_window.paneconfig(drop_listbox_frame, minsize=frame3_width, width=frame3_width)

last_resize_time = 0

def resize_panes_throttled(event=None):
    global last_resize_time
    current_time = time.time()
    if current_time - last_resize_time > 0.2:
        resize_panes()
        last_resize_time = current_time

root = tk.Tk()
root.title("LootShade")
root.geometry("1000x700")
root.resizable(False, False)
icon_path = os.path.join(os.path.dirname(__file__), "images", "LootShade.ico")
root.iconbitmap(icon_path)

def create_placeholder_image():
    hex_bg_color = theme_settings.get("img_bg_color", "#ffffff")
    background_color = hex_to_rgb(hex_bg_color)

    placeholder = Image.new("RGBA", (150, 200), background_color)
    return ImageTk.PhotoImage(placeholder)

placeholder_image = create_placeholder_image()

images, display_name_map = load_images("images")

def display_image(event):
    if npc_listbox.curselection():
        selected_index = npc_listbox.curselection()[0]
        selected_npc, selected_world_entry, _ = npc_listbox_data[selected_index]
        image_name = selected_npc.lower()

        for display_name, filename in display_name_map.items():
            if display_name.lower() == image_name:
                full_filename = filename  
                
                if full_filename in image_cache:
                    base_img = image_cache[full_filename]
                    target_size = (150, 200)

                    background_color = theme_settings.get("img_bg_color", "#ffffff")
                    background_color_rgba = tuple(int(background_color[i:i+2], 16) for i in (1, 3, 5)) + (255,)
                    background = Image.new("RGBA", target_size, background_color_rgba)

                    img = base_img.copy()
                    img.thumbnail(target_size, Image.Resampling.LANCZOS)
                    img = ImageOps.pad(img, target_size, color=None)
                    background.paste(img, (0, 0), img)

                    photo_image = ImageTk.PhotoImage(background)
                    image_label.config(image=photo_image)
                    image_label.image = photo_image
                    get_image_info(full_filename, selected_npc, selected_world_entry['id'])
                    return

        image_label.config(image=placeholder_image)
        image_label.image = placeholder_image

search_info_frame = tk.Frame(root)
search_info_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10, expand=True)
search_info_frame.grid_columnconfigure(0, weight=1)
search_info_frame.grid_columnconfigure(1, weight=2)
search_info_frame.grid_rowconfigure(0, weight=1)

info_container_frame = tk.Frame(search_info_frame, relief="sunken")
info_container_frame.grid(row=0, column=0, sticky="nsew")

info_treeview = ttk.Treeview(info_container_frame, columns=("Attribute", "Value"), show="headings", height=18)
info_treeview.heading("Attribute", text="Attribute")
info_treeview.heading("Value", text="Value")
info_treeview.column("Attribute", width=150, anchor="w")
info_treeview.column("Value", width=100, anchor="w")

info_treeview_scrollbar = ttk.Scrollbar(info_container_frame, orient="vertical", command=info_treeview.yview)
info_treeview.configure(yscrollcommand=info_treeview_scrollbar.set)

info_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
info_treeview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

search_frame = tk.Frame(search_info_frame)
search_frame.grid(row=0, column=1, sticky="nsew")
search_info_frame.grid_columnconfigure(1, weight=2)

search_bar_frame = tk.Frame(search_frame)
search_bar_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

search_label = tk.Label(search_bar_frame, text="Search for item:")
search_label.pack(side=tk.LEFT, padx=(0, 5))
search_entry = tk.Entry(search_bar_frame)
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
search_entry.bind("<Return>", lambda event: search_items())
search_button = tk.Button(search_bar_frame, text="Search", command=search_items)
search_button.pack(side=tk.LEFT, padx=(5, 0))

def initialize_info_treeview():
    attributes = [
        "Level", "HP", "Attack", "Strength", "Defence", "Magic",
        "Att Bonus", "Str Bonus", "Range Bonus", "Stab Defence",
        "Slash Defence", "Crush Defence", "Magic Defence",
        "Range Defence", "Attack Style", "Respawn Rate", "Hunt Range",
        "Wander Range", "Max Range"
    ]
    for attribute in attributes:
        info_treeview.insert("", "end", values=(attribute, "N/A"))

initialize_info_treeview()

def get_image_info(filename, npc_name, npc_id):
    info_treeview.delete(*info_treeview.get_children())

    if npc_name not in npc_data or not npc_data[npc_name]:
        info_treeview.insert("", "end", values=("Error", "NPC not found"))
        return

    npc_entry = next((entry for entry in npc_data[npc_name] if entry['id'] == npc_id), None)

    if not npc_entry:
        info_treeview.insert("", "end", values=("Error", "No data found for this ID"))
        return

    level_options = [str(level["lvl"]) for level in npc_entry.get("levels", [])]
    level_to_entry_map = {str(level["lvl"]): npc_entry for level in npc_entry.get("levels", [])}
    level_options.sort(key=int)
    level_dropdown["menu"].delete(0, "end")

    if level_options:
        option_var.set(level_options[0])

        for level in level_options:
            level_dropdown["menu"].add_command(
                label=level, 
                command=lambda value=level: option_var.set(value)
            )

    level_dropdown.npc_name = npc_name  
    level_dropdown.npc_id = npc_id

    def update_stats(*args):
        selected_lvl = option_var.get()
        selected_npc = level_dropdown.npc_name  
        selected_id = level_dropdown.npc_id

        if selected_npc != npc_name or selected_id != npc_id:
            return

        selected_entry = level_to_entry_map.get(selected_lvl)

        if not selected_entry:
            info_treeview.insert("", "end", values=("Error", "No level data"))
            return

        selected_data = next(
            (lvl for lvl in selected_entry["levels"] if str(lvl["lvl"]) == selected_lvl),
            None
        )

        if not selected_data:
            return

        info_treeview.delete(*info_treeview.get_children())
        attributes = [
            ("Level", selected_data["lvl"]),
            ("HP", selected_data["hp"]),
            ("Attack", selected_data["att"]),
            ("Strength", selected_data["str"]),
            ("Defence", selected_data["def"]),
            ("Magic", selected_data.get("magic", 0)),
            ("Att Bonus", selected_data.get("attBo", 0)),
            ("Str Bonus", selected_data.get("strBo", 0)),
            ("Range Bonus", selected_data.get("rangeBo", 0)),
            ("Stab Defence", selected_data.get("stabDef", 0)),
            ("Slash Defence", selected_data.get("slashDef", 0)),
            ("Crush Defence", selected_data.get("crushDef", 0)),
            ("Magic Defence", selected_data.get("magicDef", 0)),
            ("Range Defence", selected_data.get("rangeDef", 0)),
            ("Attack Style", selected_data.get("attStyle", " ")),
            ("Respawn Rate", selected_data.get("respawnrate", 0)),
            ("Hunt Range", selected_data.get("huntrange", 0)),
            ("Wander Range", selected_data.get("wanderrange", 0)),
            ("Max Range", selected_data.get("maxrange", 0))
        ]
        for attribute, value in attributes:
            info_treeview.insert("", "end", values=(attribute, value))

    option_var.trace_add("write", update_stats)
    update_stats()

style = ttk.Style()

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

world_var = tk.StringVar(value=config.get("world", "F2P"))
theme_var = tk.StringVar(value=config.get("theme", "OSWiki: Day"))
show_members_var = tk.BooleanVar(value=config.get("show_members_items", True))
show_frac_var = tk.BooleanVar(value=config.get("show_drops_as_fraction", False))

worlds_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="World", menu=worlds_menu)

worlds_menu.add_radiobutton(label="F2P", variable=world_var, value="F2P", command=update_world)
worlds_menu.add_radiobutton(label="P2P", variable=world_var, value="P2P", command=update_world)

settings_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Settings", menu=settings_menu)

theme_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Theme", menu=theme_menu)

for theme_name in theme_data:
    theme_menu.add_radiobutton(
        label=f"{theme_name}", 
        variable=theme_var, 
        value=theme_name, 
        command=toggle_theme
    )

enable_profiling_var = tk.BooleanVar(value=config.get("enable_profiling", False))

def toggle_profiling():
    confirmation = messagebox.askyesno(
        "Confirm Action", 
        "Are you sure you want to enable/disable profiling? The application will restart."
    )

    if confirmation:
        config["enable_profiling"] = enable_profiling_var.get()
        save_config(config)
        restart_application()

hide_guardians_var = tk.BooleanVar(value=config.get("hide_guardians", False))
hide_drop_tables_var = tk.BooleanVar(value=config.get("hide_drop_tables", False))

settings_menu.add_checkbutton(label="Enable Profiling", variable=enable_profiling_var, command=toggle_profiling)
settings_menu.add_checkbutton(label="Show Member Items", variable=show_members_var, command=toggle_show_members)
settings_menu.add_checkbutton(label="Show drops as 1/128", variable=show_frac_var, command=toggle_rarity_display)
settings_menu.add_checkbutton(label="Hide Guardians", variable=hide_guardians_var, command=toggle_hide_guardians)
settings_menu.add_checkbutton(label="Hide Drop Tables", variable=hide_drop_tables_var, command=toggle_hide_drop_tables)

top_paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
top_paned_window.pack(fill=tk.BOTH, expand=True)

npc_listbox_frame = tk.Frame(top_paned_window)
npc_listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
npc_listbox = tk.Listbox(npc_listbox_frame, bg=theme_settings["treeview_bg"])
npc_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

def handle_npc_select(event=None):
    show_drops(event)
    display_image(event)
    if npc_listbox.curselection():
        selected_index = npc_listbox.curselection()[0]
        selected_npc, selected_world_entry, npc_id = npc_listbox_data[selected_index]
        get_image_info(None, selected_npc, npc_id)


npc_listbox.bind("<<ListboxSelect>>", handle_npc_select)

image_frame = tk.Frame(top_paned_window)
image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)

image_label = tk.Label(image_frame, image=placeholder_image, bd=2, relief=tk.SUNKEN, bg=theme_settings["img_bg_color"])
image_label.pack(fill=tk.BOTH, expand=True)

level_frame = tk.Frame(image_frame)
level_frame.pack(side=tk.TOP, pady=1)

level_label = tk.Label(level_frame, text="lvl:")
level_label.pack(side=tk.LEFT, padx=(0, 5))

option_var = tk.StringVar(value="Select Level")
level_dropdown = ttk.OptionMenu(level_frame, option_var, "Select Level")
level_dropdown.pack(side=tk.LEFT)

min_width = 5
level_dropdown.config(width=min_width)

npc_scrollbar = ttk.Scrollbar(npc_listbox_frame, orient=tk.VERTICAL, command=npc_listbox.yview)
npc_listbox.configure(yscrollcommand=npc_scrollbar.set)
npc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def adjust_drop_listbox_columns(event):
    frame_width = event.width
    num_columns = len(drop_listbox["columns"])
    column_width = frame_width // num_columns

    for col in drop_listbox["columns"]:
        drop_listbox.column(col, width=column_width)

drop_listbox_frame = tk.Frame(top_paned_window)
drop_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

drop_listbox_frame.grid_rowconfigure(0, weight=1)
drop_listbox_frame.grid_columnconfigure(0, weight=1)

drop_listbox = ttk.Treeview(drop_listbox_frame, columns=("Item", "Quantity", "Rarity"), show="headings")
drop_listbox.heading("Item", text="Item", command=lambda: sort_treeview(drop_listbox, 0))
drop_listbox.heading("Quantity", text="Quantity", command=lambda: sort_treeview(drop_listbox, 1))
drop_listbox.heading("Rarity", text="Rarity", command=lambda: sort_treeview(drop_listbox, 2))
drop_listbox.grid(row=0, column=0, sticky="nsew")

for col in drop_listbox["columns"]:
    drop_listbox.column(col, width=500, stretch=True)

drop_scrollbar = ttk.Scrollbar(drop_listbox_frame, orient=tk.VERTICAL, command=drop_listbox.yview)
drop_listbox.configure(yscrollcommand=drop_scrollbar.set)
drop_scrollbar.grid(row=0, column=1, sticky="ns")

drop_listbox_frame.bind("<Configure>", adjust_drop_listbox_columns)

def adjust_treeview_columns(event):
    tree_width = event.width
    num_columns = len(search_results["columns"])
    column_width = tree_width // num_columns
    for col in search_results["columns"]:
        search_results.column(col, width=column_width)

search_results_frame = tk.Frame(search_frame)
search_results_frame.pack(fill=tk.BOTH, expand=True)
search_results_frame.columnconfigure(0, weight=1)
search_results_frame.rowconfigure(0, weight=1)

search_results = ttk.Treeview(
    search_results_frame, columns=("NPC", "Item", "Quantity", "Rarity"), show="headings"
)
search_results.heading("NPC", text="NPC", command=lambda: sort_treeview(search_results, 0))
search_results.heading("Item", text="Item", command=lambda: sort_treeview(search_results, 1))
search_results.heading("Quantity", text="Quantity", command=lambda: sort_treeview(search_results, 2))
search_results.heading("Rarity", text="Rarity", command=lambda: sort_treeview(search_results, 3))
search_results.grid(row=0, column=0, sticky="nsew")

for col in search_results["columns"]:
    search_results.column(col, width=100, stretch=True)

search_results_scrollbar = ttk.Scrollbar(search_results_frame, orient=tk.VERTICAL, command=search_results.yview)
search_results.configure(yscrollcommand=search_results_scrollbar.set)
search_results_scrollbar.grid(row=0, column=1, sticky="ns")
search_results_frame.bind("<Configure>", adjust_treeview_columns)
search_results_scrollbar = ttk.Scrollbar(search_results_frame, orient=tk.VERTICAL, command=search_results.yview)
search_results.configure(yscrollcommand=search_results_scrollbar.set)
search_results_scrollbar.grid(row=0, column=1, sticky="ns")

def show_credits():
    credits_window = tk.Toplevel(root)
    credits_window.title("Credits")
    credits_window.geometry("300x200")
    credits_window.resizable(False, False)
    credits_window.iconbitmap(icon_path)

    credits_label = tk.Label(
        credits_window,
        text="LootShade\n\nDeveloped by Taz\n\n2025\nAll Rights Reserved",
        justify="center",
        font=("Arial", 12)
    )
    credits_label.pack(expand=True, padx=10, pady=10)

    close_button = tk.Button(
        credits_window,
        text="Close",
        command=credits_window.destroy,
        font=("Arial", 10)
    )
    close_button.pack(pady=10)

def open_discord():
    discord_link = "https://discord.gg/wKf3KTaM"
    webbrowser.open(discord_link)
def open_readme():
    readme_link = "https://github.com/SirTaz95/LootShade/blob/main/README.md"
    webbrowser.open(readme_link)
def open_faq():
    faq_link = "https://github.com/SirTaz95/LootShade/blob/main/FAQ.md"
    webbrowser.open(faq_link)
    
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
#help_menu.add_command(label="Credits", command=show_credits)
help_menu.add_command(label="Read Me", command=open_readme)
help_menu.add_command(label="FAQ", command=open_faq)
help_menu.add_command(label="Discord", command=open_discord)
help_menu.add_command(label="Submit a Bug", command=report_bug)
help_menu.add_command(label="Show Info Window", command=force_show_info_window)

npc_listbox_data = []
for npc, worlds in npc_data.items():
    for world_entry in worlds:
        npc_listbox_data.append((npc, world_entry, world_entry['id']))

npc_display_to_data = {}
for npc, world_entry, npc_id in npc_listbox_data:
    if isinstance(npc, str) and isinstance(npc_id, int):
        npc_display_to_data[npc] = (npc, npc_id)
        npc_listbox.insert(tk.END, npc)
    else:
        print(f"Skipping invalid entry: {npc}, {npc_id}")


#root.update_idletasks()
resize_panes()
toggle_theme()
refresh_drops()
show_info_window()
update_npc_list()

root.bind("<Configure>", lambda event: resize_panes_throttled())

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Script took {elapsed_time:.2f} seconds to start up.")

profile_script()
#root.mainloop()