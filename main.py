import os
import time
import winsound
import threading
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageSequence, ImageTk

# Configuração visual do modo claro
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

# Caminhos dinâmicos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "assets", "images")
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")

MAX_TOTAL_SECONDS = 300  # 20 minutos no total = Tela 4 (Explosão)


class SoundManager:
    """Gerenciador de áudio nativo utilizando winsound para arquivos .wav."""

    @staticmethod
    def play_button():
        """Toca o som de clique de botão."""
        path = os.path.join(SOUNDS_DIR, "buttonSound.wav")
        if os.path.exists(path):
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)

    @staticmethod
    def play_egg_ready():
        """Toca o som de alerta quando o timer atinge 00:00."""
        path = os.path.join(SOUNDS_DIR, "eggReady.wav")
        if os.path.exists(path):
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)

    @staticmethod
    def start_continuous_alarm():
        """Inicia o alarme contínuo em loop."""
        path = os.path.join(SOUNDS_DIR, "continuousAlarm.wav")
        if os.path.exists(path):
            winsound.PlaySound(
                path,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP
            )

    @staticmethod
    def stop_sound():
        """Interrompe qualquer áudio em execução."""
        winsound.PlaySound(None, winsound.SND_PURGE)

    @staticmethod
    def play_exploded():
        """Para os alarmes e toca o som de explosão aos 20 min."""
        SoundManager.stop_sound()
        path = os.path.join(SOUNDS_DIR, "explodedEgg.wav")
        if os.path.exists(path):
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)


class EggTimerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Eggspectation 🥚✨")
        self.geometry("580x780")
        self.resizable(False, False)

        # Configuração completa dos 6 ovos
        self.egg_options = [
            {
                "id": "molinha",
                "title": "4 min",
                "desc": "Gema Molinha",
                "seconds": 240,
                "basket": "cesta_white.png",
                "egg_img": "egg_4min.png",
                "btn_no_press": "Gema_molinha_copiar_no_press.png",
                "btn_press": "gema_molinha_Press.png",
                "cook_gif": "egg_cooking.gif"
            },
            {
                "id": "cremosa",
                "title": "6 min",
                "desc": "Gema Cremosa",
                "seconds": 360,
                "basket": "cesta_brown.png",
                "egg_img": "egg_6min.png",
                "btn_no_press": "Gema_Cremosa_copiar_no_press.png",
                "btn_press": "Gema_Cremosa_Press.png",
                "cook_gif": "egg_cooking.gif"
            },
            {
                "id": "macia",
                "title": "8 min",
                "desc": "Gema Macia",
                "seconds": 480,
                "basket": "cesta_white.png",
                "egg_img": "egg_8min.png",
                "btn_no_press": "Gema_Macia_copiar_press.png",
                "btn_press": "gema_macia_Press.png",
                "cook_gif": "egg_cooking.gif"
            },
            {
                "id": "firme",
                "title": "10 min",
                "desc": "Gema Firme",
                "seconds": 600,
                "basket": "cesta_brown.png",
                "egg_img": "egg_10min.png",
                "btn_no_press": "Gema_Firme_copiar_no_press.png",
                "btn_press": "gema_firme_Press.png",
                "cook_gif": "egg_cooking.gif"
            },
            {
                "id": "dura",
                "title": "12 min",
                "desc": "Gema Dura",
                "seconds": 720,
                "basket": "cesta_white.png",
                "egg_img": "egg_12min.png",
                "btn_no_press": "Gema_Dura_copiar_no_press.png",
                "btn_press": "gema_dura_Press.png",
                "cook_gif": "egg_cooking.gif"
            },
            {
                "id": "passada",
                "title": "15 min",
                "desc": "Gema Passada",
                "seconds": 900,
                "basket": "cesta_brown.png",
                "egg_img": "egg_15min.png",
                "btn_no_press": "Gema_Passada_copiar_no_press.png",
                "btn_press": "Gema_Passada_Press.png",
                "cook_gif": "egg_cooking.gif"
            },
        ]

        # Estado do Temporizador
        self.current_egg_data = None
        self.total_seconds = 0
        self.time_left = 0
        self.overcook_seconds = 0
        self.is_running = False
        self.is_overcooking = False
        self.timer_thread = None
        self.stop_event = threading.Event()
        self.active_pressed_egg = None

        # Controle de Animações
        self.cook_frames = []
        self.cook_frame_idx = 0
        self.cook_anim_id = None
        self.exploded_anim_id = None

        # Imagens Compartilhadas do Botão Voltar
        self.voltar_np_img = self.load_photo_image("voltar_botao_no_press.png", target_width=180)
        self.voltar_p_img = self.load_photo_image("voltar_botao_press.png", target_width=180)
        if not self.voltar_np_img:
            self.voltar_np_img = self.voltar_p_img

        # Telas (Frames)
        self.welcome_screen = ctk.CTkFrame(self, fg_color="transparent")
        self.selection_screen = ctk.CTkFrame(self, fg_color="transparent")
        self.timer_screen = ctk.CTkFrame(self, fg_color="transparent")
        self.exploded_screen = ctk.CTkFrame(self, fg_color="transparent")
        self.ready_screen = ctk.CTkFrame(self, fg_color="transparent")

        self.setup_welcome_screen()
        self.setup_selection_screen()
        self.setup_timer_screen()
        self.setup_exploded_screen()
        self.setup_ready_screen()

        self.show_welcome_screen()

    def load_photo_image(self, filename, target_width=None, target_height=None):
        """Carrega e redimensiona imagem mantendo a qualidade."""
        path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(path):
            try:
                pil_img = Image.open(path).convert("RGBA")
                w, h = pil_img.size
                if target_width and not target_height:
                    target_height = max(1, int(h * (target_width / w)))
                    pil_img = pil_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                elif target_width and target_height:
                    pil_img = pil_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(pil_img)
            except Exception:
                return None
        return None

    def load_gif_frames(self, filename, size):
        """Carrega frames de animação GIF."""
        path = os.path.join(IMAGES_DIR, filename)
        frames = []
        if os.path.exists(path):
            try:
                pil_img = Image.open(path)
                for frame in ImageSequence.Iterator(pil_img):
                    f_copy = frame.copy().convert("RGBA")
                    f_copy = f_copy.resize(size, Image.Resampling.NEAREST)
                    frames.append(ImageTk.PhotoImage(f_copy))
            except Exception:
                pass
        return frames

    # --- TELA 1: BOAS-VINDAS ---
    def setup_welcome_screen(self):
        self.canvas_1 = tk.Canvas(self.welcome_screen, width=580, height=780, highlightthickness=0, bd=0)
        self.canvas_1.pack(fill="both", expand=True)

        self.bg_photo_1 = self.load_photo_image("background.png", target_width=580)
        if self.bg_photo_1:
            self.canvas_1.create_image(0, 0, image=self.bg_photo_1, anchor="nw")
            self.canvas_1.bg_ref = self.bg_photo_1

        self.logo_photo = self.load_photo_image("egg_spectation_logo.png", target_width=380)
        if self.logo_photo:
            self.canvas_1.create_image(290, 160, image=self.logo_photo)
            self.canvas_1.logo_ref = self.logo_photo

        self.welcome_egg_photo = self.load_photo_image("welcome_egg.png", target_width=400)
        if self.welcome_egg_photo:
            self.canvas_1.create_image(290, 400, image=self.welcome_egg_photo)
            self.canvas_1.welcome_egg_ref = self.welcome_egg_photo

        self.start_no_press_photo = self.load_photo_image("start_button_no_press.png", target_width=300)
        self.start_press_photo = self.load_photo_image("start_button_press.png", target_width=300)

        if not self.start_no_press_photo:
            self.start_no_press_photo = self.load_photo_image("start_button_no_press.png", target_width=300)
            self.start_press_photo = self.load_photo_image("start_button_press.png", target_width=300)

        if self.start_no_press_photo:
            self.start_btn_item = self.canvas_1.create_image(290, 630, image=self.start_no_press_photo, tags="btn_iniciar")
            self.canvas_1.start_no_press_ref = self.start_no_press_photo
            self.canvas_1.start_press_ref = self.start_press_photo
            self.canvas_1.tag_bind("btn_iniciar", "<Button-1>", self.on_start_press)
            self.canvas_1.tag_bind("btn_iniciar", "<ButtonRelease-1>", self.on_start_release)

    def on_start_press(self, event=None):
        SoundManager.play_button()
        if hasattr(self, "start_press_photo") and self.start_press_photo:
            self.canvas_1.itemconfig(self.start_btn_item, image=self.start_press_photo)

    def on_start_release(self, event=None):
        if hasattr(self, "start_no_press_photo") and self.start_no_press_photo:
            self.canvas_1.itemconfig(self.start_btn_item, image=self.start_no_press_photo)
        self.show_selection_screen()

    def show_welcome_screen(self):
        self.stop_timer_and_sound()
        self.hide_all_screens()
        self.welcome_screen.pack(fill="both", expand=True)

    def show_welcome_screen_with_sound(self):
        SoundManager.play_button()
        self.show_welcome_screen()

    # --- TELA 2: SELEÇÃO ---
    def setup_selection_screen(self):
        self.canvas_2 = tk.Canvas(self.selection_screen, width=580, height=780, highlightthickness=0, bd=0)
        self.canvas_2.pack(fill="both", expand=True)

        self.bg_photo_2 = self.load_photo_image("background.png", target_width=580)
        if self.bg_photo_2:
            self.canvas_2.create_image(0, 0, image=self.bg_photo_2, anchor="nw")
            self.canvas_2.bg_ref = self.bg_photo_2

        self.choose_title_photo = self.load_photo_image("choose_time.png", target_width=380)
        if self.choose_title_photo:
            self.canvas_2.create_image(290, 75, image=self.choose_title_photo)
            self.canvas_2.choose_title_ref = self.choose_title_photo

        col_x = [110, 290, 470]
        basket_y = [260, 520]
        btn_y = [375, 635]

        self.selection_items = {}
        self.selection_img_refs = []

        for index, item in enumerate(self.egg_options):
            c = index % 3
            r = index // 3
            cx = col_x[c]
            by = basket_y[r]
            ly = btn_y[r]

            basket_photo = self.load_photo_image(item["basket"], target_width=500)
            if basket_photo:
                self.canvas_2.create_image(cx, by, image=basket_photo)
                self.selection_img_refs.append(basket_photo)

            egg_photo = self.load_photo_image(item["egg_img"], target_width=130)
            if egg_photo:
                self.canvas_2.create_image(cx, by, image=egg_photo)
                self.selection_img_refs.append(egg_photo)

            btn_no_press_photo = self.load_photo_image(item["btn_no_press"], target_width=300)
            btn_press_photo = self.load_photo_image(item["btn_press"], target_width=300)

            if btn_no_press_photo:
                self.selection_img_refs.extend([btn_no_press_photo, btn_press_photo])
                btn_item = self.canvas_2.create_image(cx, ly, image=btn_no_press_photo)
            else:
                btn_item = self.canvas_2.create_text(
                    cx, ly,
                    text=f"{item['title']}\n{item['desc']}",
                    font=("Segoe UI", 12, "bold"),
                    fill="#4A3B32",
                    justify="center"
                )

            self.selection_items[item["id"]] = {
                "btn_item": btn_item,
                "no_press": btn_no_press_photo,
                "press": btn_press_photo,
                "data": item
            }

        # Botão Voltar (Canto Inferior Esquerdo)
        if self.voltar_np_img:
            self.voltar_btn_t2 = self.canvas_2.create_image(80, 745, image=self.voltar_np_img, tags="btn_voltar_t2")
            self.canvas_2.tag_bind("btn_voltar_t2", "<Button-1>", self.on_voltar_t2_press)
            self.canvas_2.tag_bind("btn_voltar_t2", "<ButtonRelease-1>", self.on_voltar_t2_release)

        self.canvas_2.bind("<Button-1>", self.on_canvas_2_press)
        self.canvas_2.bind("<ButtonRelease-1>", self.on_canvas_2_release)

    def on_voltar_t2_press(self, event=None):
        SoundManager.play_button()
        if self.voltar_p_img:
            self.canvas_2.itemconfig(self.voltar_btn_t2, image=self.voltar_p_img)

    def on_voltar_t2_release(self, event=None):
        if self.voltar_np_img:
            self.canvas_2.itemconfig(self.voltar_btn_t2, image=self.voltar_np_img)
        self.show_welcome_screen()

    def _find_egg_at_coords(self, x, y):
        col_x = [110, 290, 470]
        basket_y = [260, 520]
        btn_y = [375, 635]

        for index, item in enumerate(self.egg_options):
            c = index % 3
            r = index // 3
            cx = col_x[c]
            by = basket_y[r]
            ly = btn_y[r]

            if (cx - 85 <= x <= cx + 85) and (by - 90 <= y <= ly + 50):
                return item["id"]
        return None

    def on_canvas_2_press(self, event):
        x, y = event.x, event.y
        if 20 <= x <= 160 and 700 <= y <= 780:
            return  # Gerenciado pela tag direta btn_voltar_t2

        egg_id = self._find_egg_at_coords(x, y)
        if egg_id:
            self.active_pressed_egg = egg_id
            self.on_egg_select_press(egg_id)

    def on_canvas_2_release(self, event):
        if self.active_pressed_egg:
            egg_id = self.active_pressed_egg
            self.active_pressed_egg = None
            self.on_egg_select_release(egg_id)

    def on_egg_select_press(self, egg_id):
        SoundManager.play_button()
        info = self.selection_items.get(egg_id)
        if info and info["press"] and info["btn_item"]:
            self.canvas_2.itemconfig(info["btn_item"], image=info["press"])

    def on_egg_select_release(self, egg_id):
        info = self.selection_items.get(egg_id)
        if info:
            if info["no_press"] and info["btn_item"]:
                self.canvas_2.itemconfig(info["btn_item"], image=info["no_press"])
            self.open_timer_page(info["data"])

    def show_selection_screen(self):
        self.stop_timer_and_sound()
        self.hide_all_screens()
        self.selection_screen.pack(fill="both", expand=True)

    def show_selection_screen_with_sound(self):
        SoundManager.play_button()
        self.show_selection_screen()

    # --- TELA 3: TIMER (COM CABEÇALHO EM IMAGENS) ---
    def setup_timer_screen(self):
        self.canvas_3 = tk.Canvas(self.timer_screen, width=580, height=780, highlightthickness=0, bd=0)
        self.canvas_3.pack(fill="both", expand=True)

        # 1. Background
        self.bg_photo_3 = self.load_photo_image("background.png", target_width=580)
        if self.bg_photo_3:
            self.canvas_3.create_image(0, 0, image=self.bg_photo_3, anchor="nw")
            self.canvas_3.bg_ref = self.bg_photo_3

        # 2. Cabeçalho: Imagem "cooking.png" em cima
        self.cooking_title_photo = self.load_photo_image("cooking.png", target_width=330)
        if not self.cooking_title_photo:
            self.cooking_title_photo = self.load_photo_image("coo.png", target_width=330)

        if self.cooking_title_photo:
            self.canvas_3.create_image(290, 50, image=self.cooking_title_photo)
            self.canvas_3.cooking_title_ref = self.cooking_title_photo

        # 3. Cabeçalho: Imagem da Gema selecionada logo abaixo
        self.t3_gema_text_item = self.canvas_3.create_image(290, 110)

        # 4. GIF da Panela / Cozimento
        self.cooking_gif_item = self.canvas_3.create_image(290, 240)

        # 5. Display do Relógio (Timer)
        self.timer_display_item = self.canvas_3.create_text(
            290, 390,
            text="00:00",
            font=("Segoe UI", 68, "bold"),
            fill="#E07A5F"
        )

        # 6. Barra de Progresso
        self.progress_bar = ctk.CTkProgressBar(
            self.canvas_3,
            width=430,
            height=14,
            corner_radius=7,
            progress_color="#E07A5F",
            fg_color="#E6D3B8"
        )
        self.progress_bar.set(1.0)
        self.canvas_3.create_window(290, 455, window=self.progress_bar)

        # 7. Botões Iniciar e Pausar
        self.t3_iniciar_np = self.load_photo_image("iniciar_botao_no_press.png", target_width=170)
        self.t3_iniciar_p = self.load_photo_image("iniciar_botao_Press.png", target_width=170)

        self.t3_pausar_np = self.load_photo_image("pausar_botao_no_press.png", target_width=170)
        self.t3_pausar_p = self.load_photo_image("pausar_botao_Press.png", target_width=170)

        self.t3_desativar_np = self.load_photo_image("desativar_alarme_botao_no_press.png", target_width=320)
        self.t3_desativar_p = self.load_photo_image("desativar_alarme_botao_P.png", target_width=320)

        # Botão Iniciar
        if self.t3_iniciar_np:
            self.btn_iniciar_item = self.canvas_3.create_image(195, 535, image=self.t3_iniciar_np, tags="t3_iniciar")
            self.canvas_3.tag_bind("t3_iniciar", "<Button-1>", self.on_t3_iniciar_press)
            self.canvas_3.tag_bind("t3_iniciar", "<ButtonRelease-1>", self.on_t3_iniciar_release)

        # Botão Pausar
        if self.t3_pausar_np:
            self.btn_pausar_item = self.canvas_3.create_image(385, 535, image=self.t3_pausar_np, tags="t3_pausar")
            self.canvas_3.tag_bind("t3_pausar", "<Button-1>", self.on_t3_pausar_press)
            self.canvas_3.tag_bind("t3_pausar", "<ButtonRelease-1>", self.on_t3_pausar_release)

        # Botão Desativar Alarme (Oculto inicialmente)
        if self.t3_desativar_np:
            self.btn_desativar_item = self.canvas_3.create_image(290, 620, image=self.t3_desativar_np, state="hidden", tags="t3_desativar")
            self.canvas_3.tag_bind("t3_desativar", "<Button-1>", self.on_t3_desativar_press)
            self.canvas_3.tag_bind("t3_desativar", "<ButtonRelease-1>", self.on_t3_desativar_release)

        # Botão Voltar (Canto Inferior Esquerdo)
        if self.voltar_np_img:
            self.btn_voltar_t3 = self.canvas_3.create_image(80, 735, image=self.voltar_np_img, tags="t3_voltar")
            self.canvas_3.tag_bind("t3_voltar", "<Button-1>", self.on_t3_voltar_press)
            self.canvas_3.tag_bind("t3_voltar", "<ButtonRelease-1>", self.on_t3_voltar_release)

    def on_t3_voltar_press(self, event=None):
        SoundManager.play_button()
        if self.voltar_p_img:
            self.canvas_3.itemconfig(self.btn_voltar_t3, image=self.voltar_p_img)

    def on_t3_voltar_release(self, event=None):
        if self.voltar_np_img:
            self.canvas_3.itemconfig(self.btn_voltar_t3, image=self.voltar_np_img)
        self.show_selection_screen()

    def on_t3_iniciar_press(self, event=None):
        SoundManager.play_button()
        if hasattr(self, "t3_iniciar_p") and self.t3_iniciar_p:
            self.canvas_3.itemconfig(self.btn_iniciar_item, image=self.t3_iniciar_p)

    def on_t3_iniciar_release(self, event=None):
        if hasattr(self, "t3_iniciar_np") and self.t3_iniciar_np:
            self.canvas_3.itemconfig(self.btn_iniciar_item, image=self.t3_iniciar_np)
        self.start_timer()

    def on_t3_pausar_press(self, event=None):
        SoundManager.play_button()
        if hasattr(self, "t3_pausar_p") and self.t3_pausar_p:
            self.canvas_3.itemconfig(self.btn_pausar_item, image=self.t3_pausar_p)

    def on_t3_pausar_release(self, event=None):
        if hasattr(self, "t3_pausar_np") and self.t3_pausar_np:
            self.canvas_3.itemconfig(self.btn_pausar_item, image=self.t3_pausar_np)
        self.pause_timer()

    def on_t3_desativar_press(self, event=None):
        SoundManager.play_button()
        if hasattr(self, "t3_desativar_p") and self.t3_desativar_p:
            self.canvas_3.itemconfig(self.btn_desativar_item, image=self.t3_desativar_p)

    def on_t3_desativar_release(self, event=None):
        if hasattr(self, "t3_desativar_np") and self.t3_desativar_np:
            self.canvas_3.itemconfig(self.btn_desativar_item, image=self.t3_desativar_np)
        self.show_ready_screen()

    def open_timer_page(self, item_data):
        self.current_egg_data = item_data
        SoundManager.play_button()
        self.stop_timer_and_sound()

        self.total_seconds = item_data["seconds"]
        self.time_left = item_data["seconds"]
        self.overcook_seconds = 0
        self.is_overcooking = False

        # Define a imagem correspondente da gema selecionada no cabeçalho
        gema_img = self.load_photo_image(item_data["btn_no_press"], target_width=210)
        if gema_img:
            self.canvas_3.itemconfig(self.t3_gema_text_item, image=gema_img)
            self.canvas_3.current_gema_img_ref = gema_img

        self.canvas_3.itemconfig(self.timer_display_item, fill="#E07A5F")
        self.progress_bar.configure(progress_color="#E07A5F")
        self.progress_bar.set(1.0)

        # Oculta botão de desativar alarme
        if hasattr(self, "btn_desativar_item"):
            self.canvas_3.itemconfig(self.btn_desativar_item, state="hidden")

        self.update_display()

        # Carrega o GIF da panela e fixa o primeiro frame até iniciar
        self.cook_frames = self.load_gif_frames("egg_cooking.gif", (200, 200))
        self.cook_frame_idx = 0
        if self.cook_frames:
            self.canvas_3.itemconfig(self.cooking_gif_item, image=self.cook_frames[0])

        self.hide_all_screens()
        self.timer_screen.pack(fill="both", expand=True)

    def animate_cook_gif(self):
        if self.is_running and self.cook_frames:
            self.canvas_3.itemconfig(self.cooking_gif_item, image=self.cook_frames[self.cook_frame_idx])
            self.cook_frame_idx = (self.cook_frame_idx + 1) % len(self.cook_frames)
            self.cook_anim_id = self.after(30, self.animate_cook_gif)

    # --- TELA 5: OVO PRONTO (BON APPETIT) ---
    def setup_ready_screen(self):
        self.canvas_5 = tk.Canvas(self.ready_screen, width=580, height=780, highlightthickness=0, bd=0)
        self.canvas_5.pack(fill="both", expand=True)

        # 1. Background
        self.bg_photo_5 = self.load_photo_image("background.png", target_width=580)
        if self.bg_photo_5:
            self.canvas_5.create_image(0, 0, image=self.bg_photo_5, anchor="nw")
            self.canvas_5.bg_ref = self.bg_photo_5

        # 2. Imagem Bon Appetit
        self.bon_appetit_photo = self.load_photo_image("bon_appetit.png", target_width=360)
        if self.bon_appetit_photo:
            self.canvas_5.create_image(290, 160, image=self.bon_appetit_photo)
            self.canvas_5.bon_ref = self.bon_appetit_photo

        # 3. Imagem do Ovo Pronto
        self.ready_egg_item = self.canvas_5.create_image(290, 370)
        self.ready_desc_item = self.canvas_5.create_text(
            290, 490,
            text="",
            font=("Segoe UI", 22, "bold"),
            fill="#4A3B32",
            justify="center"
        )

        # 4. Botão Voltar no Canto Inferior Esquerdo
        if self.voltar_np_img:
            self.btn_voltar_t5 = self.canvas_5.create_image(80, 735, image=self.voltar_np_img, tags="btn_voltar_t5")
            self.canvas_5.tag_bind("btn_voltar_t5", "<Button-1>", self.on_voltar_t5_press)
            self.canvas_5.tag_bind("btn_voltar_t5", "<ButtonRelease-1>", self.on_voltar_t5_release)

    def on_voltar_t5_press(self, event=None):
        SoundManager.play_button()
        if self.voltar_p_img:
            self.canvas_5.itemconfig(self.btn_voltar_t5, image=self.voltar_p_img)

    def on_voltar_t5_release(self, event=None):
        if self.voltar_np_img:
            self.canvas_5.itemconfig(self.btn_voltar_t5, image=self.voltar_np_img)
        self.show_selection_screen()

    def show_ready_screen(self):
        self.stop_timer_and_sound()
        self.hide_all_screens()

        if self.current_egg_data:
            egg_photo = self.load_photo_image(self.current_egg_data["egg_img"], target_width=200)
            if egg_photo:
                self.canvas_5.itemconfig(self.ready_egg_item, image=egg_photo)
                self.canvas_5.ready_photo_ref = egg_photo
            self.canvas_5.itemconfig(self.ready_desc_item, text=f"Seu ovo com {self.current_egg_data['desc']}\nestá pronto!")

        self.ready_screen.pack(fill="both", expand=True)

    # --- TELA 4: EXPLOSÃO (20 MINUTOS) ---
    def setup_exploded_screen(self):
        self.canvas_4 = tk.Canvas(self.exploded_screen, width=580, height=780, highlightthickness=0, bd=0)
        self.canvas_4.pack(fill="both", expand=True)

        self.bg_photo_4 = self.load_photo_image("background.png", target_width=580)
        if self.bg_photo_4:
            self.canvas_4.create_image(0, 0, image=self.bg_photo_4, anchor="nw")
            self.canvas_4.bg_ref = self.bg_photo_4

        self.canvas_4.create_text(290, 100, text="OVO EXPLODIU! 💥", font=("Segoe UI", 28, "bold"), fill="#D9534F")
        self.canvas_4.create_text(
            290, 160,
            text="Passaram-se 20 minutos de cozimento!\nSeu ovo passou completamente do ponto.",
            font=("Segoe UI", 14),
            fill="#4A3B32",
            justify="center"
        )

        self.exploded_img_item = self.canvas_4.create_image(290, 360)
        exploded_img = self.load_photo_image("exploded_egg.png", target_width=260)
        if exploded_img:
            self.canvas_4.itemconfig(self.exploded_img_item, image=exploded_img)
            self.canvas_4.exp_ref = exploded_img

        # Botão Tentar Novamente
        self.exp_restart_np = self.load_photo_image("tentar_novamente_botao_no_press.png", target_width=280)
        self.exp_restart_p = self.load_photo_image("Tentar_Novamente_Press.png", target_width=280)

        if self.exp_restart_np:
            self.exp_restart_btn_item = self.canvas_4.create_image(290, 560, image=self.exp_restart_np, tags="btn_restart_4")
            self.canvas_4.tag_bind("btn_restart_4", "<Button-1>", lambda e: SoundManager.play_button())
            self.canvas_4.tag_bind("btn_restart_4", "<ButtonRelease-1>", lambda e: self.show_selection_screen())

    def show_exploded_screen(self):
        self.stop_timer_and_sound()
        self.hide_all_screens()
        SoundManager.play_exploded()
        self.exploded_screen.pack(fill="both", expand=True)

    def stop_animations(self):
        if self.cook_anim_id:
            self.after_cancel(self.cook_anim_id)
            self.cook_anim_id = None

    def hide_all_screens(self):
        self.stop_animations()
        self.welcome_screen.pack_forget()
        self.selection_screen.pack_forget()
        self.timer_screen.pack_forget()
        self.exploded_screen.pack_forget()
        self.ready_screen.pack_forget()

    # --- LÓGICA DO TEMPORIZADOR ---
    def update_display(self):
        if not self.is_overcooking:
            mins, secs = divmod(self.time_left, 60)
            self.canvas_3.itemconfig(self.timer_display_item, text=f"{mins:02d}:{secs:02d}", fill="#E07A5F")
        else:
            mins, secs = divmod(self.overcook_seconds, 60)
            self.canvas_3.itemconfig(self.timer_display_item, text=f"+{mins:02d}:{secs:02d}", fill="#D9534F")

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.stop_event.clear()  # Libera o temporizador para rodar
            self.animate_cook_gif()
            self.timer_thread = threading.Thread(
                target=self.run_timer, daemon=True
            )
            self.timer_thread.start()

    def pause_timer(self):
        self.is_running = False
        self.stop_event.set()  # Interrompe o sleep imediatamente no mesmo milissegundo
        self.stop_animations()

    def stop_timer_and_sound(self):
        self.is_running = False
        self.stop_event.set()  # Cancela qualquer contagem pendente na hora
        self.stop_animations()
        SoundManager.stop_sound()

    def run_timer(self):
        while self.is_running:
            # Espera 1 segundo, mas se 'stop_event.set()' for chamado (Pause),
            # o wait() é cancelado instantaneamente e retorna True
            if self.stop_event.wait(timeout=1.0):
                break

            # Se foi pausado durante a espera, não desconta o tempo
            if not self.is_running:
                break

            elapsed_total = (
                self.total_seconds - self.time_left
            ) + self.overcook_seconds

            # 1. 20 minutos no total -> Tela 4 (Explosão)
            if elapsed_total >= MAX_TOTAL_SECONDS:
                self.after(0, self.show_exploded_screen)
                break

            if self.time_left > 0:
                self.time_left -= 1
                progress = self.time_left / self.total_seconds
                self.progress_bar.set(progress)
            else:
                # 2. Bateu 00:00 -> Exibe botão Desativar Alarme e toca som
                if not self.is_overcooking:
                    self.is_overcooking = True
                    self.after(
                        0,
                        lambda: self.canvas_3.itemconfig(
                            self.btn_desativar_item, state="normal"
                        ),
                    )

                    SoundManager.play_egg_ready()
                    self.after(1200, SoundManager.start_continuous_alarm)

                self.overcook_seconds += 1
                self.progress_bar.set(0)

            self.after(0, self.update_display)


if __name__ == "__main__":
    app = EggTimerApp()
    app.mainloop()