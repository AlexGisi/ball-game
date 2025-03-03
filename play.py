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
font = pygame.font.Font(pygame.font.get_default_font(), 16)
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

parser = argparse.ArgumentParser()
parser.add_argument('--operator', default='human')
parser.add_argument('--gain', default=1.0)
args = parser.parse_args()

logger = Logger(directory='data', name=str(args.gain))
pid = control.pid(0.05, 0.0, 0.0)
hom = control.OperatorModel(game.ball)


# Game Loop
while running:
    
    ### get action ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if args.operator == "human" and game.info.episode_step > WARMUP_LENGTH:
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
              
    # error = game.reference.get_error(game.ball)
    y_ref = game.reference.y_ref()
    y_ball = game.ball.position()   
    if args.operator == "pid":
        action = pid.control(y_ref, y_ball)
    elif args.operator == "hom":
        action = hom.control(y_ref, y_ball)
    
    print(f"{action:.2f}, y_ref: {y_ref:.2f}, y_ball: {y_ball:.2f}")
    
    ### Update game state ----------
    # print(action)
    action *= float(args.gain)
    ep_done, game_done = game.step(action)

    ### Render ----------
    screen.fill(WHITE)

    # Draw gameplay area
    pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, GAME_HEIGHT))

    # Draw reference line
    line_y_values = game.reference.values
    for x in range(len(line_y_values) - 1):
        pygame.draw.line(screen, BLACK,
                         (x, line_y_values[x] + (GAME_HEIGHT / 2)),
                         (x + 1, line_y_values[x + 1] + (GAME_HEIGHT / 2)))

    # Draw blue ball
    pygame.draw.circle(screen, BLUE, (int(game.ball.x), (GAME_HEIGHT / 2) + int(game.ball.position())), BALL_RADIUS)

    # Draw slider track
    pygame.draw.rect(screen, GRAY, (slider_x, slider_y, slider_width, slider_height))

    # Draw slider handle
    pygame.draw.circle(screen, DARK_GRAY, (int(handle_x), int(handle_y)), handle_radius)

    # Add text
    time_str = f"step: {game.info.step}, episode: {game.info.episode}, episode step: {game.info.episode_step}"
    time_text = font.render(time_str, True, (0, 0, 0))
    screen.blit(time_text, dest=(0,0))
    
    costs = game.info.episode_costs()
    cost_str = f"cost: {costs[-1]:.2f}, mean: {sum(costs)/len(costs):.2f}, sum: {sum(costs):.2f}"
    gui_text = font.render(cost_str, True, (0, 0, 0))
    screen.blit(gui_text, dest=(SCREEN_WIDTH-300,0))
        
    if game.info.episode_step < WARMUP_LENGTH:
        warmup_str = font.render("WARM UP", True, (0, 0, 0))
        screen.blit(warmup_str, dest=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    # Update the display
    pygame.display.flip()

    # Frame rate
    clock.tick(FPS)
    
    ### Logging ----------
    logger.log(game=game, action=action)
    
    ### ----------
    # Must be the last thing done, otherwise the reset() can cause out of bounds
    if ep_done:
        game.reset()
        hom.reset()  # todo
        handle_x = slider_x + (slider_width / 2)
        action = 0.0
    if game_done:
        running = False

logger.write()
pygame.quit()
