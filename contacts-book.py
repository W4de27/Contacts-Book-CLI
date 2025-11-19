#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contacts Book — Refactored & improved
Author: refactor by ChatGPT for W4de27's original
Features:
 - JSON persistent storage (contacts.json in script dir)
 - Unicode icons for UI (works in terminals)
 - Optional color output via colorama (auto-fallback)
 - Robust validation, safer save, tidy UX
"""

from pathlib import Path
import json
import re
import sys
import time
import tempfile
import os

# ---------- Configuration ----------
BASE_PATH = Path(__file__).resolve().parent
JSON_PATH = BASE_PATH / "contacts.json"

# UI timing (seconds). Keep small so UX is snappy.
_SHORT = 0.6
_MED = 1.0

# ---------- Optional color support ----------
try:
    from colorama import init as _color_init, Fore, Style
    _color_init(autoreset=True)
    COLOR_OK = Fore.GREEN + Style.BRIGHT
    COLOR_WARN = Fore.YELLOW + Style.BRIGHT
    COLOR_ERR = Fore.RED + Style.BRIGHT
    COLOR_INFO = Fore.CYAN + Style.BRIGHT
except Exception:
    COLOR_OK = COLOR_WARN = COLOR_ERR = COLOR_INFO = ""
    Style = type("S", (), {"RESET_ALL": ""})  # minimal fallback

# ---------- Icons ----------
ICON_ADD = "➕"
ICON_SEARCH = "🔎"
ICON_DELETE = "🗑️"
ICON_UPDATE = "✏️"
ICON_LIST = "📋"
ICON_CLEAR = "⚠️"
ICON_EXIT = "✅"
ICON_OK = "✔️"
ICON_FAIL = "❌"
ICON_WAIT = "⏳"
ICON_EMAIL = "✉️"
ICON_PHONE = "📞"
ICON_USER = "👤"
ICON_WARN = "🚨"

# ---------- Validators ----------
PHONE_RE = re.compile(r'^\d{10}$')  # keep 10-digit rule as original
EMAIL_RE = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

def is_valid_phone(p: str) -> bool:
    return bool(PHONE_RE.match(p))

def is_valid_email(e: str) -> bool:
    return bool(EMAIL_RE.match(e) or e == "")

# ---------- IO helpers ----------
def safe_load_contacts() -> dict:
    if not JSON_PATH.exists():
        return {}
    try:
        with JSON_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f) or {}
            if isinstance(data, dict):
                return data
    except (json.JSONDecodeError, IOError):
        pass
    return {}

def safe_save_contacts(data: dict) -> None:
    # atomic write to avoid corruption
    try:
        tmp_fd, tmp_path = tempfile.mkstemp(dir=str(BASE_PATH))
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=4)
        Path(tmp_path).replace(JSON_PATH)
    except Exception as e:
        print(f"\n{COLOR_ERR}{ICON_FAIL} ERROR saving contacts: {e}{Style.RESET_ALL}")
        time.sleep(_MED)
        pause()

# ---------- Small UI helpers ----------


def pause(msg: str = "Press Enter to continue..."):
    print()
    input(msg)

def print_info(text: str):
    print(f"{COLOR_INFO}{ICON_WAIT} {text}{Style.RESET_ALL}")

def print_ok(text: str):
    print(f"{COLOR_OK}{ICON_OK} {text}{Style.RESET_ALL}")

def print_warn(text: str):
    print(f"{COLOR_WARN}{ICON_WARN} {text}{Style.RESET_ALL}")

def print_err(text: str):
    print(f"{COLOR_ERR}{ICON_FAIL} {text}{Style.RESET_ALL}")

def anim_dots(word="Processing", repeats=3, delay=0.4):
    for i in range(repeats):
        dots = "." * ((i % 3) + 1)
        print(f"\r{word}{dots}   ", end="", flush=True)
        time.sleep(delay)
    print("\r", end="")




# ---------- Core actions ----------
def add_contact():
    contacts = safe_load_contacts()
    print()
    print(f"{ICON_ADD}  Add New Contact")
    print("-" * 36)
    name = input("Name: ").strip()
    if not name:
        anim_dots("Checking")
        print_err("Name required!")
        pause()
        return

    phone = input("Phone (10 digits): ").strip()
    if not phone:
        anim_dots("Checking")
        print_err("Phone required!")
        pause()
        return
    if not is_valid_phone(phone):
        anim_dots("Checking")
        print_err("Phone must be 10 digits only!")
        pause()
        return
    if phone in contacts:
        anim_dots("Checking")
        print_err("Phone already exists!")
        pause()
        return

    email = input("Email (optional): ").strip()
    if email and not is_valid_email(email):
        anim_dots("Checking")
        print_err("Invalid email format!")
        pause()
        return

    anim_dots("Saving", 2)
    contacts[phone] = {"name": name.strip().title(), "email": email}
    safe_save_contacts(contacts)
    print_ok("Contact added successfully!")
    time.sleep(_SHORT)
    pause()

def _print_contact_block(index, phone, info):
    print("=" * 36)
    print(f"[{index}] {ICON_USER} {info.get('name','N/A')}")
    print(f"    {ICON_PHONE} Phone: {phone}")
    email = info.get("email") or "—"
    print(f"    {ICON_EMAIL}  Email: {email}")
    print("-" * 36)

def list_contacts():
    contacts = safe_load_contacts()
    print(f"{ICON_LIST}  Contact List")
    print("-" * 36)
    if not contacts:
        print_warn("No contacts found. Add your first contact!")
        time.sleep(_SHORT)
        pause()
        return
    # sort by name for friendly listing
    items = sorted(contacts.items(), key=lambda kv: kv[1].get("name","").lower())
    for i, (phone, info) in enumerate(items, start=1):
        _print_contact_block(i, phone, info)
        time.sleep(0.5)
    print_ok(f" End of list — Total: {len(items)}")
    pause()

def search_contact():
    contacts = safe_load_contacts()
    print()
    print(f"{ICON_SEARCH}  Search Contacts")
    print("-" * 36)
    if not contacts:
        print_warn("No contacts to search.")
        time.sleep(_SHORT)
        pause()
        return
    print("1) By Phone")
    print("2) By Name")
    print("3) By Email")
    print("4) Cancel")
    print()
    choice = input("Choice (1-4): ").strip()
    if choice not in {"1","2","3","4"}:
        anim_dots("Checking")
        print_err("Invalid choice!")
        pause()
        return
    if choice == "4":
        anim_dots("Cancelling")
        print_warn("Search cancelled.")
        pause()
        return

    if choice == "1":
        q = input("Enter phone (10 digits): ").strip()
        if not is_valid_phone(q):
            anim_dots("Checking")
            print_err("Invalid phone!")
            pause()
            return
        res = [(p,v) for p,v in contacts.items() if p == q]

    elif choice == "2":
        q = input("Enter name: ").strip().lower()
        if not q:
            anim_dots("Checking")
            print_err("Name required!")
            pause()
            return
        res = [(p,v) for p,v in contacts.items() if v.get("name","").lower() == q]

    else:  # email
        q = input("Enter email: ").strip().lower()
        if not is_valid_email(q) or not q == "":
            anim_dots("Checking")
            print_err("Invalid email!")
            pause()
            return
        res = [(p,v) for p,v in contacts.items() if (v.get("email") or "").lower() == q]

    if not res:
        print_err("No contact found.")
        time.sleep(_SHORT)
        pause()
        return

    print()
    for i, (phone, info) in enumerate(res, start=1):
        _print_contact_block(i, phone, info)
        time.sleep(0.6)
    pause()

def delete_contact():
    contacts = safe_load_contacts()
    print()
    print(f"{ICON_DELETE}  Delete Contact")
    print("-" * 36)
    if not contacts:
        print_warn("No contacts to delete.")
        time.sleep(_SHORT)
        pause()
        return
    print("1) By Phone")
    print("2) By Name")
    print("3) By Email")
    print("4) Cancel")
    print()
    choice = input("Choice (1-4): ").strip()
    if choice not in {"1","2","3","4"}:
        anim_dots("Checking")
        print_err("Invalid choice!")
        pause()
        return
    if choice == "4":
        anim_dots("Cancelling")
        print_warn("Delete cancelled.")
        pause()
        return

    if choice == "1":
        q = input("Phone (10 digits): ").strip()
        if not is_valid_phone(q):
            anim_dots("Checking")
            print_err("Invalid phone!")
            pause()
            return
        matches = {p:v for p,v in contacts.items() if p == q}

    elif choice == "2":
        q = input("Name: ").strip().lower()
        if not q:
            anim_dots("Checking")
            print_err("Name required!")
            pause()
            return
        matches = {p:v for p,v in contacts.items() if v.get("name","").lower() == q}

    else:
        q = input("Email: ").strip().lower()
        if not is_valid_email(q) or not q == "":
            anim_dots("Checking")
            print_err("Invalid email!")
            pause()
            return
        matches = {p:v for p,v in contacts.items() if (v.get("email") or "").lower() == q}

    if not matches:
        print_err("No matching contact found.")
        time.sleep(_SHORT)
        pause()
        return

    # Show matches
    print()
    items = list(matches.items())
    print("=" * 40)
    for i, (phone, info) in enumerate(items, start=1):
        print(f"[{i}] {info.get('name')} — {phone}")
    print("=" * 40)
    
    print()
    if len(items) == 1:
        confirm = input("Delete this contact? (yes/no): ").strip().lower()
        if confirm != "yes":
            anim_dots("Cancelling")
            print_warn("Delete cancelled.")
            pause()
            return
        contacts.pop(items[0][0], None)
    else:
        try:
            sel = int(input(f"Select contact number to delete (1-{len(items)}): ").strip())
            if not (1 <= sel <= len(items)):
                print_err("Invalid selection!")
                pause()
                return
            contacts.pop(items[sel-1][0], None)
        except ValueError:
            print_err("Please enter a valid number!")
            pause()
            return
    safe_save_contacts(contacts)
    print_ok("Contact deleted.")
    time.sleep(_SHORT)
    pause()

def update_contact():
    contacts = safe_load_contacts()
    print()
    print(f"{ICON_UPDATE}  Update Contact")
    print("-" * 36)
    if not contacts:
        print_warn("No contacts to update.")
        time.sleep(_SHORT)
        pause()
        return
    # Find contact first
    print("Find contact by:")
    print("-" * 20)
    print("1) Phone")
    print("2) Name")
    print("3) Email")
    print("4) Cancel")
    print()
    ch = input("Choice (1-4): ").strip()
    if ch not in {"1","2","3","4"}:
        anim_dots("Checking")
        print_err("Invalid choice!")
        pause()
        return
    if ch == "4":
        anim_dots("Cancelling")
        print_warn("Update cancelled.")
        pause()
        return

    if ch == "1":
        q = input("Phone (10 digits): ").strip()
        if not is_valid_phone(q):
            anim_dots("Checking")
            print_err("Invalid phone!")
            pause()
            return
        matches = {p:v for p,v in contacts.items() if p == q}
    elif ch == "2":
        q = input("Name: ").strip().lower()
        if not q:
            anim_dots("Checking")
            print_err("Name required!")
            pause()
            return
        matches = {p:v for p,v in contacts.items() if v.get("name","").lower() == q}
    else:
        q = input("Email: ").strip().lower()
        if not is_valid_email(q) or not q == "":
            anim_dots("Checking")
            print_err("Invalid email!")
            pause()
            return
        matches = {p:v for p,v in contacts.items() if (v.get("email") or "").lower() == q}

    if not matches:
        print_err("No contact found.")
        time.sleep(_SHORT)
        pause()
        return

    print()
    items = list(matches.items())
    if len(items) == 1:
        phone_sel = items[0][0]
    else:
        print("=" * 40)
        for i, (phone, info) in enumerate(items, start=1):
            print(f"[{i}] {info.get('name')} — {phone}")
        print("=" * 40)
        print()
        try:
            sel = int(input(f"Select contact number to update (1-{len(items)}): ").strip())
            if not (1 <= sel <= len(items)):
                print_err("Invalid selection!")
                pause()
                return
            phone_sel = items[sel-1][0]
        except ValueError:
            print_err("Please enter a valid number!")
            pause()
            return

    # Now update fields
    print("-" * 36)
    print("Fields to update:")
    print("1) Phone")
    print("2) Name")
    print("3) Email")
    print("4) Cancel")
    print()
    fld = input("Choice (1-4): ").strip()
    if fld not in {"1","2","3","4"}:
        anim_dots("Checking")
        print_err("Invalid choice!")
        pause()
        return
    if fld == "4":
        anim_dots("Cancelling")
        print_warn("Update cancelled.")
        pause()
        return

    if fld == "1":
        new_phone = input("New phone (10 digits): ").strip()
        if not is_valid_phone(new_phone):
            anim_dots("Checking")
            print_err("Invalid phone!")
            pause()
            return
        if new_phone in contacts and new_phone != phone_sel:
            anim_dots("Checking")
            print_err("Phone already exists!")
            pause()
            return
        contacts[new_phone] = contacts.pop(phone_sel)
    elif fld == "2":
        new_name = input("New name: ").strip()
        if not new_name:
            anim_dots("Checking")
            print_err("Name required!")
            pause()
            return
        contacts[phone_sel]["name"] = new_name.title()
    else:
        new_email = input("New email (leave blank to clear): ").strip()
        if new_email and not is_valid_email(new_email):
            anim_dots("Checking")
            print_err("Invalid email!")
            pause()
            return
        contacts[phone_sel]["email"] = new_email

    safe_save_contacts(contacts)
    print_ok(" Contact updated.")
    time.sleep(_SHORT)
    pause()

def clear_all_contacts():
    contacts = safe_load_contacts()
    print(f"{ICON_CLEAR}  Clear All Contacts")
    print("-" * 36)
    if not contacts:
        print_warn("No contacts to clear.")
        time.sleep(_SHORT)
        pause()
        return
    print_warn("WARNING: This will permanently delete ALL contacts!")
    confirm = input("Type 'confirm' to delete everything, or anything else to cancel: ").strip().lower()
    print()
    if confirm != "confirm":
        print_warn("Clear cancelled.")
        return
    safe_save_contacts({})
    print_ok("All contacts removed.")
    time.sleep(_SHORT)
    pause()

# ---------- Main menu ----------
def main():
    # small start banner
    print()
    print("=" * 48)
    print(f"{'CONTACTS BOOK — Simple CLI':^48}")
    print("=" * 48)
    time.sleep(0.4)

    while True:
        print()
        print("----- Contact Book Menu -----")
        print()
        print(f"1. {ICON_ADD}  Add New Contact")
        print(f"2. {ICON_SEARCH}  Search For Contact")
        print(f"3. {ICON_DELETE}   Delete Contact")
        print(f"4. {ICON_UPDATE}   Update Contact")
        print(f"5. {ICON_LIST}  List Contacts")
        print(f"6. {ICON_CLEAR}   Clear All Contacts")
        print(f"7. {ICON_EXIT}  Exit")
        print("-----------------------------")
        choice = input("Enter a valid choice (1-7): ").strip()
        if choice == "1":
            add_contact()
        elif choice == "2":
            search_contact()
        elif choice == "3":
            delete_contact()
        elif choice == "4":
            update_contact()
        elif choice == "5":
            list_contacts()
        elif choice == "6":
            clear_all_contacts()
        elif choice == "7":
            print("\n" + "=" * 45)
            print_ok(" Thank you for using Contacts Book — Bye!")
            print("=" * 45)
            time.sleep(0.6)
            sys.exit(0)
        else:
            anim_dots("Checking")
            print_err("Invalid choice — try again.")
            time.sleep(0.6)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram closed by user. Goodbye!\n")
