import argparse
import pygame

from logger import Logger
import control
from constants import *
from game import *

# Initialize Pygame
pygame.init()
game = Game(reference_type=sim.SineReference)

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font(pygame.font.get_default_font(), 24)
pygame.display.set_caption("ball game")

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
pid = control.pid(0.05, 0, 0)

parser = argparse.ArgumentParser()
parser.add_argument('--operator', default='human')
args = parser.parse_args()

# Game Loop
while running:
    
    ### get action ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if args.operator == "human":
            if event.type == pygame.MOUSEBUTTONDOWN:
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
              
    error = game.reference.get_error(game.ball)      
    if args.operator == "pid":
        action = pid.control(error)
    
    # print(f"{game.step}\t{action}\t{error}\t({game.ball.x}, {game.ball.y})")
    
    ### Update game state ----------
    ep_done, game_done = game.step(action)
    if ep_done:
        game.reset()
        handle_x = slider_x + (slider_width / 2)
        action = 0.0
    if game_done:
        running = False

    ### Render ----------
    screen.fill(WHITE)

    # Draw gameplay area
    pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, GAME_HEIGHT))

    # Draw reference line
    line_y_values = game.reference.values
    for x in range(len(line_y_values) - 1):
        pygame.draw.line(screen, BLACK,
                         (x, line_y_values[x]),
                         (x + 1, line_y_values[x + 1]))

    # Draw blue ball
    pygame.draw.circle(screen, BLUE, (int(game.ball.x), int(game.ball.y)), BALL_RADIUS)

    # Draw slider track
    pygame.draw.rect(screen, GRAY, (slider_x, slider_y, slider_width, slider_height))

    # Draw slider handle
    pygame.draw.circle(screen, DARK_GRAY, (int(handle_x), int(handle_y)), handle_radius)

    # Add text
    gui_str = f"step: {game.info.step}, episode: {game.info.episode}"
    gui_text = font.render(gui_str, True, (0, 0, 0))
    screen.blit(gui_text, dest=(0,0))

    # Update the display
    pygame.display.flip()

    # Frame rate
    clock.tick(FPS)
    
    ### Logging ----------
    logger.log(game=game, action=action)

logger.write(directory='data')
pygame.quit()
