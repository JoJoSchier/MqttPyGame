import pygame
import os
import random
import math
import sys
import paho.mqtt.client as mqtt
from queue import Queue
import ssl
from PIL import Image
import time

# MQTT Settings
BROKER = "xmas.coreflux.cloud"
PORT = 8883  # Secure port for TLS
TOPIC = "#"
MESSAGE_QUEUE = Queue()
connected = False

# Game Settings
MESSAGE_DELAY = 2000  # Delay in milliseconds before processing a new message
enemy_speed = 100  # Pixels per second for horizontal movement
enemy_drop_distance = 20  # Vertical drop when hitting the edge
direction = 1  # 1 for right, -1 for left
FPS = 60  # Frames per second
PLAY_AREA_HEIGHT = 810  # Top 75% of the screen

# Snowfall settings
snowflakes = []  # List of snowflakes
MAX_SNOWFLAKES = 100

# Font Colors
FONT_COLORS = [(239, 35, 60), (213, 242, 227), (115, 186, 155), (0, 62, 31), (217, 4, 41)]

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        connected = True
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC)  # Subscribe to all topics to receive retained messages
        print(f"Subscribed to topic: {TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")  # Convert bytes to string
        print(f"Received message on topic '{msg.topic}': {payload}")
        MESSAGE_QUEUE.put((msg.topic, payload))
    except Exception as e:
        print(f"Error decoding message: {e}")

# Initialize MQTT client with TLS
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Configure TLS
client.tls_set(cert_reqs=ssl.CERT_NONE)  # Bypass certificate verification
client.tls_insecure_set(True)

# Attempt to connect
print("Attempting to connect to the MQTT Broker...")
client.connect(BROKER, PORT, 60)

# Start the loop
client.loop_start()

# Wait for connection
while not connected:
    print("Waiting for connection...")
    time.sleep(1)

print("Starting the game...")

# Initialize Pygame
pygame.init()

# Initialize Pygame Mixer
pygame.mixer.init()

# Load the background music
pygame.mixer.music.load("mariah.mp3")

# Set volume (optional)
pygame.mixer.music.set_volume(0.7)

# Start playing the music
pygame.mixer.music.play(loops=-1)

# Load collision sound effect
collision_sound = pygame.mixer.Sound("explosion.mp3")  # Replace with your 8-bit sound file
collision_sound.set_volume(0.5)  # Adjust volume if needed

def load_gif_frames(gif_path):
    """Load frames from a GIF file and convert them to Pygame surfaces."""
    frames = []
    try:
        gif = Image.open(gif_path)
        for frame in range(gif.n_frames):  # Extract each frame
            gif.seek(frame)
            frame_image = gif.convert("RGBA")  # Ensure compatibility
            frame_surface = pygame.image.fromstring(
                frame_image.tobytes(), gif.size, "RGBA"
            )
            frames.append(frame_surface)
    except Exception as e:
        print(f"Error loading GIF: {e}")
    return frames

info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("A Very Schier Xmas")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (253, 103, 52)

# Fonts
try:
    emoji_font_path = os.path.join(os.getcwd(), "seguiemj.ttf")
    emoji_font = pygame.font.Font(emoji_font_path, 25)  # Uniform font size
except FileNotFoundError:
    print(f"Emoji font not found at {emoji_font_path}, falling back to default font.")
    emoji_font = pygame.font.Font(None, 40)  # Fallback font for emojis

font = pygame.font.Font(None, 32)  # Regular text font
menu_font = pygame.font.Font(None, 100)
button_font = pygame.font.Font(None, 64)
over_font = pygame.font.Font(None, 80)

# Load Images
santa_image = pygame.image.load("santa.png")
santa_image = pygame.transform.scale(santa_image, (80, 120))  # Resize to fit game
candy_cane_image = pygame.image.load("cane.png")
candy_cane_image = pygame.transform.scale(candy_cane_image, (60, 80))  # Resize to fit laser

# Load the background image
background_image = pygame.image.load("bg.jpg")  # Replace with your image file
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Scale to fit screen

# Load Celebration GIF Frames
gif_path = "game_over_santa.gif"  # Path to your animated GIF file
gif_frames = load_gif_frames(gif_path)


# Player
player_x = SCREEN_WIDTH / 2
player_y = SCREEN_HEIGHT - 70
player_x_change = 0

# Messages (Characters as Enemies)
messages = []  # List of dictionaries: {"chars": [...], "x": x, "y": y, "direction": direction}

# Bullet
bullet_x = 0
bullet_y = player_y
bullet_y_change = -18  # Speed of the bullet (candy cane)
bullet_state = "ready"

# Score
score_value = 0
text_x = 10
text_y = 10

# Clock for frame rate control
clock = pygame.time.Clock()
last_message_time = pygame.time.get_ticks()

def draw_snowflakes():
    for snowflake in snowflakes:
        snowflake["y"] += snowflake["speed"] * 0.2  # Adjusted snowfall speed
        if snowflake["y"] > SCREEN_HEIGHT:
            snowflake.update({"x": random.randint(0, SCREEN_WIDTH), "y": random.randint(-100, -10)})
        pygame.draw.circle(screen, WHITE, (int(snowflake["x"]), int(snowflake["y"])), 2)

def create_snowflake():
    return {"x": random.randint(0, SCREEN_WIDTH), "y": random.randint(-100, -10), "speed": random.uniform(5, 50)}

for _ in range(MAX_SNOWFLAKES):
    snowflakes.append(create_snowflake())

def render_colored_text(text, font, colors):
    surfaces = []
    for i, char in enumerate(text):
        color = colors[i % len(colors)]
        surfaces.append(font.render(char, True, color))
    return surfaces

def menu():
    while True:
        screen.fill(BLACK)
        draw_snowflakes()
        title = render_colored_text("A Very Schier Xmas", menu_font, FONT_COLORS)
        title_x = SCREEN_WIDTH // 2 - sum(surface.get_width() for surface in title) // 2
        x_offset = 0
        for surface in title:
            screen.blit(surface, (title_x + x_offset, 200))
            x_offset += surface.get_width()

        start_button = button_font.render("Start", True, WHITE)
        exit_button = button_font.render("Exit", True, WHITE)
        start_rect = start_button.get_rect(center=(SCREEN_WIDTH // 2, 400))
        exit_rect = exit_button.get_rect(center=(SCREEN_WIDTH // 2, 500))

        mx, my = pygame.mouse.get_pos()
        if start_rect.collidepoint((mx, my)):
            start_button = button_font.render("Start", True, ORANGE)
        if exit_rect.collidepoint((mx, my)):
            exit_button = button_font.render("Exit", True, ORANGE)

        screen.blit(start_button, start_rect)
        screen.blit(exit_button, exit_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(event.pos):
                    return
                if exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(FPS)

menu()

# Functions
def player(x, y):
    screen.blit(santa_image, (int(x) - 30, int(y) - 30))  # Center image on player position

def enemy(char, x, y, color):
    try:
        if ord(char) > 1000:  # Use emoji font for emojis
            text_surface = emoji_font.render(char, True, WHITE)
        else:  # Use regular font for text
            text_surface = font.render(char, True, color)

        scaled_surface = pygame.transform.scale(text_surface, (20, 35))
        screen.blit(scaled_surface, (x, y))
    except pygame.error as e:
        print(f"⚠️ Skipping unsupported character: '{char}' (Error: {e})")

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(candy_cane_image, (x - 10, y))  # Center the candy cane on the x-coordinate

def show_score(x, y, score):
    score_render = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_render, (x, y))
    
    
def display_gif(frames, x, y, delay=100):
    """Displays a sequence of images (GIF frames) at the specified location."""
    if not frames:
        print("No GIF frames loaded.")
        return
    for frame in frames:
        screen.fill(BLACK)  # Clear the screen before drawing each frame
        screen.blit(frame, (x, y))
        pygame.display.update()
        pygame.time.delay(delay)  # Delay for the animation    

def game_over():
    frame_index = 0
    frame_delay = 100  # Milliseconds per frame
    last_frame_time = pygame.time.get_ticks()

    while True:
        # Clear the screen
        screen.fill(BLACK)

        # Draw "GAME OVER" text
        over_text = over_font.render("GAME OVER", True, WHITE)
        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, 100))

        # Draw the messages
        messages_to_show = ["You deleted all messages!","Wait, do you think that's a nice thing to do???", "How will Santa read the messages from the kids?", "Omg, you've been a naughty kid, you deserve coal for xmas..." "Praise Jesus! xD"]
        y_offset = 200  # Start drawing messages below the "GAME OVER" text
        for msg in messages_to_show:
            text = font.render(msg, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 50  # Move down for the next message

        # Draw the GIF frame
        if gif_frames:
            current_time = pygame.time.get_ticks()
            if current_time - last_frame_time > frame_delay:
                frame_index = (frame_index + 1) % len(gif_frames)
                last_frame_time = current_time
            gif_x_position = SCREEN_WIDTH // 2 - gif_frames[frame_index].get_width() // 2
            gif_y_position = y_offset + 50  # Leave extra space after the last message
            screen.blit(gif_frames[frame_index], (gif_x_position, gif_y_position))

        # Update the display
        pygame.display.update()

        # Event handling to exit the game over screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    

def is_collision(char_x, char_y, bullet_x, bullet_y):
    distance = math.hypot(char_x - bullet_x, char_y - bullet_y)
    return distance < 20

# Pre-populate snowflakes
for _ in range(MAX_SNOWFLAKES):
    snowflakes.append(create_snowflake())

# Game Loop
running = True
while running:
    dt = clock.tick(FPS) / 1000  # Delta time in seconds
    screen.blit(background_image, (0, 0))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x_change = -300  # Pixels per second
            if event.key == pygame.K_RIGHT:
                player_x_change = 300
            if event.key == pygame.K_SPACE:
                if bullet_state == "ready":
                    bullet_x = player_x
                    bullet_y = player_y
                    fire_bullet(bullet_x, bullet_y)
            if event.key == pygame.K_s:  # Skip message
                if messages:
                    messages.pop(0)  # Remove the first message
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                player_x_change = 0

    # Process one message at a time (only if no active messages on screen)
    if not messages and not MESSAGE_QUEUE.empty():
        topic, payload = MESSAGE_QUEUE.get()
        print(f"Processing message from topic '{topic}' with payload: {payload}")
        chars = [char for char in payload if char.strip()]  # Filter invalid characters
        messages.append({"chars": chars, "x": 50, "y": 0, "direction": direction})
        
    if not messages and MESSAGE_QUEUE.empty():
        game_over()    

    # Update player position
    player_x += player_x_change * dt
    player_x = max(30, min(player_x, SCREEN_WIDTH - 30))

    # Snowfall movement
    draw_snowflakes()

   # Enemy (Character) movement
    for message in messages[:]:
        message["x"] += enemy_speed * message["direction"] * dt
        if message["x"] <= 10 or message["x"] >= SCREEN_WIDTH - 10:
            message["direction"] *= -1
            message["y"] += enemy_drop_distance

    # Draw each character
    for i, char in enumerate(message["chars"]):
        color = FONT_COLORS[i % len(FONT_COLORS)]
        enemy(char, message["x"] + i * 40, message["y"], color)

    # Collision detection
    for i, char in enumerate(message["chars"][:]):
        if is_collision(message["x"] + i * 40, message["y"], bullet_x, bullet_y):
            bullet_y = player_y
            bullet_state = "ready"
            score_value += 1
            del message["chars"][i]
            
            # Play collision sound
            collision_sound.play()

    if not message["chars"]:
        messages.remove(message)


    # Bullet movement
    if bullet_state == "fire":
        fire_bullet(bullet_x, bullet_y)
        bullet_y += bullet_y_change
        if bullet_y <= 0:
            bullet_y = player_y
            bullet_state = "ready"

    # Draw player and show score
    player(player_x, player_y)
    show_score(text_x, text_y, score_value)

    # Update the display
    pygame.display.update()

pygame.quit()
client.loop_stop()
sys.exit()