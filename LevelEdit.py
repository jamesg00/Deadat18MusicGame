import json
import pygame
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
LANE_WIDTH = SCREEN_WIDTH // 4
LANES = [LANE_WIDTH * i + LANE_WIDTH // 2 for i in range(4)]
KEYS = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]
LANE_MAPPING = {pygame.K_a: 0, pygame.K_s: 1, pygame.K_d: 2, pygame.K_f: 3}

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Level Editor')


pygame.mixer.music.load('assets/Awesomenarnia 124 (1).mp3')
pygame.mixer.music.play()



# Clock to control the frame rate
clock = pygame.time.Clock()
start_time = None

# List to store note data
notes = []

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in LANE_MAPPING:
                if start_time is None:
                    start_time = time.time()
                current_time = (time.time() - start_time) * 1000  # in milliseconds
                lane = LANE_MAPPING[event.key]
                notes.append({"time": current_time, "lane": lane})
                print(f'Note added at {current_time:.2f} ms in lane {lane}')

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the lanes
    for lane in LANES:
        pygame.draw.line(screen, (255, 255, 255), (lane, 0), (lane, SCREEN_HEIGHT))

    # Refresh the screen
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()

# Save notes to a file
with open('json/level.json', 'w') as f:
    json.dump(notes, f, indent=4)
