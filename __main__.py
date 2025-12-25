import tkinter as tk
import ctypes
import os
import keyboard

# ---------------- Win32 constants ----------------
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST = 0x00000008

user32 = ctypes.windll.user32

BOUNDS_FILE = "window_bounds.txt"

# ---------------- Load saved bounds ----------------
def load_bounds():
    if not os.path.exists(BOUNDS_FILE):
        return None
    try:
        with open(BOUNDS_FILE, "r") as f:
            x, y, w, h = map(int, f.read().split(","))
            return w, h, x, y
    except Exception:
        return None

saved = load_bounds()
default_geometry = "400x300+500+300"
geometry = f"{saved[0]}x{saved[1]}+{saved[2]}+{saved[3]}" if saved else default_geometry

# ---------------- Window ----------------
root = tk.Tk()
root.overrideredirect(True)
root.geometry(geometry)
root.configure(bg="pink")
root.wm_attributes("-transparentcolor", "pink")
root.wm_attributes("-alpha", 0.3)   # <<< semi-transparent outline
root.wm_attributes("-topmost", True)

root.update_idletasks()
hwnd = user32.GetParent(root.winfo_id())

def set_clickthrough(enabled: bool):
    styles = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    if enabled:
        styles |= WS_EX_TRANSPARENT
    else:
        styles &= ~WS_EX_TRANSPARENT
    user32.SetWindowLongW(
        hwnd,
        GWL_EXSTYLE,
        styles | WS_EX_LAYERED | WS_EX_TOPMOST
    )

set_clickthrough(True)

# ---------------- Canvas + border ----------------
canvas = tk.Canvas(root, bg="pink", highlightthickness=0)
canvas.pack(fill="both", expand=True)

BORDER = 2
MIN_W, MIN_H = 120, 80

def redraw_border():
    canvas.delete("border")
    w, h = root.winfo_width(), root.winfo_height()
    canvas.create_rectangle(
        BORDER//2, BORDER//2,
        w - BORDER//2, h - BORDER//2,
        outline="red",
        width=BORDER,
        tags="border"
    )

root.bind("<Configure>", lambda e: redraw_border())
redraw_border()

# ---------------- Resize handles ----------------
HANDLE = 12
handles = []
handles_visible = False

resize_state = {}

def start_resize(event, mode):
    resize_state.update({
        "x": event.x_root,
        "y": event.y_root,
        "w": root.winfo_width(),
        "h": root.winfo_height(),
        "wx": root.winfo_x(),
        "wy": root.winfo_y(),
        "mode": mode
    })

def do_resize(event):
    dx = event.x_root - resize_state["x"]
    dy = event.y_root - resize_state["y"]

    w, h = resize_state["w"], resize_state["h"]
    x, y = resize_state["wx"], resize_state["wy"]
    m = resize_state["mode"]

    if "e" in m: w += dx
    if "s" in m: h += dy
    if "w" in m:
        w -= dx
        x += dx
    if "n" in m:
        h -= dy
        y += dy

    w = max(MIN_W, w)
    h = max(MIN_H, h)

    root.geometry(f"{int(w)}x{int(h)}+{int(x)}+{int(y)}")

def make_handle(cursor, mode):
    f = tk.Frame(root, bg="black", width=HANDLE, height=HANDLE, cursor=cursor)
    f.bind("<Button-1>", lambda e, m=mode: start_resize(e, m))
    f.bind("<B1-Motion>", do_resize)
    handles.append(f)

make_handle("size_nw_se", "nw")
make_handle("size_ns",    "n")
make_handle("size_ne_sw", "ne")
make_handle("size_we",    "w")
make_handle("size_we",    "e")
make_handle("size_ne_sw", "sw")
make_handle("size_ns",    "s")
make_handle("size_nw_se", "se")

def place_handles():
    w, h = root.winfo_width(), root.winfo_height()
    coords = [
        (0, 0), (w//2, 0), (w, 0),
        (0, h//2), (w, h//2),
        (0, h), (w//2, h), (w, h)
    ]
    for hndl, (x, y) in zip(handles, coords):
        hndl.place(x=x-HANDLE//2, y=y-HANDLE//2)

# ---------------- Toggle resize mode ----------------
def toggle_resize(event=None):
    global handles_visible
    handles_visible = not handles_visible

    if handles_visible:
        set_clickthrough(False)
        for h in handles:
            h.place(x=0, y=0)
        place_handles()
    else:
        for h in handles:
            h.place_forget()
        set_clickthrough(True)

# root.bind_all("<Alt-w>", toggle_resize)
# root.bind_all("<Alt-W>", toggle_resize)

# ---------------- Save bounds (Alt + S) ----------------
def save_bounds(event=None):
    x = root.winfo_x()
    y = root.winfo_y()
    w = root.winfo_width()
    h = root.winfo_height()
    with open(BOUNDS_FILE, "w") as f:
        f.write(f"{x},{y},{w},{h}")
    print("Bounds saved")

# root.bind_all("<Alt-s>", save_bounds)
# root.bind_all("<Alt-S>", save_bounds)

def close_window(event=None):
    root.destroy()

# root.bind_all("<Alt-x>", close_window)
# root.bind_all("<Alt-X>", close_window)


# ---------------- Start ----------------
def start():
    keyboard.add_hotkey("alt+o", toggle_resize)
    keyboard.add_hotkey("alt+k", save_bounds)
    keyboard.add_hotkey("alt+m", close_window)
    root.mainloop()

start()
