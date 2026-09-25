import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BG_COLOR = (30, 30, 30)
CIRCLE_COLOR = (0, 150, 255)
GRID_LINE_COLOR = (50, 50, 50)
CIRCLE_RADIUS = 15
GRID_SPACING = 60  # Distance between circles

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Draggable Grid View")
clock = pygame.time.Clock()

# Camera offset variables
camera_x = 0
camera_y = 0
dragging = False
drag_start_x = 0
drag_start_y = 0

# Game loop
running = True
while running:
    # 1. Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click starts dragging
                dragging = True
                mouse_x, mouse_y = event.pos
                # Record where the drag started relative to the current camera position
                drag_start_x = mouse_x - camera_x
                drag_start_y = mouse_y - camera_y
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_x, mouse_y = event.pos
                # Update camera offset based on mouse movement
                camera_x = mouse_x - drag_start_x
                camera_y = mouse_y - drag_start_y

    # 2. Clear Screen
    screen.fill(BG_COLOR)

    # 3. Dynamic Culling & Rendering Logic
    # Determine the range of grid indices currently visible on screen
    start_col = int((-camera_x - CIRCLE_RADIUS) // GRID_SPACING)
    end_col = int((WIDTH - camera_x + CIRCLE_RADIUS) // GRID_SPACING) + 1
    
    start_row = int((-camera_y - CIRCLE_RADIUS) // GRID_SPACING)
    end_row = int((HEIGHT - camera_y + CIRCLE_RADIUS) // GRID_SPACING) + 1

    # Draw the visible grid circles
    for col in range(start_col, end_col):
        for row in range(start_row, end_row):
            # Calculate world position
            world_x = col * GRID_SPACING
            world_y = row * GRID_SPACING
            
            # Translate world position to screen position via camera offsets
            screen_x = world_x + camera_x
            screen_y = world_y + camera_y
            
            # Double check boundary culling before committing to drawing
            if -CIRCLE_RADIUS <= screen_x <= WIDTH + CIRCLE_RADIUS and -CIRCLE_RADIUS <= screen_y <= HEIGHT + CIRCLE_RADIUS:
                pygame.draw.circle(screen, CIRCLE_COLOR, (int(screen_x), int(screen_y)), CIRCLE_RADIUS)

    # 4. Flip Buffers & Maintain Frame Rate
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()