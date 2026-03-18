import pygame

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Logic Gate Simulator")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Gate logic functions
def AND(a, b): return a and b
def OR(a, b): return a or b
def NOT(a): return not a

# Draw gate shapes
def draw_and_gate(x, y, input_a, input_b):
    pygame.draw.rect(screen, BLACK, (x, y, 60, 60), 2)
    pygame.draw.circle(screen, BLACK, (x + 60, y + 30), 30, 2)
    output = AND(input_a, input_b)
    pygame.draw.circle(screen, GREEN if output else RED, (x + 100, y + 30), 10)
    return output

def draw_or_gate(x, y, input_a, input_b):
    pygame.draw.arc(screen, BLACK, (x, y, 80, 60), 3.14/2, -3.14/2, 2)
    output = OR(input_a, input_b)
    pygame.draw.circle(screen, GREEN if output else RED, (x + 100, y + 30), 10)
    return output

def draw_not_gate(x, y, input_a):
    pygame.draw.polygon(screen, BLACK, [(x, y), (x, y+60), (x+60, y+30)], 2)
    pygame.draw.circle(screen, BLACK, (x+70, y+30), 10, 2)
    output = NOT(input_a)
    pygame.draw.circle(screen, GREEN if output else RED, (x + 100, y + 30), 10)
    return output

# Main loop
running = True
input_a, input_b = True, False

while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:  # Toggle A
                input_a = not input_a
            elif event.key == pygame.K_b:  # Toggle B
                input_b = not input_b

    # Draw gates
    draw_and_gate(100, 100, input_a, input_b)
    draw_or_gate(100, 250, input_a, input_b)
    draw_not_gate(100, 400, input_a)

    # Display input states
    font = pygame.font.SysFont(None, 30)
    text_a = font.render(f"A: {'1' if input_a else '0'}", True, BLACK)
    text_b = font.render(f"B: {'1' if input_b else '0'}", True, BLACK)
    screen.blit(text_a, (10, 10))
    screen.blit(text_b, (10, 40))

    pygame.display.flip()

pygame.quit()