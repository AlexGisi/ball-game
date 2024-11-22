import pygame
import math

from logger import Logger
import sim
import control
from constants import *

# Initialize Pygame
pygame.init()

ball_x = SCREEN_WIDTH * 0.2

ball_state = sim.BallState(y=GAME_HEIGHT / 2, vy=0)
reference = sim.Reference()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ball game")

step_count = 0
running = True

# Slider Properties
slider_x = 50
slider_y = GAME_HEIGHT + (SLIDER_HEIGHT / 2) - 5  # Centered vertically in slider area
slider_width = SCREEN_WIDTH - 100
slider_height = 10

handle_radius = 15
handle_x = slider_x + (slider_width / 2)  # Start at the center
handle_y = slider_y + (slider_height / 2)

action = 0.0  # Initialize action at neutral, takes values in [-1, 1]
dragging = False  # Flag to indicate if the handle is being dragged

logger = Logger()

# Game Loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the mouse is over the handle
            mouse_x, mouse_y = event.pos
            if (mouse_x - handle_x) ** 2 + (mouse_y - handle_y) ** 2 <= handle_radius ** 2:
                dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_x, _ = event.pos
                # Constrain handle within slider track
                handle_x = max(slider_x, min(mouse_x, slider_x + slider_width))
                # Update action value based on handle position
                action = ((handle_x - slider_x) / slider_width)*2 - 1

    # Update reference line
    step_count += 1
    reference.step(step_count)

    # Update ball position
    ball_state.step(action)
    ball_state.clip()

    # Render
    screen.fill(WHITE)

    # Draw gameplay area
    pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, GAME_HEIGHT))

    # Draw reference line
    line_y_values = reference.get()
    for x in range(len(line_y_values) - 1):
        pygame.draw.line(screen, BLACK,
                         (x, line_y_values[x]),
                         (x + 1, line_y_values[x + 1]))

    # Draw blue ball
    pygame.draw.circle(screen, BLUE, (int(ball_x), int(ball_state.y)), BALL_RADIUS)

    # Draw slider track
    pygame.draw.rect(screen, GRAY, (slider_x, slider_y, slider_width, slider_height))

    # Draw slider handle
    pygame.draw.circle(screen, DARK_GRAY, (int(handle_x), int(handle_y)), handle_radius)

    # Update the display
    pygame.display.flip()

    # Frame rate
    clock.tick(FPS)
    
    logger.log(time_step=step_count,
               ball_state=ball_state,
               reference_state=line_y_values[int(ball_x)],
               action=action)

logger.write(directory='data')
pygame.quit()
