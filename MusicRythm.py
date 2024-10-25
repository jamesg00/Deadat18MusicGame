
import pygame
import random
import json
import math
import os 

# Initialize Pygame
pygame.init()
bg = pygame.image.load("assets/backgroundd.png")
akey = pygame.transform.scale(pygame.image.load("assets/a keyy.png"), (60, 60))
akey2 = pygame.transform.scale(pygame.image.load("assets/akey2.png"), (60, 60))
skey = pygame.transform.scale(pygame.image.load("assets/s_light.png"), (60, 60))
skey2 = pygame.transform.scale(pygame.image.load("assets/s_dark.png"), (60, 60))
dkey = pygame.transform.scale(pygame.image.load("assets/d_light.png"), (60, 60))
dkey2 = pygame.transform.scale(pygame.image.load("assets/d_dark.png"), (60, 60))
fkey = pygame.transform.scale(pygame.image.load("assets/f_light.png"), (60, 60))
fkey2 = pygame.transform.scale(pygame.image.load("assets/f_dark.png"), (60, 60))

note_image = pygame.transform.scale(pygame.image.load("assets/tool.png"), (20, 20))

# Load level data
with open('json/level.json', 'r') as f: 
    level_data = json.load(f)

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
NOTE_SPEED = 73.6
LANE_WIDTH = SCREEN_WIDTH // 4
HIT_Y = 525  # Aligning hit area with key sprites
SCROLLING_TEXT_DURATION = 4000  # Duration to show scrolling text (in milliseconds)


# Get the note dimensions from the resized image
NOTE_WIDTH, NOTE_HEIGHT = note_image.get_size()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Key mapping
KEYS = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]
LANES = [59, 137, 215, 293]

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Rhythm Game')

# Clock to control the frame rate
clock = pygame.time.Clock()

notes = []


class TitleState:
    def __init__(self):
        self.frame = 0
        self.animation1_frames = [pygame.image.load(f"animation1/frame{i:04d}.png") for i in range(120)]
        self.animation2_frames = [pygame.image.load(f"animation2/frame{i:04d}.png") for i in range(120)]
        self.animation1_rect = self.animation1_frames[0].get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.animation2_rect = self.animation2_frames[0].get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # start animation
                    self.frame = 0

    def draw(self):
        screen.fill(BLACK)

        # draw animation
        if self.frame < len(self.animation1_frames):
            screen.blit(self.animation1_frames[self.frame], self.animation1_rect)
            screen.blit(self.animation2_frames[self.frame], self.animation2_rect)
            self.frame += 1

        # draw title text
        font = pygame.font.Font('assets/upheavtt.ttf', 64)
        title_text = font.render("Rhythm Game", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        wave_y = SCREEN_HEIGHT / 2 + 10 * math.sin(pygame.time.get_ticks() * 0.005)
        screen.blit(title_text, (title_rect.x, wave_y))

        font = pygame.font.Font('assets/upheavtt.ttf', 32)
        press_space_text = "Press Space to continue"
        for i, char in enumerate(press_space_text):
            char_surface = font.render(char, True, WHITE)
            char_rect = char_surface.get_rect(center=(SCREEN_WIDTH / 2 - len(press_space_text) * 10 / 2 + i * 20, SCREEN_HEIGHT * 0.8 + 5 * math.sin(pygame.time.get_ticks() * 0.005 + math.pi / 2)))
            if char_rect.collidepoint(pygame.mouse.get_pos()):
                color_angle = pygame.time.get_ticks() * 0.01 + i * 0.1
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                char_surface = font.render(char, True, (r, g, b))
                char_rect.y += 5 * math.sin(pygame.time.get_ticks() * 0.01 + i * 0.1)
            screen.blit(char_surface, char_rect)

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.size, self.size))

class Menu:
    def __init__(self, options, trails):
        self.options = options
        self.selected_option = 0
        self.sin_offset = 0
        self.hover_option = None
        self.mouse_trail = []
        self.trails = trails
        self.selected_trail = 0
        self.trail_dropdown_open = False
        self.trail_rects = []

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.selected_option  # Return the selected option
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.trail_dropdown_rect.collidepoint(mouse_pos):
                self.trail_dropdown_open = not self.trail_dropdown_open
            for i, trail_rect in enumerate(self.trail_rects):
                if trail_rect.collidepoint(mouse_pos):
                    self.selected_trail = i
                    self.trail_dropdown_open = False
        return None

    def draw(self, screen, font):
        screen.fill(BLACK)

        self.sin_offset += 0.2
        mouse_pos = pygame.mouse.get_pos()
        self.hover_option = None
        for idx, option in enumerate(self.options):
            option_rect = pygame.Rect(SCREEN_WIDTH // 2 - len(option) * 20 // 2, 200 + idx * 50, len(option) * 20, 30)
            if option_rect.collidepoint(mouse_pos):
                self.hover_option = idx

            if idx == self.hover_option:
                self.draw_option(screen, font, option, idx)
            else:
                # Draw non-hovered options with white letters
                text = font.render(option, True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + idx * 50))

        # Draw trail dropdown button
        self.trail_dropdown_rect = pygame.Rect(10, 10 + math.sin(self.sin_offset) * 5, 100, 20)
        pygame.draw.rect(screen, (255, 255, 255), self.trail_dropdown_rect)
        trail_text = font.render("Trail: " + self.trails[self.selected_trail], True, (0, 0, 0))
        screen.blit(trail_text, (self.trail_dropdown_rect.x + 10, self.trail_dropdown_rect.y + 5 + math.sin(self.sin_offset) * 2))

        if self.trail_dropdown_open:
            self.trail_rects = []
            for i, trail in enumerate(self.trails):
                trail_rect = pygame.Rect(self.trail_dropdown_rect.x, self.trail_dropdown_rect.y + (i + 1) * 20, self.trail_dropdown_rect.width, 20)
                self.trail_rects.append(trail_rect)
                pygame.draw.rect(screen, (255, 255, 255), trail_rect)
                trail_text = font.render(trail, True, (0, 0, 0))
                screen.blit(trail_text, (trail_rect.x + 10, trail_rect.y + 5))

        # Draw trail
        if self.selected_trail == 0:
            # No trail
            pass
        elif self.selected_trail == 1:
            # RGB Trail
            self.mouse_trail.append((mouse_pos, self.sin_offset))
            if len(self.mouse_trail) > 100:
                self.mouse_trail.pop(0)

            # Draw magical pixels
            for i, (pos, offset) in enumerate(self.mouse_trail):
                color_angle = offset + i * 0.1
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                opacity = int(255 * (1 - i / len(self.mouse_trail)))
                x = pos[0] + math.sin(offset + i * 0.1) * 5
                y = pos[1] + math.sin(offset + i * 0.1 + math.pi / 2) * 5
                pygame.draw.circle(screen, (r, g, b), (int(x), int(y)), 2)
        elif self.selected_trail == 2:
            # Fading Trail
            self.mouse_trail.append((mouse_pos, self.sin_offset))
            if len(self.mouse_trail) > 100:
                self.mouse_trail.pop(0)

            # Draw fading trail
            for i, (pos, offset) in enumerate(self.mouse_trail):
                opacity = int(255 * (1 - i / len(self.mouse_trail)))
                s = pygame.Surface((5, 5), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 255, opacity), (2, 2), 2)
                screen.blit(s, pos)

    def draw_option(self, screen, font, option, idx):
        # Draw hovered option with sine wave movement and RGB letters
        text = ''
        for i, char in enumerate(option):
            color_angle = self.sin_offset + i * 0.1
            r = int(math.sin(color_angle) * 128 + 128)
            g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
            b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
            char_surface = font.render(char, True, (r, g, b))
            screen.blit(char_surface, (SCREEN_WIDTH // 2 - len(option) * 20 // 2 + i * 20, 200 + idx * 50 + math.sin(self.sin_offset + idx) * 5))


# Define the menu options
options = ['Play Level', 'Settings', 'Quit']

# Define the trail options
trails = ['RGB Trail', 'Fading Trail']

menu = Menu(["Play Level", "Settings", "Quit"], trails)
title_font = pygame.font.Font('assets/upheavtt.ttf', 64)


title_text = title_font.render("Rhythm Game", True, WHITE)
title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))


# Define game states
STATE_TITLE = 0
STATE_GAME = 1
STATE_PAUSE = 2
STATE_MENU = 3
STATE_SETTINGS = 4
STATE_TRAIL_SELECTION = 5
STATE_SCROLLED_TEXT = 6  # Add a new state
STATE_FADE_OUT = 7
STATE_FADE_IN = 8
# Initialize game state
state = STATE_TITLE


explosion_start_time = None



def load_songs():
    songs = []
    for i in range(1, 7):
        song = pygame.mixer.Sound('assets/song' + str(i) + '.mp3')
        songs.append(song)
    return songs

def play_random_song(songs):
    random_song = random.choice(songs)
    random_song.play(-1)  # -1 to loop the song

# Load songs in the initialization part of your code
songs = load_songs()




# Function to calculate NOTE_SPEED based on BPM
def calculate_note_speed(bpm):
    beat_duration = 60 / bpm  # seconds per beat
    travel_distance = HIT_Y  # distance to travel to hit line
    beats_to_hit_line = travel_distance / 60  # Assumption: 60 beats per full screen height
    note_speed = travel_distance / (beats_to_hit_line * beat_duration)
    return note_speed

# Example BPM input by user
user_bpm = 135
NOTE_SPEED = calculate_note_speed(user_bpm)

def drawPerfect(x, y):
    font = pygame.font.Font(None, 36)
    perfect_text = font.render("Perfect!", True, (0, 0, 0))
    screen.blit(perfect_text, (x, y))
    pygame.display.update()



def create_checkerboard_pattern(width, height, square_size, color, progress):
    pattern = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, square_size):
        for x in range(0, width, square_size):
            constant_alpha = 200  # Adjust the opacity value as needed
            alpha = constant_alpha
            color_with_alpha = (*color, alpha)
            pygame.draw.rect(pattern, color_with_alpha, (x, y, square_size, square_size))
    return pattern

def load_level_data():
    global notes
    with open('json/level.json', 'r') as f:
        level_data = json.load(f)
    notes = [Note(note['lane'], note['time']) for note in level_data]



menu_font = pygame.font.Font('assets/upheavtt.ttf', 36)

# Note class
class Note:
    def __init__(self, lane, timestamp):
        self.x = LANES[lane] + 10  # Adjust the offset_x as needed
        self.y = 0
        self.lane = lane
        self.timestamp = timestamp
        self.trail_length = 25  # Length of the trail
        self.trail_frequency = 10  # Frequency of trail points
        self.hit = False  # Flag to check if the note has been hit
    def update(self, current_time):
        self.y = (current_time - self.timestamp) * NOTE_SPEED / 1000

    def draw(self):
        # Draw the trail as circles
        for i in range(0, self.trail_length, self.trail_frequency):
            trail_y = self.y - i
            if trail_y >= 0:
                alpha = max(0, 255 - (255 * i / self.trail_length))  # Calculate alpha for fading effect
                color_with_alpha = (255, 255, 255, alpha)  # White color with alpha
                trail_surface = pygame.Surface((NOTE_WIDTH, NOTE_HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, color_with_alpha, (NOTE_WIDTH // 2, NOTE_HEIGHT // 2), NOTE_WIDTH // 2)
                screen.blit(trail_surface, (self.x, trail_y))

        # Draw the note
        screen.blit(note_image, (self.x, self.y))

class Explosion:
    def __init__(self, x, y, frames):
        self.x = x
        self.y = y
        self.frames = frames
        self.start_time = None
        self.frame_index = 0

    def trigger(self):
        self.start_time = pygame.time.get_ticks()
        self.frame_index = 0

    def update(self):
        if self.start_time is not None:
            elapsed_time = pygame.time.get_ticks() - self.start_time
            frame_duration = 1000 // FPS  # 60 FPS, so frame duration is about 16.67 ms
            self.frame_index = elapsed_time // frame_duration

    def draw(self, screen):
        if self.start_time is not None and self.frame_index < len(self.frames):
            screen.blit(self.frames[self.frame_index], (self.x, self.y))
            return True  # Animation is still running
        else:
            self.start_time = None  # Stop animation when it finishes
            return False


explosions = []
explosion_frames = []



explosion_path = 'assets/next'
for i in range(1, 12):  # Assumes frames are named "frame1.png" to "frame11.png"
    frame = pygame.image.load(os.path.join(explosion_path, f'frame{i}.png'))
    explosion_frames.append(frame) 

explosions = [
    Explosion(LANES[0], HIT_Y, explosion_frames),
    Explosion(LANES[1], HIT_Y, explosion_frames),
    Explosion(LANES[2], HIT_Y, explosion_frames),
    Explosion(LANES[3], HIT_Y, explosion_frames)
]

# Load animation frames
animation_frames = []
animation_path = 'assets/wills_magic_particle_effects/black_hole/frames'
for i in range(17, 120):
    frame = pygame.image.load(os.path.join(animation_path, f'frame{i:04d}.png'))
    animation_frames.append(frame)

# Game variables
notes = [Note(note['lane'], note['time']) for note in level_data]
score = 0
animation_start_time = None
animation_frame_index = 0
animation_x = 0  # Initialize animation position
animation_y = 0  # Initialize animation positio








def display_black_scrolling_text(text, duration):
    font = pygame.font.Font('assets/upheavtt.ttf', 32)
    text_surface = font.render(text, True, BLACK)
    text_width = text_surface.get_width()
    text_height = text_surface.get_height()
    
    start_time = pygame.time.get_ticks()
    elapsed_time = pygame.time.get_ticks() - start_time
    x_position = SCREEN_WIDTH - (elapsed_time / duration) * (SCREEN_WIDTH + text_width)
    
    screen.fill(BLACK)
    screen.blit(bg, (0,0))
    screen.blit(text_surface, (x_position, SCREEN_HEIGHT // 2 - text_height // 2))
    pygame.display.flip()
    
    # Return whether the text is still displaying
    return elapsed_time < duration


# Function to display scrolling text


# Extract song name from file path
music_file_path = 'assets/Awesomenarnia 124 (1).mp3'
song_name = os.path.basename(music_file_path).replace('.mp3', '')


enterMusic = 'assets/selection_01.mp3'




# Main game loop
running = True
start_time = pygame.time.get_ticks()

# Key states
key_states = {
    pygame.K_a: False,
    pygame.K_s: False,
    pygame.K_d: False,
    pygame.K_f: False
}


# Load sound effects
note5_sound = pygame.mixer.Sound('assets/note5.mp3')
note6_sound = pygame.mixer.Sound('assets/note6.mp3')

# Initialize flags to track whether the sound has been played for each selection
selection_sounds_played = [False] * len(menu.options)

game_start_time = 0
song_playing = False
trail_enabled = True
back_button_frame = 1
back_button_animation = False
back_button_animation_time = 0
previous_mouse_pos = None

previous_trail_type = None
# Load animation frames
animation1_frames = [pygame.image.load(f"assets/wills_magic_particle_effects/green_spiral/frames/frame{i:04d}.png") for i in range(120)]
animation2_frames = [pygame.image.load(f"assets/wills_magic_particle_effects/green_spiral/frames/frame{i:04d}.png") for i in range(120)]
fade_back = False
animation_started = False
opacity = 0
game_started = False
trail_type = None
star_trail = []


# Initialize key states
key_states = {
    pygame.K_w: False,
    pygame.K_a: False,
    pygame.K_s: False,
    pygame.K_d: False,
}

key_rgb_values = {
    pygame.K_w: (255, 255, 255),
    pygame.K_a: (255, 255, 255),
    pygame.K_s: (255, 255, 255),
    pygame.K_d: (255, 255, 255),
}


while running:
    current_time = pygame.time.get_ticks() - start_time
    if state == STATE_TITLE:
        # Handle title screen events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:

                    pygame.mixer.init()
                    pygame.mixer.music.load(enterMusic)
                    pygame.mixer.music.play()
                    animation_started = True

        # Draw title screen
        screen.fill(BLACK)

        font_size = int(SCREEN_HEIGHT / 15)
        font = pygame.font.Font('assets/upheavtt.ttf', font_size)
        rhythm_game_text = "deadat18 rhythm"
        text_width = 0
        for char in rhythm_game_text:
            char_surface = font.render(char, True, WHITE)
            text_width += char_surface.get_width()
        x_offset = (SCREEN_WIDTH - text_width) / 2
        for i, char in enumerate(rhythm_game_text):
            char_surface = font.render(char, True, WHITE)
            char_rect = char_surface.get_rect(center=(x_offset + char_surface.get_width() / 2, SCREEN_HEIGHT / 2 + 10 * math.sin(pygame.time.get_ticks() * 0.005)))
            x_offset += char_surface.get_width()
            if char_rect.collidepoint(pygame.mouse.get_pos()):
                color_angle = pygame.time.get_ticks() * 0.01 + i * 0.1
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                char_surface = font.render(char, True, (r, g, b))
                char_rect.y += 5 * math.sin(pygame.time.get_ticks() * 0.01 + i * 0.1)
            screen.blit(char_surface, char_rect)

        font_size = int(SCREEN_HEIGHT / 30)
        font = pygame.font.Font('assets/upheavtt.ttf', font_size)
        press_space_text = "Press Space to continue"
        text_width = 0
        for char in press_space_text:
            char_surface = font.render(char, True, WHITE)
            text_width += char_surface.get_width()
        x_offset = (SCREEN_WIDTH - text_width) / 2
        for i, char in enumerate(press_space_text):
            char_surface = font.render(char, True, WHITE)
            char_rect = char_surface.get_rect(center=(x_offset + char_surface.get_width() / 2, SCREEN_HEIGHT * 0.8 + 5 * math.sin(pygame.time.get_ticks() * 0.005 + math.pi / 2)))
            x_offset += char_surface.get_width()
            if char_rect.collidepoint(pygame.mouse.get_pos()):
                color_angle = pygame.time.get_ticks() * 0.01 + i * 0.1
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                char_surface = font.render(char, True, (r, g, b))
                char_rect.y += 5 * math.sin(pygame.time.get_ticks() * 0.01 + i * 0.1)
            screen.blit(char_surface, char_rect)

        if animation_started:
            # Draw animation
            frame = (current_time // 16) % 120  # 16ms per frame, 120 frames total
            animation1_surface = animation1_frames[frame]
            animation2_surface = animation2_frames[frame]
            animation1_rect = animation1_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            animation2_rect = animation2_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(animation1_surface, animation1_rect)
            #screen.blit(animation2_surface, animation2_rect)

            # Wait for animation to finish
            if frame >= 119:  # 120 frames total
                animation_started = False
                state = STATE_MENU  # Show menu

                    
        pygame.display.flip()
        clock.tick(60)
    elif state == STATE_MENU:
            print("Drawing trail with type:", trail_type)
            
            if not song_playing:
                play_random_song(songs)
                song_playing = True

            opacity = 0  # Reset opacity for menu screen
            # Handle menu events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_k:
                        trail_enabled = False
                        if not trail_enabled:
                            star_trail = []  # Clear the trail when it's disabled
                    selected_option = menu.handle_input(event)
                    if selected_option is not None:
                        if selected_option == len(menu.options) - 1:
                            running = False
                        elif selected_option == 0:  # "Play Level" is the first option
                            # Change to STATE_SCROLLED_TEXT to display scrolling text
                            state = STATE_SCROLLED_TEXT
                            scroll_text_start_time = pygame.time.get_ticks()  # Store the start time
                            pygame.mixer.stop()
                            # Preload level data here but don't start the game yet
                            load_level_data()
                            notes = [Note(note['lane'], note['time']) for note in level_data] 
                        elif selected_option == 1:  # "Settings" is the second option
                            # Change to STATE_SETTINGS to display settings
                            state = STATE_SETTINGS
                                    
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    for idx, option in enumerate(menu.options):
                        option_rect = pygame.Rect(SCREEN_WIDTH // 2 - len(option) * 20 // 2, 200 + idx * 50, len(option) * 20, 30)
                        if option_rect.collidepoint(mouse_pos) and not selection_sounds_played[idx]:
                            note5_sound.play()
                            selection_sounds_played[idx] = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for idx, option in enumerate(menu.options):
                        option_rect = pygame.Rect(SCREEN_WIDTH // 2 - len(option) * 20 // 2, 200 + idx * 50, len(option) * 20, 30)
                        if option_rect.collidepoint(mouse_pos):
                            if idx == len(menu.options) - 1:
                                running = False
                            elif idx == 0:
                                state = STATE_SCROLLED_TEXT
                                scroll_text_start_time = pygame.time.get_ticks()  # Store the start time
                                pygame.mixer.stop()
                                # Load the selected level
                                load_level_data()
                                notes = [Note(note['lane'], note['time']) for note in level_data]
                                pygame.mixer.music.load('assets/Awesomenarnia 124 (1).mp3')
                                pygame.mixer.music.play()
                                start_time = pygame.time.get_ticks()  # Reset the start time
                                state = STATE_GAME
                            elif idx == 1:
                                state = STATE_SETTINGS
                    # Check if settings button is pressed
                    settings_button_rect = pygame.Rect(SCREEN_WIDTH - 150, 10, 150, 20)
                    if settings_button_rect.collidepoint(mouse_pos):
                        state = STATE_SETTINGS

            # Reset the flags when the mouse is not hovering over any selection
            if not any(option_rect.collidepoint(pygame.mouse.get_pos()) for option_rect in [pygame.Rect(SCREEN_WIDTH // 2 - len(option) * 20 // 2, 200 + idx * 50, len(option) * 20, 30) for idx, option in enumerate(menu.options)]):
                selection_sounds_played = [False] * len(menu.options)

            # Draw menu
            screen.fill(BLACK)
            menu.draw(screen, menu_font)


            if trail_enabled:
                mouse_pos = pygame.mouse.get_pos()

                if previous_mouse_pos is not None and mouse_pos != previous_mouse_pos:
                    # Clear the screen to remove previous trails
                    screen.fill(BLACK)  
                    menu.draw(screen, menu_font)  # Redraw the menu

                    # Spawn new star
                    star_trail.append((mouse_pos[0], mouse_pos[1], 0))  # Start with opacity 0

                # Move and fade stars
                for i, (x, y, opacity) in enumerate(star_trail):
                    y -= 2  # Move star up
                    opacity += 10  # Fade in star
                    if opacity > 255:
                        opacity = 255
                    star_trail[i] = (x, y, opacity)

                    # Draw star
                    s = pygame.Surface((5, 5), pygame.SRCALPHA)
                    pygame.draw.circle(s, (255, 255, 255, opacity), (2, 2), 2)
                    screen.blit(s, (x, y))

                # Remove stars that are off the screen
                star_trail = [(x, y, opacity) for x, y, opacity in star_trail if y > 0]

                # Reset previous_mouse_pos to handle new trail drawing
                previous_mouse_pos = mouse_pos
            else:
                # Calculate sine wave values
                sine_wave_value = math.sin(pygame.time.get_ticks() / 1000) * 100

                # Update star trail
                star_trail.append((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + sine_wave_value, 255))

                # Draw trail
                for i, (x, y, opacity) in enumerate(star_trail):
                    s = pygame.Surface((5, 5), pygame.SRCALPHA)
                    pygame.draw.circle(s, (255, 0, 0, opacity), (2, 2), 2)  # Red color
                    screen.blit(s, (x, y))

                # Remove stars that are off the screen
                star_trail = [(x, y, opacity) for x, y, opacity in star_trail if y > 0]

                # Draw menu and buttons
                screen.fill(BLACK)
                menu.draw(screen, menu_font)  # Redraw the menu

            pygame.display.flip()
            clock.tick(60)
   

    elif state == STATE_SETTINGS:
        # Draw settings window
        screen.fill(BLACK)
        settings_window_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 200, 300, 400)
        pygame.draw.rect(screen, WHITE, settings_window_rect, 1)

        # Music volume settings
        music_volume_meter_rect = pygame.Rect(settings_window_rect.x + 10, settings_window_rect.y + 10, 280, 25)
        pygame.draw.rect(screen, WHITE, music_volume_meter_rect, 1)
        music_volume_percentage = pygame.mixer.music.get_volume() * 100
        for i in range(int(music_volume_percentage * 2.8)):
            hue = (music_volume_percentage / 100) * 0.83  
            h_i = int(hue * 6)
            f = hue * 6 - h_i
            p = 1 * (1 - 1)
            q = 1 * (1 - f * 1)
            t = 1 * (1 - (1 - f) * 1)

            if h_i == 0:
                r, g, b = 1, t, p
            elif h_i == 1:
                r, g, b = q, 1, p
            elif h_i == 2:
                r, g, b = p, 1, t
            elif h_i == 3:
                r, g, b = p, q, 1
            elif h_i == 4:
                r, g, b = t, p, 1
            elif h_i == 5:
                r, g, b = 1, p, q

            r, g, b = int(r * 255), int(g * 255), int(b * 255)  
            pygame.draw.rect(screen, (r, g, b), (music_volume_meter_rect.x + i, music_volume_meter_rect.y, 1, 25))

        music_volume_text = font.render("Music Volume: " + str(int(pygame.mixer.music.get_volume() * 100)) + "%", True, WHITE)
        music_volume_text_rect = music_volume_text.get_rect()
        music_volume_text_rect.x = settings_window_rect.x + 10
        music_volume_text_rect.y = settings_window_rect.y + 40
        screen.blit(music_volume_text, music_volume_text_rect)

        # SFX volume settings
        sfx_volume_meter_rect = pygame.Rect(settings_window_rect.x + 10, settings_window_rect.y + 80, 280, 25)
        pygame.draw.rect(screen, WHITE, sfx_volume_meter_rect, 1)
        sfx_volume_percentage = note5_sound.get_volume() * 100
        for i in range(int(sfx_volume_percentage * 2.8)):
            hue = (sfx_volume_percentage / 100) * 0.83  
            h_i = int(hue * 6)
            f = hue * 6 - h_i
            p = 1 * (1 - 1)
            q = 1 * (1 - f * 1)
            t = 1 * (1 - (1 - f) * 1)

            if h_i == 0:
                r, g, b = 1, t, p
            elif h_i == 1:
                r, g, b = q, 1, p
            elif h_i == 2:
                r, g, b = p, 1, t
            elif h_i == 3:
                r, g, b = p, q, 1
            elif h_i == 4:
                r, g, b = t, p, 1
            elif h_i == 5:
                r, g, b = 1, p, q

            r, g, b = int(r * 255), int(g * 255), int(b * 255)  
            pygame.draw.rect(screen, (r, g, b), (sfx_volume_meter_rect.x + i, sfx_volume_meter_rect.y, 1, 25))

        sfx_volume_text = font.render("SFX Volume: " + str(int(note5_sound.get_volume() * 100)) + "%", True, WHITE)
        sfx_volume_text_rect = sfx_volume_text.get_rect()
        sfx_volume_text_rect.x = settings_window_rect.x + 10
        sfx_volume_text_rect.y = settings_window_rect.y + 110
        screen.blit(sfx_volume_text, sfx_volume_text_rect)

        # Back button
        back_button_image = pygame.image.load('assets/Back' + str(back_button_frame) + '.png')
        back_button_image = pygame.transform.scale(back_button_image, (25, 25))
        back_button_rect = pygame.Rect(settings_window_rect.x + 10, settings_window_rect.y + 140, 25, 25)
        screen.blit(back_button_image, back_button_rect)

        # Keybind settings
        keybind_font = pygame.font.Font('assets/upheavtt.ttf', 24)
        keybind_text = 'Keybinds:'
        keybind_surface = keybind_font.render(keybind_text, True, WHITE)
        screen.blit(keybind_surface, (settings_window_rect.x + 10, settings_window_rect.y + 170))

        # Keybind options
        keybind_options = [
            {'key': 'W', 'binding': pygame.K_w, 'text': 'Move Up'},
            {'key': 'A', 'binding': pygame.K_a, 'text': 'Move Left'},
            {'key': 'S', 'binding': pygame.K_s, 'text': 'Move Down'},
            {'key': 'D', 'binding': pygame.K_d, 'text': 'Move Right'},
        ]

        for i, option in enumerate(keybind_options):
            option_text = f'{option["key"]}: {option["text"]}'
            option_surface = keybind_font.render(option_text, True, WHITE)
            screen.blit(option_surface, (settings_window_rect.x + 10, settings_window_rect.y + 200 + i * 30))

        # Change keybind button
        change_keybind_button = pygame.Rect(settings_window_rect.x + 10, settings_window_rect.y + 320, 150, 30)
        change_keybind_text = 'Change Keybind'
        change_keybind_surface = keybind_font.render(change_keybind_text, True, WHITE)
        pygame.draw.rect(screen, WHITE, change_keybind_button, 1)
        screen.blit(change_keybind_surface, (change_keybind_button.x + 10, change_keybind_button.y + 5))

        # Save keybind button
        save_keybind_button = pygame.Rect(settings_window_rect.x + 170, settings_window_rect.y + 320, 100, 30)
        save_keybind_text = 'Save'
        save_keybind_surface = keybind_font.render(save_keybind_text, True, WHITE)
        pygame.draw.rect(screen, WHITE, save_keybind_button, 1)
        screen.blit(save_keybind_surface, (save_keybind_button.x + 10, save_keybind_button.y + 5))


        # Handle user input to change volume
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if music_volume_meter_rect.collidepoint(mouse_pos):
                    new_volume = (mouse_pos[0] - music_volume_meter_rect.x) / 280
                    pygame.mixer.music.set_volume(new_volume)
                    for song in songs:
                        song.set_volume(new_volume)
                elif sfx_volume_meter_rect.collidepoint(mouse_pos):
                    new_volume = (mouse_pos[0] - sfx_volume_meter_rect.x) / 280
                    note5_sound.set_volume(new_volume)
                    note6_sound.set_volume(new_volume)
                elif back_button_rect.collidepoint(mouse_pos):
                    back_button_animation = True
                    back_button_animation_time = pygame.time.get_ticks()
                    note6_sound.play()
                elif change_keybind_button.collidepoint(mouse_pos):
                    # Get the selected keybind option
                    selected_option = None
                    for i, option in enumerate(keybind_options):
                        option_rect = pygame.Rect(settings_window_rect.x + 10, settings_window_rect.y + 200 + i * 30, 200, 30)
                        if option_rect.collidepoint(mouse_pos):
                            selected_option = option
                            break

                    # Change keybind
                    if selected_option:
                        waiting_for_key = True
                        while waiting_for_key:
                            for event in pygame.event.get():
                                if event.type == pygame.KEYDOWN:
                                    new_binding = event.key
                                    selected_option['binding'] = new_binding
                                    waiting_for_key = False

                elif save_keybind_button.collidepoint(mouse_pos):
                    # Save keybinds to JSON file
                    with open('keybinds.json', 'w') as f:
                        json.dump({option['key']: option['binding'] for option in keybind_options}, f)
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                if music_volume_meter_rect.collidepoint(mouse_pos) and event.buttons[0]:
                    new_volume = (mouse_pos[0] - music_volume_meter_rect.x) / 280
                    pygame.mixer.music.set_volume(new_volume)
                    for song in songs:
                        song.set_volume(new_volume)
            elif sfx_volume_meter_rect.collidepoint(mouse_pos) and event.buttons[0]:
                new_volume = (mouse_pos[0] - sfx_volume_meter_rect.x) / 280
                note5_sound.set_volume(new_volume)
                note6_sound.set_volume(new_volume)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = STATE_MENU


        # Update back button animation
        if back_button_animation:
            current_time = pygame.time.get_ticks()
            if current_time - back_button_animation_time > 100:
                back_button_frame += 1
                back_button_animation_time = current_time
            if back_button_frame > 5:
                state = STATE_MENU
                back_button_frame = 1
                back_button_animation = False


        pygame.display.flip()
        clock.tick(60)

    elif state == STATE_GAME:
                # Initialize key states


        game_started = True
        game_time = current_time - game_start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Clear the screen
            #screen.fill((0, 0, 0))
            if event.type == pygame.KEYDOWN:
                if event.key in key_states:
                    key_states[event.key] = True
                    color_angle = current_time * 0.01
                    r = int(math.sin(color_angle) * 128 + 128)
                    g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                    b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                    key_rgb_values[event.key] = (r, g, b)
            if event.type == pygame.KEYUP:
                if event.key in key_states:
                    key_states[event.key] = False
                    # Reset the RGB value for the key
                    key_rgb_values[event.key] = (255, 255, 255)
                    '''
                    if event.key == pygame.K_a:  # Start animation on "a" key hit
                        animation_start_time = pygame.time.get_ticks()
                        animation_frame_index = 0
                        animation_x = random.randint(0, SCREEN_WIDTH - animation_frames[0].get_width())
                        animation_y = random.randint(0, SCREEN_HEIGHT - animation_frames[0].get_height())
                    '''
          

            
        
        # Update notes
        for note in notes:
            note.update(current_time)
            

        # Check for hits
        keys = pygame.key.get_pressed()
        for note in notes[:]:
            if HIT_Y - NOTE_HEIGHT <= note.y <= HIT_Y + NOTE_HEIGHT:

                if keys[KEYS[note.lane]]:
                    
                    #drawPerfect(note.x, note.y)



                    notes.remove(note)
                    score += 1
                        # Trigger explosion animation
        
                    explosion_start_time = pygame.time.get_ticks()
                    explosion_frame_index = 0
                    explosion_x = LANES[note.lane] - 7
                    explosion_y = HIT_Y

                    

                    
                        # Trigger animation on "a" key hit
                    '''
                    if KEYS[note.lane] == pygame.K_a:
                        animation_start_time = pygame.time.get_ticks()
                        animation_frame_index = 0
                        animation_x = random.randint(0, SCREEN_WIDTH - animation_frames[0].get_width())
                        animation_y = random.randint(0, SCREEN_HEIGHT - animation_frames[0].get_height())
                    '''

        # Remove notes that are off the screen
        notes = [note for note in notes if note.y <= SCREEN_HEIGHT]


        

        # Draw everything
        screen.fill(BLACK)
        screen.blit(bg, (0,0))
        for note in notes:
            note.draw()

        # Draw keys based on their state
        font = pygame.font.Font('assets/upheavtt.ttf', 80)
        keys = ['W', 'A', 'S', 'D']
        key_x_positions = [59, 137, 215, 295]  # offset +10 on x-axis
        key_y_position = HIT_Y - 18
        wave_amplitude = 10
        wave_frequency = 0.005

        key_press_timers = {
            'W': 0,
            'A': 0,
            'S': 0,
            'D': 0,
        }

        key_rgb_values = {
            'W': (255, 255, 255),
            'A': (255, 255, 255),
            'S': (255, 255, 255),
            'D': (255, 255, 255),
        }

        for i, key in enumerate(keys):
            color = key_rgb_values[key]
            if key == 'W' and key_states[pygame.K_w]:
                key_press_timers[key] = pygame.time.get_ticks()
                color_angle = current_time * 0.01
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                key_rgb_values[key] = (r, g, b)
            elif key == 'A' and key_states[pygame.K_a]:
                key_press_timers[key] = pygame.time.get_ticks()
                color_angle = current_time * 0.01
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                key_rgb_values[key] = (r, g, b)
            elif key == 'S' and key_states[pygame.K_s]:
                key_press_timers[key] = pygame.time.get_ticks()
                color_angle = current_time * 0.01
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                key_rgb_values[key] = (r, g, b)
            elif key == 'D' and key_states[pygame.K_d]:
                key_press_timers[key] = pygame.time.get_ticks()
                color_angle = current_time * 0.01
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                key_rgb_values[key] = (r, g, b)

            if key_press_timers[key] != 0 and pygame.time.get_ticks() - key_press_timers[key] < 5000:
                color = key_rgb_values[key]
            else:
                key_press_timers[key] = 0
                key_rgb_values[key] = (255, 255, 255)

            key_surface = font.render(key, True, color)
            key_width = key_surface.get_width()
            key_height = key_surface.get_height()
            wave_y = key_y_position + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
            screen.blit(key_surface, (key_x_positions[i], wave_y))
                
                
        # Draw animation frames if triggered
        if animation_start_time is not None:
            elapsed_time = pygame.time.get_ticks() - animation_start_time
            frame_duration = 1000 // FPS  # 60 FPS, so frame duration is about 16.67 ms
            animation_frame_index = elapsed_time // frame_duration
            if animation_frame_index < len(animation_frames):   
                screen.blit(animation_frames[animation_frame_index], (animation_x, animation_y))
            else:
                animation_start_time = None  # Stop animation when it finishes

        # Draw explosion frames if triggered
        if explosion_start_time is not None:
            elapsed_time = pygame.time.get_ticks() - explosion_start_time
            frame_duration = 1000 // FPS  # 60 FPS, so frame duration is about 16.67 ms
            explosion_frame_index = elapsed_time // frame_duration
            if explosion_frame_index < len(explosion_frames):
                screen.blit(explosion_frames[explosion_frame_index], (explosion_x, explosion_y))
            else:
                explosion_start_time = None  # Stop explosion when it finishes

        # Draw hit line
        pygame.draw.line(screen, WHITE, (0, HIT_Y + NOTE_HEIGHT // 2), (SCREEN_WIDTH, HIT_Y + NOTE_HEIGHT // 2))



        # Display score with wave motion
        font = pygame.font.Font('assets/upheavtt.ttf', 32)
        score_text = f'Score: {score}'
        base_x = 15  # Starting x position for the score text
        base_y = 15  # Starting y position for the score text
        wave_amplitude = 10
        wave_frequency = 0.005
        
        # Calculate the width of the entire score text
        text_width = sum(font.render(char, True, BLACK).get_width() for char in score_text)
        
        # Render each character of the score text
        if notes:
            for i, char in enumerate(score_text):
                char_surface = font.render(char, True, BLACK)
                char_width = char_surface.get_width()
                # Calculate the wave y-offset
                wave_y = base_y + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
                screen.blit(char_surface, (base_x, wave_y))
                # Update the x position for the next character
                base_x += char_width

            base_x = 10  # Starting x position for the score text
            base_y = 10  # Starting y position for the score text
            for i, char in enumerate(score_text):
                char_surface = font.render(char, True, WHITE)
                char_width = char_surface.get_width()
                # Calculate the wave y-offset
                wave_y = base_y + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
                screen.blit(char_surface, (base_x, wave_y))
                # Update the x position for the next character
                base_x += char_width
            fade_in_start_time = None
        else:
            if fade_in_start_time is None:
                fade_in_start_time = pygame.time.get_ticks()

            fade_out_time = 1000  # 1 second
            fade_in_time = 1000  # 1 second
            fade_out_start_time = pygame.time.get_ticks() - fade_out_time

            font = pygame.font.Font('assets/upheavtt.ttf', 32)
            score_text = f'Score: {score}'
            base_x = 15  # Starting x position for the score text
            base_y = 15  # Starting y position for the score text
            wave_amplitude = 10
            wave_frequency = 0.005

            fade_out_alpha = int(255 * (1 - (pygame.time.get_ticks() - fade_out_start_time) / fade_out_time))
            if fade_out_alpha < 0:
                fade_out_alpha = 0
            for i, char in enumerate(score_text):
                char_surface = font.render(char, True, (0, 0, 0, fade_out_alpha))
                char_surface.set_alpha(fade_out_alpha)
                char_width = char_surface.get_width()
                # Calculate the wave y-offset
                wave_y = base_y + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
                screen.blit(char_surface, (base_x, wave_y))
                # Update the x position for the next character
                base_x += char_width

            base_x = 10  # Starting x position for the score text
            base_y = 10  # Starting y position for the score text
            for i, char in enumerate(score_text):
                char_surface = font.render(char, True, (255, 255, 255, fade_out_alpha))
                char_surface.set_alpha(fade_out_alpha)
                char_width = char_surface.get_width()
                # Calculate the wave y-offset
                wave_y = base_y + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
                screen.blit(char_surface, (base_x, wave_y))
                # Update the x position for the next character
                base_x += char_width

            font = pygame.font.Font('assets/upheavtt.ttf', 30)
            score_text = f'Score: {score}'
            base_x = SCREEN_WIDTH / 2 - text_width / 2
            base_y = SCREEN_HEIGHT / 2 - 32
            color_angle = current_time * 0.01
            r = int(math.sin(color_angle) * 128 + 128)
            g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
            b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
            fade_in_alpha = int(255 * (pygame.time.get_ticks() - fade_in_start_time) / fade_in_time)
            if fade_in_alpha > 255:
                fade_in_alpha = 255
            for i, char in enumerate(score_text):
                char_surface = font.render(char, True, (r, g, b))
                char_surface.set_alpha(fade_in_alpha)
                char_width = char_surface.get_width()
                # Calculate the wave y-offset
                wave_y = base_y + wave_amplitude * math.sin(current_time * wave_frequency + i * 0.5)
                screen.blit(char_surface, (base_x, wave_y))
                # Update the x position for the next character
                base_x += char_width

        
            # Draw the back to menu button
            button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 50, 200, 50)
            button_color = (255, 255, 255)
            button_hover_color = (200, 200, 200)
            button_text_color = (0, 0, 0)
            button_font = pygame.font.Font('assets/upheavtt.ttf', 24)
            button_text = 'Back to Menu'
            button_text_surface = button_font.render(button_text, True, button_text_color)

            if fade_in_start_time is None:
                fade_in_start_time = pygame.time.get_ticks()
                fade_in_time = 1000  # 1 second

            fade_in_alpha = int(255 * (pygame.time.get_ticks() - fade_in_start_time) / fade_in_time)
            if fade_in_alpha > 255:
                fade_in_alpha = 255

            if button_rect.collidepoint(pygame.mouse.get_pos()):
                # RGB reactive color
                color_angle = current_time * 0.01
                r = int(math.sin(color_angle) * 128 + 128)
                g = int(math.sin(color_angle + 2 * math.pi / 3) * 128 + 128)
                b = int(math.sin(color_angle + 4 * math.pi / 3) * 128 + 128)
                button_text_color = (r, g, b)

            # Draw the button
            pygame.draw.rect(screen, button_color, button_rect, border_radius=10)

            # Draw the text
            text_x = button_rect.x + 25
            text_y = button_rect.y + 15 + math.sin(current_time * 0.01) * 5
            button_text_surface = button_font.render(button_text, True, button_text_color)
            button_text_surface.set_alpha(fade_in_alpha)
            screen.blit(button_text_surface, (text_x, text_y))

            # Cyberpunk style border
            pygame.draw.rect(screen, (255, 255, 255), (button_rect.x - 2, button_rect.y - 2, button_rect.width + 4, button_rect.height + 4), 1, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), (button_rect.x - 4, button_rect.y - 4, button_rect.width + 8, button_rect.height + 8), 1, border_radius=10)

            # Check for button click
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        # Stop the music
                        pygame.mixer.music.stop()
                        song_playing = False
                        # Fade out the screen
                        fade_out_start_time = pygame.time.get_ticks()
                        fade_out_time = 500  # 0.5 seconds
                        state = STATE_FADE_OUT
    elif state == STATE_FADE_OUT:
        # Fade out the screen
        fade_out_alpha = int(255 * (1 - (pygame.time.get_ticks() - fade_out_start_time) / fade_out_time))
        if fade_out_alpha < 0:
            fade_out_alpha = 0
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, fade_out_alpha))
        screen.blit(s, (0, 0))

        # Check if fade out is complete
        if fade_out_alpha == 0:
            state = STATE_FADE_IN
            fade_in_start_time = pygame.time.get_ticks()
            fade_in_time = 500  # 0.5 seconds                    
        
    
    elif state == STATE_FADE_IN:
        # Fade in the menu screen
        fade_in_alpha = int(255 * (pygame.time.get_ticks() - fade_in_start_time) / fade_in_time)
        if fade_in_alpha > 255:
            fade_in_alpha = 255
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 255 - fade_in_alpha))
        screen.blit(s, (0, 0))


        # Draw the menu
        menu.draw(screen, menu_font)

        # Check if fade in is complete
        if fade_in_alpha == 255:
            state = STATE_MENU 

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()