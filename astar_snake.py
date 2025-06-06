import pygame
import random
import heapq
import math

# Game settings
WIDTH, HEIGHT = 700, 700
CELL_SIZE = 25
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN , LEFT, RIGHT]


def random_position(snake): # This function puts the food in the screen
    while True:
        pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        if pos not in snake:
            return pos

def draw_rect(screen, color, pos):
    rect = pygame.Rect(pos[0]*CELL_SIZE, pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)

def astar(start, goal, snake_body):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: abs(goal[0] - start[0]) + abs(goal[1] - start[1])}
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            # Reconstruct path
            path = []
            while current != start:
                path.append(tuple(current))
                current = came_from[current]
            path.reverse()
            return path
        neighbors = []
        for d in DIRECTIONS:
            neighbor = (current[0] + d[0], current[1] + d[1])
            if (0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT and
            (neighbor not in snake_body or neighbor == goal)):
                neighbors.append(neighbor)
        for neighbor in neighbors:
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + ((abs(goal[0] - neighbor[0]))**(1/10) + (abs(goal[1] - neighbor[1]))**(1/10))**(10)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None  # No path found

def find_path(snake,food):
    path_to_food = astar(snake[0], food, snake)
    if path_to_food:
        path_to_tail = astar(food, snake[-1], snake)
        if path_to_tail:
            path = list(path_to_food + path_to_tail)
        else:
            path_to_tail = astar(food, snake[-1], snake )
            if path_to_tail:
                path_to_food = astar(snake[0], food, snake + path_to_tail)
                if path_to_food:
                    path = list(path_to_food + path_to_tail)
                else:
                    path = astar(snake[0], snake[-1], snake)
            else:
                path = astar(snake[0], snake[-1], snake)
    else:
        path = astar(snake[0], snake[-1], snake)
    return(path)

def go_anywhere(snake):
    for d in DIRECTIONS:
        nx, ny = snake[0][0] + d[0], snake[0][1] + d[1]
        path = astar(snake[0], (nx,ny), snake)
        if path:
            break
        else:
            continue
    return path

def draw_snake(snake,screen):
    snake_len = len(snake)
    for i, s in enumerate(snake):
        ratio = i / max(snake_len - 1, 1)
        # Rainbow gradient using HSV to RGB conversion
        hue = int(360 * ratio)
        color = pygame.Color(0)
        color.hsva = (hue, 100, 100, 100)
        rect = pygame.Rect(s[0]*CELL_SIZE, s[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        # Gradually change the size from small (tail) to large (head)
        min_size = int(CELL_SIZE * 0.4)
        max_size = CELL_SIZE
        size = int(min_size + (max_size - min_size) * (1 - ratio))
        offset = (CELL_SIZE - size) // 2
        rect = pygame.Rect(s[0]*CELL_SIZE + offset, s[1]*CELL_SIZE + offset, size, size)
        pygame.draw.rect(screen, color, rect)
    
def draw_path(path,screen):
    if path:
        for pos in path:
            rect = pygame.Rect(pos[0]*CELL_SIZE, pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            # Gradient from white to black along the path
            path_len = len(path)
            if path_len > 1:
                idx = path.index(pos)
                ratio = idx / (path_len - 1)
            else:
                ratio = 0
            shade = int(255 * (1 - ratio))
            color = (shade, shade, shade)
            pygame.draw.rect(screen, color, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("A* Snake Game")
    clock = pygame.time.Clock()
    FPS = 60  # Increase FPS for faster game

    snake = [(GRID_WIDTH//2, GRID_HEIGHT//2), (GRID_WIDTH//2, GRID_HEIGHT//2 - 1)]  # Start with a snake of length 2
    next_pos = (GRID_WIDTH//2, GRID_HEIGHT//2 + 1)  # Start moving down
    food = random_position(snake)
    score = 0
    path = [(next_pos)]  # Start with the next position to move

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw everything
        screen.fill(BLACK)

        # Move snake
        next_pos = path[0]
        path.remove(next_pos)
        new_head = next_pos

        if new_head in snake and new_head != snake[-1]:
            print("ran into itself!")
            print(snake[0])
            print(new_head)
            break
        snake.insert(0, new_head)
        if new_head == food:
            score += 1
            food = random_position(snake)
        else:
            snake.pop()

        path = find_path(snake,food)

        if path is None:
            path = go_anywhere(snake)                   
        
        # Draw snake in rainbow gradient, fixed size
        draw_snake(snake, screen)
        # Draw the path to follow
        draw_path(path, screen)
        # Draw food as a yellow circle for visibility
        food_rect = pygame.Rect(food[0]*CELL_SIZE, food[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.ellipse(screen, (255, 0, 0), food_rect)
        pygame.display.flip()

    percentage = 100 * (len(snake) + 1) / (GRID_WIDTH * GRID_HEIGHT)
    print(f"Game Over! Score: {percentage:.2f}% percentage of grid filled")

    # Freeze the last frame before closing the window
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                waiting = False
        pygame.time.wait(50)
    pygame.quit()

if __name__ == "__main__":
    main()