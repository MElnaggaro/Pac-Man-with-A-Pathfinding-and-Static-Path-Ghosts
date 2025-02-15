import pygame
import random

# Initialize pygame
pygame.init()

# Define screen dimensions and grid size
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
GRID_SIZE = 20 

# Define colors
PACMAN_COLOR = (255, 255, 0)  # Yellow for Pac-Man
GHOST_COLOR = (255, 0, 0)  # Red for Ghosts
WALL_COLOR = (0, 0, 255)  # Blue for Walls
PELLET_COLOR = (0, 255, 255)  # Cyan for Pellets
BACKGROUND_COLOR = (0, 0, 0)  # Black for the background

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man Game")

# Define possible movement directions (right, left, down, up)
DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

def create_grid():
    """
    Creates the grid for the game, populating it with walls and pellets.
    
    Returns:
        grid (list): A 2D list representing the game grid.
        pellets (list): A list of coordinates where pellets are located.
    """
    grid = []
    pellets = []
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        row = []
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            if random.random() < 0.1:
                row.append(1)  # Wall
            else:
                row.append(0)  # Empty space
                if len(pellets) < 10 and random.random() < 0.1:  # Place pellets
                    row[-1] = 2  # Pellet
                    pellets.append((x // GRID_SIZE, y // GRID_SIZE))  # Store pellet position
        grid.append(row)
    return grid, pellets

def a_star_search(start, goal, grid):
    """
    Performs A* search to find the shortest path from the start to the goal.
    
    Args:
        start (tuple): The starting position (x, y).
        goal (tuple): The goal position (x, y).
        grid (list): The game grid containing walls and empty spaces.
    
    Returns:
        list: The path from start to goal, or an empty list if no path exists.
    """
    open_nodes = [(start, 0)]  # Nodes to explore, with initial cost 0
    visited_nodes = {}  # Dictionary to track the cost of visited nodes
    path_tracker = {}  # Dictionary to track the path for reconstruction

    while open_nodes:
        open_nodes.sort(key=lambda x: x[1] + manhattan_distance(x[0], goal))  # Sort by cost + heuristic
        current_node, g_cost = open_nodes.pop(0)

        # If goal is reached, reconstruct the path
        if current_node == goal:
            path = []
            while current_node in path_tracker:
                path.append(current_node)
                current_node = path_tracker[current_node]
            path.reverse()  # Reverse the path to get it from start to goal
            return path  

        visited_nodes[current_node] = g_cost  # Mark node as visited

        # Explore neighbors
        for dx, dy in DIRECTIONS:
            neighbor = (current_node[0] + dx, current_node[1] + dy)
            if (0 <= neighbor[0] < SCREEN_WIDTH // GRID_SIZE and
                0 <= neighbor[1] < SCREEN_HEIGHT // GRID_SIZE and
                grid[neighbor[1]][neighbor[0]] != 1):  # Ensure the neighbor is within bounds and not a wall

                new_cost = g_cost + 1  # Increment cost for moving to a neighbor

                if neighbor not in visited_nodes or new_cost < visited_nodes[neighbor]:
                    visited_nodes[neighbor] = new_cost
                    open_nodes.append((neighbor, new_cost))
                    path_tracker[neighbor] = current_node

    return []  # Return an empty path if no path found

def manhattan_distance(a, b):
    """
    Computes the Manhattan distance between two points.
    
    Args:
        a (tuple): The first point (x, y).
        b (tuple): The second point (x, y).
    
    Returns:
        int: The Manhattan distance between the points.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

class PacMan:
    """
    Represents the Pac-Man character, its position, and score.
    """
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 // GRID_SIZE
        self.y = SCREEN_HEIGHT // 2 // GRID_SIZE
        self.score = 0

    def move(self, goal, grid):
        """
        Moves Pac-Man towards the goal using A* search.
        
        Args:
            goal (tuple): The goal position (x, y).
            grid (list): The game grid.
        """
        path = a_star_search((self.x, self.y), goal, grid)
        if path:
            next_step = path[0]  # Move to the next step in the path
            self.x, self.y = next_step

    def collect_pellet(self, grid, pellets):
        """
        Collects a pellet if Pac-Man is on its position and updates the score.
        
        Args:
            grid (list): The game grid.
            pellets (list): The list of remaining pellets.
        """
        if (self.x, self.y) in pellets:
            pellets.remove((self.x, self.y))  # Remove pellet from the list
            self.score += 1  # Increase score

class Ghost:
    """
    Represents a ghost in the game, which can move towards Pac-Man.
    """
    def __init__(self, x, y, is_ai_ghost=False):  
        self.x = x  
        self.y = y  
        self.is_ai_ghost = is_ai_ghost  # Whether this ghost uses AI

    def move(self, pacman, grid):
        """
        Moves the ghost towards Pac-Man. If AI ghost, uses A* search.
        
        Args:
            pacman (PacMan): The Pac-Man object.
            grid (list): The game grid.
        """
        try:
            if self.is_ai_ghost:  # AI-controlled ghost
                path = a_star_search((self.x, self.y), (pacman.x, pacman.y), grid)
                if path:
                    next_step = path[0]  # Move to the next step in the path
                    self.x, self.y = next_step 
            else:  # Random movement for non-AI ghost
                if random.random() < 0.4:  # 40% chance to use A* for random ghost
                    path = a_star_search((self.x, self.y), (pacman.x, pacman.y), grid)
                    if path:
                        next_step = path[0]  
                        self.x, self.y = next_step  
                    else:
                        dx, dy = random.choice(DIRECTIONS)  # Move randomly
                        self.x += dx  
                        self.y += dy  
                else:
                    dx, dy = random.choice(DIRECTIONS)  # Move randomly
                    self.x += dx  
                    self.y += dy  
        except Exception as e:
            print(f"Error moving ghost at ({self.x}, {self.y}): {e}")  # Error handling for unexpected issues

# Initialize game elements
grid, pellets = create_grid()
pacman = PacMan()
ghosts = [Ghost(random.randint(0, SCREEN_WIDTH // GRID_SIZE - 1),
                random.randint(0, SCREEN_HEIGHT // GRID_SIZE - 1),
                is_ai_ghost=(i == 0))  # First ghost is AI-controlled
               for i in range(4)]  # Create 4 ghosts

# Game loop
running = True
clock = pygame.time.Clock()
game_over = ""

while running:
    try:
        screen.fill(BACKGROUND_COLOR)

        # Check for game over condition (all pellets collected)
        if len(pellets) == 0:
            game_over = "Pac-Man Won!"
            running = False

        # Move Pac-Man towards the first pellet (if any)
        if pellets:
            pacman.move(pellets[0], grid)
            pacman.collect_pellet(grid, pellets)

        # Move ghosts and check for collision with Pac-Man
        for ghost in ghosts:
            ghost.move(pacman, grid)
            if ghost.x == pacman.x and ghost.y == pacman.y:
                game_over = "Game Over!"
                running = False

        # Draw the grid (walls)
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if grid[y][x] == 1:  # Wall
                    pygame.draw.rect(screen, WALL_COLOR, pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                elif grid[y][x] == 0:  # Empty space
                    pygame.draw.rect(screen, BACKGROUND_COLOR, pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Draw pellets
        for pellet in pellets:
            pygame.draw.rect(screen, PELLET_COLOR, pygame.Rect(pellet[0] * GRID_SIZE + 4, pellet[1] * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8))

        # Draw Pac-Man
        pygame.draw.rect(screen, PACMAN_COLOR, pygame.Rect(pacman.x * GRID_SIZE, pacman.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Draw ghosts
        for ghost in ghosts:
            ghost_color = GHOST_COLOR if not ghost.is_ai_ghost else (0, 255, 0)  # AI ghosts are green
            pygame.draw.rect(screen, ghost_color, pygame.Rect(ghost.x * GRID_SIZE, ghost.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Display the score
        score_font = pygame.font.Font(None, 30)
        score_text = score_font.render(f"Score: {pacman.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        # Display game over message
        if game_over:
            font = pygame.font.Font(None, 50)
            text = font.render(game_over, True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

        pygame.display.flip()  # Update the display
        clock.tick(10)  # Set the game speed

    except Exception as e:
        print(f"Error during game loop: {e}")

# Quit pygame
pygame.quit()

