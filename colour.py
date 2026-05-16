"""
Colour Inspector  —  Professional Edition
==========================================
• Image fits window like Windows Photos (scale-to-fit, centred, no scroll)
• Info bar always docked at bottom with horizontal scrollbar if too narrow
• Color name never overflows — auto-truncated with ellipsis
• RGB bars dynamically resize with window width
• Buttons: Upload Another Image  |  Close
• Crosshair repositions correctly on window resize
• Esc or Close button to quit
"""

import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, ttk
import tkinter.font as tkfont

# ══════════════════════════════════════════════════════════════════════════════
#  Dataset (loaded once at startup)
# ══════════════════════════════════════════════════════════════════════════════
DATASET = (
    r"C:\Users\PMYLS\OneDrive - Higher Education Commission"
    r"\Desktop\habibaa\project AI\venv\color_detection\colors_dataset.csv"
)
_df = pd.read_csv(
    DATASET, names=["color", "color_name", "hex", "R", "G", "B"], header=None)
CSV_R = _df["R"].to_numpy(np.int32)
CSV_G = _df["G"].to_numpy(np.int32)
CSV_B = _df["B"].to_numpy(np.int32)
CSV_NAME = _df["color_name"].to_numpy()


def nearest_color(R, G, B):
    d = np.abs(CSV_R - R) + np.abs(CSV_G - G) + np.abs(CSV_B - B)
    return str(CSV_NAME[np.argmin(d)])


# ══════════════════════════════════════════════════════════════════════════════
#  App
# ══════════════════════════════════════════════════════════════════════════════
class ColorInspector:

    # ── Design tokens ─────────────────────────────────────────────────────────
    BG = '#0E1016'
    CANVAS_BG = '#14161D'
    SEP = '#252738'
    TXT_PRI = '#E8E9F0'
    TXT_SEC = '#7C7E96'
    TXT_HEX = '#4ECBA8'
    BADGE_BG = '#1C1E2E'
    TRACK = '#282A40'
    BAR_R = '#E05555'
    BAR_G = '#45C96A'
    BAR_B = '#4A90E2'
    SWATCH_BDR = '#9090A8'
    BTN_UPL_BG = '#1A1C2C'
    BTN_UPL_FG = '#8090C0'
    BTN_UPL_HV = '#262840'
    BTN_CLO_BG = '#2A1010'
    BTN_CLO_FG = '#E05555'
    BTN_CLO_HV = '#3A1515'

    INFO_H = 150   # info bar height — fixed
    BTN_H = 38    # button row height — fixed

    # Info bar layout — absolute x positions inside the bar
    PAD = 14
    SW_W = 110   # swatch width
    TX = 14 + 110 + 18   # text column x  =  142
    # RGB bars start x  =  262  (TX + name column width)
    BAR_X = 142 + 120

    def __init__(self, initial_path: str):
        self.root = tk.Tk()
        self.root.title(
            "Color Inspector  |  Double-click to sample  |  Esc to quit")
        self.root.configure(bg=self.BG)
        self.root.minsize(520, 380)

        # Image state
        self.img_bgr = None
        self.img_pil = None
        self.IMG_W = 0
        self.IMG_H = 0
        self._photo = None      # keep reference so GC doesn't collect it
        self._scale = 1.0
        self._off_x = 0
        self._off_y = 0
        self._crosshair = []
        self._last = {}        # last sampled colour info

        self._build_ui()
        self._load_image(initial_path)
        self.root.bind("<Escape>", lambda _: self.root.destroy())
        self.root.mainloop()

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # Fonts (must be created after Tk root exists)
        self._fn_name = tkfont.Font(family='Segoe UI',  size=14, weight='bold')
        self._fn_hex = tkfont.Font(family='Consolas',  size=11, weight='bold')
        self._fn_lbl = tkfont.Font(family='Consolas',  size=10)
        self._fn_sm = tkfont.Font(family='Segoe UI',  size=9)
        self._fn_hint = tkfont.Font(family='Segoe UI',  size=12)
        self._fn_btn = tkfont.Font(family='Segoe UI',  size=10)

        # ── Image canvas (fills all space above the button row) ───────────────
        self.img_cv = tk.Canvas(
            self.root, bg=self.CANVAS_BG,
            highlightthickness=0, cursor='crosshair'
        )
        self.img_cv.pack(fill=tk.BOTH, expand=True)
        self.img_cv.bind("<Configure>",        self._on_canvas_resize)
        self.img_cv.bind("<Double-Button-1>",  self._on_click)

        # ── Separator ─────────────────────────────────────────────────────────
        tk.Frame(self.root, height=2, bg=self.SEP).pack(fill=tk.X)

        # ── Button row ────────────────────────────────────────────────────────
        btn_row = tk.Frame(self.root, bg='#0A0C12', height=self.BTN_H)
        btn_row.pack(fill=tk.X)
        btn_row.pack_propagate(False)

        def _hover(btn, bg_in, bg_out):
            btn.bind("<Enter>", lambda _: btn.config(bg=bg_in))
            btn.bind("<Leave>", lambda _: btn.config(bg=bg_out))

        self._btn_upload = tk.Button(
            btn_row, text="⬆   Upload Image",
            bg=self.BTN_UPL_BG, fg=self.BTN_UPL_FG,
            activebackground=self.BTN_UPL_HV, activeforeground='#C0D0FF',
            relief=tk.FLAT, font=self._fn_btn,
            cursor='hand2', padx=16, pady=6,
            command=self._upload_new
        )
        self._btn_upload.pack(side=tk.RIGHT, padx=(4, 8), pady=5)
        _hover(self._btn_upload, self.BTN_UPL_HV, self.BTN_UPL_BG)

        self._btn_close = tk.Button(
            btn_row, text="✕   Close",
            bg=self.BTN_CLO_BG, fg=self.BTN_CLO_FG,
            activebackground=self.BTN_CLO_HV, activeforeground='#FF8888',
            relief=tk.FLAT, font=self._fn_btn,
            cursor='hand2', padx=16, pady=6,
            command=self.root.destroy
        )
        self._btn_close.pack(side=tk.RIGHT, padx=(4, 2), pady=5)
        _hover(self._btn_close, self.BTN_CLO_HV, self.BTN_CLO_BG)

        # Label on left side of button row
        tk.Label(
            btn_row, text="  Double-click on image to sample colour",
            bg='#0A0C12', fg='#44465E', font=self._fn_sm
        ).pack(side=tk.LEFT, padx=10)

        # ── Separator ─────────────────────────────────────────────────────────
        tk.Frame(self.root, height=1, bg=self.SEP).pack(fill=tk.X)

        # ── Info bar — fixed height, no scrollbar (BAR_W is dynamic) ──────────
        self.info_cv = tk.Canvas(
            self.root, height=self.INFO_H,
            bg=self.BG, highlightthickness=0
        )
        self.info_cv.pack(fill=tk.X)
        self.info_cv.bind("<Configure>", self._on_info_resize)

        # Show placeholder
        self.root.after(80, self._show_placeholder)

    # ── Image loading ─────────────────────────────────────────────────────────
    def _load_image(self, path: str):
        bgr = cv2.imread(path)
        if bgr is None:
            return
        self.img_bgr = bgr
        self.img_pil = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        self.IMG_H, self.IMG_W = bgr.shape[:2]
        self._last = {}
        self._crosshair = []

        # Size window to fit image (capped at screen)
        SCR_W = self.root.winfo_screenwidth()
        SCR_H = self.root.winfo_screenheight()
        extra = self.BTN_H + self.INFO_H + 20   # buttons + info + separators
        win_w = min(max(self.IMG_W, 520), SCR_W - 40)
        win_h = min(self.IMG_H + extra, SCR_H - 80)
        ox = max(0, (SCR_W - win_w) // 2)
        oy = max(0, (SCR_H - win_h) // 2)
        self.root.geometry(f"{win_w}x{win_h}+{ox}+{oy}")

        self.root.after(60, self._refresh_canvas)
        self._show_placeholder()

    def _upload_new(self):
        path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff")]
        )
        if path:
            self._load_image(path)

    # ── Canvas image rendering ────────────────────────────────────────────────
    def _refresh_canvas(self):
        self.img_cv.update_idletasks()
        self._render_canvas_image()

    def _render_canvas_image(self):
        if self.img_pil is None:
            return
        cw = self.img_cv.winfo_width()
        ch = self.img_cv.winfo_height()
        if cw < 2 or ch < 2:
            return

        # Scale to fit while preserving aspect ratio
        scale = min(cw / self.IMG_W, ch / self.IMG_H)
        nw = max(1, int(self.IMG_W * scale))
        nh = max(1, int(self.IMG_H * scale))
        self._scale = scale
        self._off_x = (cw - nw) // 2
        self._off_y = (ch - nh) // 2

        resized = self.img_pil.resize((nw, nh), Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(resized)
        self.img_cv.delete("img")
        self.img_cv.create_image(
            self._off_x, self._off_y,
            anchor=tk.NW, image=self._photo, tags="img"
        )
        # Reposition crosshair after resize
        if self._last:
            self._draw_crosshair(
                int(self._last['px'] * self._scale + self._off_x),
                int(self._last['py'] * self._scale + self._off_y)
            )

    def _on_canvas_resize(self, _event):
        self._render_canvas_image()

    # ── Click handler ─────────────────────────────────────────────────────────
    def _on_click(self, event):
        if self.img_bgr is None:
            return
        # Widget coords → image pixel coords
        ix = int((event.x - self._off_x) / self._scale)
        iy = int((event.y - self._off_y) / self._scale)
        ix = max(0, min(ix, self.IMG_W - 1))
        iy = max(0, min(iy, self.IMG_H - 1))

        b_, g_, r_ = self.img_bgr[iy, ix]
        r, g, b = int(r_), int(g_), int(b_)
        name = nearest_color(r, g, b)
        hex_ = f"#{r:02X}{g:02X}{b:02X}"

        self._last = dict(r=r, g=g, b=b, name=name, hex=hex_, px=ix, py=iy)
        self._render_info()
        self._draw_crosshair(event.x, event.y)

        tot = max(r + g + b, 1)
        print(f"  {name:30s}  {hex_}  R={r:3d} G={g:3d} B={b:3d}  "
              f"R={r/tot*100:.1f}%  G={g/tot*100:.1f}%  B={b/tot*100:.1f}%")

    # ── Crosshair ─────────────────────────────────────────────────────────────
    def _draw_crosshair(self, cx, cy):
        for cid in self._crosshair:
            self.img_cv.delete(cid)
        A = 13
        self._crosshair = [
            self.img_cv.create_line(
                cx-A, cy,   cx+A, cy,   fill='#000000', width=2),
            self.img_cv.create_line(
                cx,   cy-A, cx,   cy+A, fill='#000000', width=2),
            self.img_cv.create_line(
                cx-A, cy,   cx+A, cy,   fill='#FFFFFF', width=1),
            self.img_cv.create_line(
                cx,   cy-A, cx,   cy+A, fill='#FFFFFF', width=1),
            self.img_cv.create_oval(
                cx-4, cy-4, cx+4, cy+4, outline='#FFFFFF', width=1),
        ]

    # ── Info bar rendering ────────────────────────────────────────────────────
    def _show_placeholder(self):
        self.info_cv.delete("all")
        self.info_cv.update_idletasks()
        W = max(self.info_cv.winfo_width(), 520)
        self.info_cv.create_text(
            W // 2, self.INFO_H // 2,
            text="Double-click on any pixel in the image to inspect its colour",
            fill='#44465E', font=self._fn_hint
        )

    def _on_info_resize(self, _event):
        if self._last:
            self._render_info()
        else:
            self._show_placeholder()

    def _render_info(self):
        if not self._last:
            return
        d = self._last
        r, g, b = d['r'], d['g'], d['b']
        name, hex_val = d['name'], d['hex']
        px,  py = d['px'],  d['py']

        self.info_cv.delete("all")
        W = max(self.info_cv.winfo_width(), 520)
        H = self.INFO_H
        PAD = self.PAD

        # ── Colour swatch ────────────────────────────────────────────────────
        sc = f'#{r:02X}{g:02X}{b:02X}'
        self.info_cv.create_rectangle(
            PAD, PAD, PAD + self.SW_W, H - PAD,
            fill=sc, outline=self.SWATCH_BDR, width=1
        )

        TX = self.TX

        # ── Colour name — ALWAYS shown in full ───────────────────────────────
        name_w = self._fn_name.measure(name)
        self.info_cv.create_text(
            TX, PAD + 18,
            text=name, anchor=tk.W,
            fill=self.TXT_PRI, font=self._fn_name
        )

        # ── Hex badge ─────────────────────────────────────────────────────────
        BY1 = PAD + 36
        BY2 = PAD + 60
        hex_w = self._fn_hex.measure(hex_val)
        BX2 = TX + hex_w + 18
        self.info_cv.create_rectangle(TX, BY1, BX2, BY2,
                                      fill=self.BADGE_BG, outline='')
        self.info_cv.create_text(
            TX + 8, (BY1 + BY2) // 2,
            text=hex_val, anchor=tk.W,
            fill=self.TXT_HEX, font=self._fn_hex
        )

        # ── Pixel position ────────────────────────────────────────────────────
        self.info_cv.create_text(
            TX, H - PAD - 4,
            text=f"Pixel  ({px}, {py})", anchor=tk.W,
            fill=self.TXT_SEC, font=self._fn_sm
        )

        # ── RGB bars — start AFTER the name/badge column, use remaining space ─
        # Gap of 20px after whichever is wider: the colour name or the hex badge
        # 44 = 22 (label width) + 22 gap
        text_col_w = max(name_w, hex_w + 18) + 44
        BAR_X = TX + text_col_w
        BAR_W = max(W - BAR_X - 62, 60)   # remaining space, min 60px
        LBL_X = BAR_X - 22
        VAL_X = BAR_X + BAR_W + 8
        BH = 13
        GAP = 24
        Y0 = PAD + 8

        for i, (val, lbl, col) in enumerate([
            (r, 'R', self.BAR_R),
            (g, 'G', self.BAR_G),
            (b, 'B', self.BAR_B),
        ]):
            y1 = Y0 + i * GAP
            y2 = y1 + BH
            fw = max(0, int(BAR_W * val / 255))

            # Track
            self.info_cv.create_rectangle(
                BAR_X, y1, BAR_X + BAR_W, y2,
                fill=self.TRACK, outline=''
            )
            # Fill
            if fw > 0:
                self.info_cv.create_rectangle(
                    BAR_X, y1, BAR_X + fw, y2,
                    fill=col, outline=''
                )
            # Label
            self.info_cv.create_text(
                LBL_X, y1 + BH // 2,
                text=lbl, anchor=tk.CENTER,
                fill=self.TXT_SEC, font=self._fn_lbl
            )
            # Value
            self.info_cv.create_text(
                VAL_X, y1 + BH // 2,
                text=str(val), anchor=tk.W,
                fill=self.TXT_PRI, font=self._fn_lbl
            )

        # ── Percentage row ────────────────────────────────────────────────────
        tot = max(r + g + b, 1)
        pct = (f"R {r/tot*100:.1f}%      "
               f"G {g/tot*100:.1f}%      "
               f"B {b/tot*100:.1f}%")
        self.info_cv.create_text(
            BAR_X, Y0 + 3 * GAP + 8,
            text=pct, anchor=tk.W,
            fill=self.TXT_SEC, font=('Consolas', 9)
        )


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    # Show file picker before main window appears
    _tmp = tk.Tk()
    _tmp.withdraw()
    first = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff")]
    )
    _tmp.destroy()

    if not first:
        raise SystemExit("No file selected.")

    ColorInspector(first)
