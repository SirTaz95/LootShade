import os
import random
import json
import time
import cProfile
import pstats
from io import StringIO
from PIL import Image, ImageTk
from PIL import Image, ImageOps
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import webbrowser
from data.npc_data import npc_data

start_time = time.time()
print("Starting up...")
time.sleep(2)

def profile_script():
    profiler = cProfile.Profile()
    profiler.enable()
    root.mainloop()
    profiler.disable()
    s = StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    with open("profile_report.txt", "w") as f:
        f.write(s.getvalue())
    print("Profile report saved to 'profile_report.txt'.")

def sort_treeview(treeview, column_index):
    items = list(treeview.get_children())

    def get_sort_value(item):
        value = treeview.item(item)['values'][column_index]
        if isinstance(value, str):  
            value = value.strip()

            if value.endswith('%'):
                try:
                    return float(value.strip('%'))
                except ValueError:
                    return value
            
            try:
                return float(value)
            except ValueError:
                return value
        
        return value
    
    items.sort(key=get_sort_value)

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
                drop_listbox.insert("", "end", values=(item_name, drop.get('qty', 1), drop.get('rarity', "N/A")))
        else:
            drop_listbox.insert("", "end", values=("No drops available", "", ""))
    else:
        drop_listbox.insert("", "end", values=("No drops available", "", ""))

def search_items():
    search_term = search_entry.get().lower()
    search_results.delete(*search_results.get_children())
    selected_world = world_var.get().lower()

    results_found = False

    for npc, worlds in npc_data.items():
        for world_entry in worlds:
            if selected_world in world_entry:
                for drop in world_entry[selected_world]:
                    if search_term in drop['item'].lower() and (show_members_var.get() or not drop['members']):
                        item_name = f"★ {drop['item']}" if drop['members'] else drop['item']

                        for level_entry in world_entry.get("levels", []):
                            npc_level = level_entry.get("lvl", "N/A")
                            npc_display_name = f"{npc} (lvl-{npc_level})"
                            search_results.insert("", "end", values=(npc_display_name, item_name, drop['qty'], drop['rarity']))
                            results_found = True

    if not results_found:
        search_results.insert("", "end", values=("No results found", "", "", ""))

def refresh_drops():
    if npc_listbox.curselection():
        show_drops(None)
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

def toggle_theme():
    global theme_settings, image_cache
    current_theme = theme_var.get()

    if current_theme == "Dark":
        theme_settings.update({
            "background_color": "#2e2e2e",
            "foreground_color": "#ffffff",
            "treeview_bg": "#2e2e2e",
            "treeview_fg": "#ffffff",
            "treeview_heading_bg": "#4d4d4d",
            "treeview_heading_fg": "#ffffff",
            "img_bg_color": "#2e2e2e",
        })
    elif current_theme == "Light":
        theme_settings.update({
            "background_color": "#ffffff",
            "foreground_color": "#000000",
            "treeview_bg": "#ffffff",
            "treeview_fg": "#000000",
            "treeview_heading_bg": "#e0e0e0",
            "treeview_heading_fg": "#000000",
            "img_bg_color": "#ffffff",
        })
    else: # default "creme"
        theme_settings.update({
            "background_color": "#e2dbc8",
            "foreground_color": "#000000",
            "treeview_bg": "#d8ccb4",
            "treeview_fg": "#000000",
            "treeview_heading_bg": "#b8a282",
            "treeview_heading_fg": "#000000",
            "img_bg_color": "#d8ccb4",
        })
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

def update_world():
    refresh_drops()

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

world_var = tk.StringVar(value="F2P")
worlds_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Worlds", menu=worlds_menu)

worlds_menu.add_radiobutton(label="F2P", variable=world_var, value="F2P", command=update_world)
worlds_menu.add_radiobutton(label="P2P", variable=world_var, value="P2P", command=update_world)

settings_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Settings", menu=settings_menu)

theme_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Theme", menu=theme_menu)

theme_var = tk.StringVar(value="Creme")
theme_menu.add_radiobutton(label="Light Theme", variable=theme_var, value="Light", command=toggle_theme)
theme_menu.add_radiobutton(label="Dark Theme", variable=theme_var, value="Dark", command=toggle_theme)
theme_menu.add_radiobutton(label="Creme Theme", variable=theme_var, value="Creme", command=toggle_theme)

show_members_var = tk.BooleanVar(value=True)
settings_menu.add_checkbutton(label="Show Member Items", variable=show_members_var, command=refresh_drops)

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

help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Credits", command=show_credits)
help_menu.add_command(label="Discord", command=open_discord)

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

toggle_theme()

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Script took {elapsed_time:.2f} seconds to start up.")

# Set initial sizes
root.update_idletasks()
resize_panes()

root.bind("<Configure>", lambda event: resize_panes_throttled())

#profile_script()
root.mainloop()