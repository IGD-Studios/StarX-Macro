from PIL import Image
import requests
import time
import tkinter as tk
from tkinter import ttk
import pyperclip
import tkinter.font as tkfont
import webbrowser
import io
import base64
import os
import random
from tkinter import messagebox
from ttkthemes import ThemedTk
from PIL import ImageGrab


start_time = time.time()

def update_session_time():
    elapsed_time = time.time() - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    session_time_label.config(text=f"Session time: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    root.after(1000, update_session_time)


def minimize_window(event=None):
    root.iconify()

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

def interpolate_color(color1, color2, factor):
    return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))

def update_glitched_color():
    colors = ["#03ab00", "#ff0000", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]
    current_color = hex_to_rgb(biome_counter_labels["GLITCHED"].cget("fg"))
    target_color = hex_to_rgb(random.choice(colors))
    steps = 20
    for step in range(steps):
        factor = step / steps
        new_color = interpolate_color(current_color, target_color, factor)
        biome_counter_labels["GLITCHED"].config(fg=rgb_to_hex(new_color))
        root.update()
        root.after(50)
    root.after(100, update_glitched_color)  

def randomize_capitalization(text):
    return ''.join(random.choice([char.upper(), char.lower()]) for char in text)
def update_glitched_text():
    current_text = "GLITCHED: " + str(biome_counts["GLITCHED"])
    new_text = randomize_capitalization(current_text)
    biome_counter_labels["GLITCHED"].config(text=new_text)
    root.after(100, update_glitched_text)



def send_discord_embed(title, description, color, image_url=None):
    global last_sent_time
    current_time = time.time()
    if current_time - last_sent_time < COOLDOWN_PERIOD:
        log_message("Cooldown period active. Message not sent.")
        return

    webhook_url1 = webhook_entry1.get()
    webhook_url2 = webhook_entry2.get()
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(current_time))
    }

    if image_url:
        embed["image"] = {"url": image_url}

    data = {
        "embeds": [embed]
    }

    if webhook_url1 and webhook_url1 != 'Insert Webhook URL Here':
        response = requests.post(webhook_url1, json=data)
        if response.status_code == 204:
            log_message("Embed message sent to Discord (Webhook 1)")
        else:
            log_message(f"Failed to send embed message to Webhook 1: {response.status_code}")

    if webhook_url2 and webhook_url2 != 'Insert Webhook URL Here':
        response = requests.post(webhook_url2, json=data)
        if response.status_code == 204:
            log_message("Embed message sent to Discord (Webhook 2)")
        else:
            log_message(f"Failed to send embed message to Webhook 2: {response.status_code}")

    last_sent_time = current_time 


COOLDOWN_PERIOD = 25

last_sent_time = 0


def log_message(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + "\n")
    log_text.config(state=tk.DISABLED)
    log_text.see(tk.END)


def send_discord_message(message):
    global last_sent_time
    current_time = time.time()
    if current_time - last_sent_time < COOLDOWN_PERIOD:
        log_message("Cooldown period active. Message not sent.")
        return

    webhook_url1 = webhook_entry1.get()
    webhook_url2 = webhook_entry2.get()
    data = {
        "content": message
    }

    if webhook_url1 and webhook_url1 != 'Insert Webhook URL Here':
        response = requests.post(webhook_url1, json=data)
        if response.status_code == 204:
            log_message("Message sent to Discord (Webhook 1)")
        else:
            log_message(f"Failed to send message to Webhook 1: {response.status_code}")

    if webhook_url2 and webhook_url2 != 'Insert Webhook URL Here':
        response = requests.post(webhook_url2, json=data)
        if response.status_code == 204:
            log_message("Message sent to Discord (Webhook 2)")
        else:
            log_message(f"Failed to send message to Webhook 2: {response.status_code}")

    last_sent_time = current_time 

def get_current_biome():
    log_dir_path = os.path.expanduser("~/AppData/Local/Roblox/logs/")
    latest_log_file = None
    latest_log_time = 0


    for filename in os.listdir(log_dir_path):
        file_path = os.path.join(log_dir_path, filename)
        file_time = os.path.getmtime(file_path)
        if file_time > latest_log_time:
            latest_log_time = file_time
            latest_log_file = file_path

    if not latest_log_file:
        return None

    try:
        with open(latest_log_file, 'r', encoding='utf-8', errors='ignore') as log_file:
            logs = log_file.readlines()
            for line in reversed(logs):
                if '"largeImage":{"hoverText":"' in line:
                    biome = line.split('"largeImage":{"hoverText":"')[1].split('"')[0].strip()
                    return biome
    except FileNotFoundError:
        return None

def start_checking():
    if auto_biome_detection_var.get():
        current_biome = get_current_biome()
        if current_biome:
            embed_details = word_embeds.get(current_biome.upper())
            if embed_details:
                send_discord_embed(embed_details["title"], embed_details["description"], embed_details["color"])
                log_message(f"Detected biome: {current_biome}")
        root.after(1000, start_checking)


word_embeds = {
    "NORMAL": {"title": "Normal Biome", "description": "Native Auras : Nothing...\n-# This biome lasts until another biome appears", "color": 0x16b800},
    "SNOWY": {"title": "Snowy Biome", "description": "Native Auras : Glaciar, Permafrost, ATLAS : YUELETIDE\n-# This biome lasts for 2 minutes", "color": 0xffffff},
    "RAINY": {"title": "Rainy Biome", "description": "Native Auras : Poseidon, Sailor, Sailor : Flying Dutchman, ABYSSAL HUNTER\n-# This biome lasts for 2 minutes", "color": 0x584aff},
    "WINDY": {"title": "Windy Biome", "description": "Native Auras : Wind, Stormal, Stormal : Hurricane\n-# This biome lasts for 2 minutes", "color": 0xbafff6},
    "SANDSTORM": {"title": "Sandstorm Biome", "description": "Native Auras : Gilded, Jackpot, ATLAS\n-# This biome lasts for 10 minutes", "color": 0xffc23f},
    "HELL": {"title": "HELL Biome", "description": "Native Auras : Undead, Undead : Devil, Hades, BLOODLUST\n-# This biome lasts for 11 minutes", "color": 0xFF0000},
    "STARFALL": {"title": "Starfall Biome", "description": "Native Auras : Starlight, Star Rider, Comet, Galaxy, Starscourge, Sirius, STARSCOURGE : RADIANT, GARGANTUA\n-# This biome lasts for 10 minutes", "color": 0x4920ff},
    "CORRUPTION": {"title": "Corruption Biome", "description": "Native Auras : Hazard, Corrosive, Hazard : Rays, Astral, IMPEACHED\n-# This biome lasts for 11 minutes", "color": 0x800080},
    "NULL": {"title": "NULL Biome", "description": "Native Auras : Undefined, Nihility\n-# This biome lasts for 99 seconds", "color": 0x000000},
    "GLITCHED": {"title": "GLITCHED Biome @{glitched_role_entry}", "description": "Native Auras : Fault, Glitch, OPPRESSION\n-# This biome lasts for 164 seconds", "color": 0x03ab00},
    "DREAMSPACE": {"title": "DREAMSPACE Biome", "description": "Native Auras : ⭐, ⭐⭐, ⭐⭐⭐\n-# This biome lasts for 128 seconds", "color": 0xff9300},
}

import json


def save_data():
    data = {
        "nickname": nickname_entry.get(),
        "private_server_link": link_entry.get(),
        "webhook_url1": webhook_entry1.get(),
        "webhook_url2": webhook_entry2.get(),
        "glitched_role_id": glitched_role_entry.get(),
        "auto_biome_detection": auto_biome_detection_var.get(),
        "biome_counts": biome_counts
    }
    with open("data.json", "w") as file:
        json.dump(data, file)
    output_label.config(text="Data saved!")


def load_data():
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
            nickname_entry.delete(0, tk.END)
            nickname_entry.insert(0, data.get("nickname", ""))
            link_entry.delete(0, tk.END)
            link_entry.insert(0, data.get("private_server_link", "Insert PS Link Here"))
            webhook_entry1.delete(0, tk.END)
            webhook_entry1.insert(0, data.get("webhook_url1", "Insert Webhook URL Here"))
            webhook_entry2.delete(0, tk.END)
            webhook_entry2.insert(0, data.get("webhook_url2", "Insert Webhook URL Here"))
            glitched_role_entry.delete(0, tk.END)
            glitched_role_entry.insert(0, data.get("glitched_role_id", "Insert Role ID Here"))
    except FileNotFoundError:
        pass

root = tk.Tk()
root.title("StarX Macro V2.0")
root.geometry("435x300")
root.resizable(False, False)
root.configure(bg='darkgray')

root.bind('<F1>', minimize_window)

style = ttk.Style()
style.theme_use('clam')  
style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=5)
style.configure('TLabel', font=('Helvetica', 10), padding=5)


default_font = tkfont.Font(family="Sarpanch Bold", size=10)
root.option_add("*Font", default_font)


container = tk.Frame(root)
container.grid(row=1, column=0, sticky="nsew")

def show_frame(frame):
    frame.tkraise()

page1 = tk.Frame(container)
page2 = tk.Frame(container)
page3 = tk.Frame(container)
page4 = tk.Frame(container)
page5 = tk.Frame(container) 

for frame in (page1, page2, page3, page4, page5): 
    frame.grid(row=0, column=0, sticky="nsew")

page5 = tk.Frame(container)
page5.grid(row=0, column=0, sticky="nsew")

biome_auras = {
    "NORMAL": "Nothing...",
    "Snowy": "Permafrost , Glaciar , ATLAS : Yueltide",
    "RAINY": "Poseidon, Sailor, Sailor : Flying Dutchman, ABYSSAL HUNTER",
    "SANDSTORM": " Gilded, Jackpot, ATLAS",
    "HELL": "Undead, Undead : Devil, Hades, BLOODLUST",
    "STARFALL": "Starlight, Star Rider, Comet, Galaxy, Starscourge, Sirius, STARSCOURGE : RADIANT, GARGANTUA",
    "CORRUPTION": "Hazard, Corrosive, Hazard : Rays, Astral, IMPEACHED",
    "NULL": "UNDEFIEND , NHILITY",
    "GLITCHED": "Fault, Glitch, OPPRESSION",
    "DREAMSPACE": "⭐, ⭐⭐, ⭐⭐⭐"
}


biome_counts = {
    "NORMAL": 0,
    "SNOWY": 0,
    "RAINY": 0,
    "WINDY": 0,
    "SANDSTORM": 0,
    "HELL": 0,
    "STARFALL": 0,
    "CORRUPTION": 0,
    "NULL": 0,
    "GLITCHED": 0,
    "DREAMSPACE": 0
}

def update_biome_label():
    current_biome = get_current_biome()
    if current_biome:
        biome_label.config(text=f"Current Biome: {current_biome}")
    else:
        biome_label.config(text="Current Biome: Unknown")
    root.after(1000, update_biome_label) 

# Page 1

tk.Label(page1, text="Roblox Username    :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
nickname_entry = tk.Entry(page1, width=29)
nickname_entry.grid(row=1, column=1, padx=5, pady=5)
nickname_entry.insert(0, "")
nickname_entry.config(fg="darkgray")


tk.Label(page1, text="Private Server Link :").grid(row=2, column=0, padx=5, pady=5, sticky="w")
link_entry = tk.Entry(page1, width=29)
link_entry.grid(row=2, column=1, padx=7, pady=5)
link_entry.insert(0, "Insert PS Link Here")
link_entry.config(fg="darkgray")


tk.Label(page1, text="Select Biome            :").grid(row=3, column=0, padx=7, pady=5, sticky="w")
biome_var = tk.StringVar()
biome_dropdown = ttk.Combobox(page1, textvariable=biome_var, width=27, values=list(biome_auras.keys()))
biome_dropdown.grid(row=3, column=1, padx=7, pady=5, sticky="w")
biome_dropdown.current(0)


biome_label = tk.Label(page1, text="Current Biome: Unknown", fg="black")
biome_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)


button_frame = tk.Frame(page1)
button_frame.grid(row=6, column=0, columnspan=2, pady=10)

def reset_data():
    nickname_entry.delete(0, tk.END)
    nickname_entry.insert(0, "")
    link_entry.delete(0, tk.END)
    link_entry.insert(0, "Insert PS Link Here")
    webhook_entry1.delete(0, tk.END)
    webhook_entry1.insert(0, "Insert Webhook URL Here")
    webhook_entry2.delete(0, tk.END)
    webhook_entry2.insert(0, "Insert Webhook URL Here")
    glitched_role_entry.delete(0, tk.END)
    glitched_role_entry.insert(0, "Insert Role ID Here")
    auto_biome_detection_var.set(False)
    for biome in biome_counts:
        biome_counts[biome] = 0
    update_biome_counters()
    output_label.config(text="Data reset to default!")

def generate_started_message():
    selected_biome = biome_var.get().upper()
    embed_details = word_embeds.get(selected_biome, {"title": selected_biome, "description": "", "color": 0x000000})
    timestamp = int(time.time())
    private_server_link = link_entry.get()
    message = f"**STARX**\nBiome: {selected_biome}\nStarted: <t:{timestamp}:R>\n-# Auras: {embed_details['description']}\nPrivate Server Link: {private_server_link}"
    send_discord_embed(embed_details["title"], message, embed_details["color"])
    pyperclip.copy(message)
    output_label.config(text="Copied to clipboard!")

def generate_ended_message():
    selected_biome = biome_var.get().upper()
    embed_details = word_embeds.get(selected_biome, {"title": selected_biome, "description": "", "color": 0x000000})
    timestamp = int(time.time())
    private_server_link = link_entry.get()
    message = f"**STARX**\nEnded {selected_biome} Biome\nTimestamp: <t:{timestamp}:R>\nAuras: {embed_details['description']}\nPrivate Server Link: {private_server_link}"
    send_discord_embed(embed_details["title"], message, embed_details["color"])
    pyperclip.copy(message)
    output_label.config(text="Copied to clipboard!")

started_button = tk.Button(button_frame, text="Copy for Start", command=generate_started_message, width=23, height=1)
started_button.pack(side="left", padx=10)

ended_button = tk.Button(button_frame, text="Copy for End", command=generate_ended_message, width=23, height=1)
ended_button.pack(side="right", padx=10)


output_label = tk.Label(page1, text="", fg="darkgray")
output_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)



tk.Label(page2, text="Discord Webhook URL 1:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
webhook_entry1 = tk.Entry(page2, width=29)
webhook_entry1.grid(row=0, column=1, padx=5, pady=5, sticky="w")
webhook_entry1.insert(0, 'Insert Webhook URL Here')
webhook_entry1.config(fg='darkgray')

def on_webhook_entry1_click(event):
    if webhook_entry1.get() == 'Insert Webhook URL Here':
        webhook_entry1.delete(0, "end")  
        webhook_entry1.insert(0, '')  
        webhook_entry1.config(fg='darkgray')

def on_webhook_focusout1(event):
    if webhook_entry1.get() == '':
        webhook_entry1.insert(0, 'Insert Webhook URL Here')
        webhook_entry1.config(fg='darkgray')

webhook_entry1.bind('<FocusIn>', on_webhook_entry1_click)
webhook_entry1.bind('<FocusOut>', on_webhook_focusout1)


tk.Label(page2, text="Discord Webhook URL 2:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
webhook_entry2 = tk.Entry(page2, width=29)
webhook_entry2.grid(row=1, column=1, padx=5, pady=5, sticky="w")
webhook_entry2.insert(0, 'Insert Webhook URL Here')
webhook_entry2.config(fg='darkgray')

def on_webhook_entry2_click(event):
    if webhook_entry2.get() == 'Insert Webhook URL Here':
        webhook_entry2.delete(0, "end")  
        webhook_entry2.insert(0, '')  
        webhook_entry2.config(fg='darkgray')

def on_webhook_focusout2(event):
    if webhook_entry2.get() == '':
        webhook_entry2.insert(0, 'Insert Webhook URL Here')
        webhook_entry2.config(fg='darkgray')

webhook_entry2.bind('<FocusIn>', on_webhook_entry2_click)
webhook_entry2.bind('<FocusOut>', on_webhook_focusout2)

# Page 3 content (Logs Page)
log_frame = tk.Frame(page3)
log_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

page3.grid_columnconfigure(0, weight=1)
page3.grid_rowconfigure(0, weight=1)
log_frame.grid_columnconfigure(0, weight=1)
log_frame.grid_rowconfigure(0, weight=1)

log_text = tk.Text(log_frame, state=tk.DISABLED, width=80, height=20)
log_text.grid(row=0, column=0, sticky="nsew")

# Page 4
biome_log_frame = tk.Frame(page5)
biome_log_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

biome_counter_frame = tk.Frame(biome_log_frame)
biome_counter_frame.grid(row=0, column=0, sticky="nsew")

biome_counter_labels = {}

auto_biome_detection_var = tk.BooleanVar()
auto_biome_detection_checkbox = tk.Checkbutton(page4, text="Auto Biome Detection", variable=auto_biome_detection_var)
auto_biome_detection_checkbox.grid(row=1, column=0, padx=5, pady=5, sticky="w")



glitched_role_frame = tk.Frame(page4)
glitched_role_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

tk.Label(glitched_role_frame, text="GLITCH Biome Role ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
glitched_role_entry = tk.Entry(glitched_role_frame, width=29)
glitched_role_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
glitched_role_entry.insert(0, 'Insert Role ID Here')
glitched_role_entry.config(fg='darkgray')

def on_glitched_role_entry_click(event):
    if glitched_role_entry.get() == 'Insert Role ID Here':
        glitched_role_entry.delete(0, "end")  
        glitched_role_entry.insert(0, '')  
        glitched_role_entry.config(fg='darkgray')

def on_glitched_role_focusout(event):
    if glitched_role_entry.get() == '':
        glitched_role_entry.insert(0, 'Insert Role ID Here')
        glitched_role_entry.config(fg='darkgray')

glitched_role_entry.bind('<FocusIn>', on_glitched_role_entry_click)
glitched_role_entry.bind('<FocusOut>', on_glitched_role_focusout)

save_data_button = tk.Button(page4, text="Save Selections", command=save_data, width=20)
save_data_button.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

delete_data_button = tk.Button(page4, text="Clear Selections", command=reset_data, width=20)
delete_data_button.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
load_data()

total_biomes_label = tk.Label(biome_counter_frame, text="Total Biomes: 0")
total_biomes_label.grid(row=(len(biome_counts) // 3) + 1, column=0, columnspan=3, pady=5, sticky="w")


nav_frame = tk.Frame(root)
nav_frame.grid(row=0, column=0, pady=10)

nav_frame = tk.Frame(root, bg='darkgray')
nav_frame.grid(row=0, column=0, pady=10)

tk.Button(nav_frame, text="Main", command=lambda: show_frame(page1), bg='darkgray', fg='white').grid(row=0, column=0, padx=10)
tk.Button(nav_frame, text="Webhook", command=lambda: show_frame(page2), bg='darkgray', fg='white').grid(row=0, column=1, padx=10)
tk.Button(nav_frame, text="Logs", command=lambda: show_frame(page3), bg='darkgray', fg='white').grid(row=0, column=2, padx=10)
tk.Button(nav_frame, text="Settings", command=lambda: show_frame(page4), bg='darkgray', fg='white').grid(row=0, column=3, padx=10)
tk.Button(nav_frame, text="Biome Logs", command=lambda: show_frame(page5), bg='darkgray', fg='white').grid(row=0, column=4, padx=10)

root.grid_columnconfigure(0, weight=1)
nav_frame.grid_columnconfigure(0, weight=1)
nav_frame.grid_columnconfigure(1, weight=1)
nav_frame.grid_columnconfigure(2, weight=1)
nav_frame.grid_columnconfigure(3, weight=1)

show_frame(page1)

def toggle_auto_biome_detection():
    if auto_biome_detection_var.get():
        send_discord_message("Automatic Biome Detection On")
        log_message("Automatic Biome Detection On")
        start_checking()
    else:
        send_discord_message("Automatic Biome Detection Off")
        log_message("Automatic Biome Detection Off")

auto_biome_detection_checkbox.config(command=toggle_auto_biome_detection)

last_detected_biome = None

update_biome_label()

def update_biome_label():
    global last_detected_biome
    current_biome = get_current_biome()
    if current_biome and current_biome != last_detected_biome:
        biome_label.config(text=f"Current Biome: {current_biome}")
        if current_biome in biome_counts:
            biome_counts[current_biome] += 1
            update_biome_counters()
        last_detected_biome = current_biome
    elif not current_biome:
        biome_label.config(text="Current Biome: Unknown")
        last_detected_biome = None
    root.after(1000, update_biome_label)

def update_biome_counters():
    total_biomes = sum(biome_counts.values())
    for biome, count in biome_counts.items():
        biome_counter_labels[biome].config(text=f"{biome}: {count}")
    total_biomes_label.config(text=f"Total Biomes: {total_biomes}")

# Define the BooleanVar for aura detection
aura_detection_var = tk.BooleanVar()

# Add the Auto Aura Detection checkbox
auto_aura_detection_checkbox = tk.Checkbutton(page4, text="Auto Aura Detection", variable=aura_detection_var)
auto_aura_detection_checkbox.grid(row=2, column=0, padx=5, pady=5, sticky="w")
# Page 5

page5.grid_columnconfigure(0, weight=1)
page5.grid_rowconfigure(0, weight=1)
biome_log_frame.grid_columnconfigure(0, weight=1)
biome_log_frame.grid_rowconfigure(0, weight=1)



biome_counter_labels = {}
biome_colors = {
    "NORMAL": "#16b800",
    "SNOWY": "#ffffff",
    "RAINY": "#584aff",
    "WINDY": "#bafff6",
    "SANDSTORM": "#ffc23f",
    "HELL": "#FF0000",
    "STARFALL": "#4920ff",
    "CORRUPTION": "#800080",
    "NULL": "#000000",
    "GLITCHED": "#03ab00",
    "DREAMSPACE": "#ff9300"
}

for i, (biome, count) in enumerate(biome_counts.items()):
    row = i // 3 
    column = i % 3
    label = tk.Label(biome_counter_frame, text=f"{biome}: {count}", fg=biome_colors[biome])
    label.grid(row=row, column=column, padx=5, pady=5, sticky="w")
    biome_counter_labels[biome] = label

def toggle_auto_aura_detection():
    if aura_detection_var.get():
        send_discord_message("Automatic Aura Detection Disabled For Now")
        log_message("Automatic Aura Detection Disabled For Now")
        start_checking()
    else:
        send_discord_message("Automatic Aura Detection Disabled For Now")
        log_message("Automatic Aura Detection Disabled For Now")

auto_aura_detection_checkbox.config(command=toggle_auto_aura_detection)

hide_button2 = tk.Button(page2, text="F1 - Hide", command=minimize_window, bg='darkgray', fg='white')
hide_button2.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

hide_button3 = tk.Button(page3, text="F1 - Hide", command=minimize_window, bg='darkgray', fg='white')
hide_button3.grid(row=9, column=0, columnspan=2, pady=10, sticky="ew")

update_glitched_color()
update_glitched_text()

def on_closing():
    if messagebox.askyesno("Unsaved Settings", "Have you saved your settings?"):
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
            root.destroy()
    else:
        return
        return

root.protocol("WM_DELETE_WINDOW", on_closing)


session_time_label = tk.Label(page5, text="Session time : 00:00:00", fg='white', bg='slategray')
session_time_label.grid(row=0, column=0, columnspan=1, pady=0, sticky="w")

update_session_time()

def open_igdstudios_link(event):
    webbrowser.open_new("https://guns.lol/igdstudios")

credits_label_page2 = tk.Label(page2, text="created with love by @igdstudios <3", fg="blue", cursor="hand2")
credits_label_page2.grid(row=6, column=0, columnspan=2, pady=10)
credits_label_page2.bind("<Button-1>", open_igdstudios_link)

credits_label_page4 = tk.Label(page4, text="created with love by @igdstudios <3 ", fg="blue", cursor="hand2")
credits_label_page4.grid(row=5, column=0, columnspan=2, pady=10)
credits_label_page4.bind("<Button-1>", open_igdstudios_link)

root.mainloop()