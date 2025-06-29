
import pygame
import sys
import random
import math

# --- Game Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GREY = (50, 50, 50)
PLAYER_COLOR = BLUE
ENEMY_COLOR = RED
PROJECTILE_COLOR = YELLOW
MULTI_SHOT_PROJECTILE_COLOR = (255, 165, 0) # Orange for multi-shot projectiles

# Player settings
PLAYER_SIZE = 30
PLAYER_SPEED = 5
PLAYER_HEALTH = 100
PLAYER_SHOOT_COOLDOWN_NORMAL = 150 # Decreased from 300 for faster normal shot
PLAYER_SHOOT_COOLDOWN_MULTI = 300 # Decreased from 600 for faster multi-shot

# Enemy settings
ENEMY_SIZE = 25
ENEMY_SPEED = 2
ENEMY_HEALTH = 20 # Changed from 30 to 20
ENEMY_SPAWN_RATE = 1000 # milliseconds between spawns

# Projectile settings
PROJECTILE_SIZE = 8
PROJECTILE_SPEED = 10
PROJECTILE_DAMAGE = 10

# Game States
GAME_STATE_PLAYING = 0
GAME_STATE_GAME_OVER = 1

# Shooting Modes
SHOOTING_MODE_NORMAL = 0
SHOOTING_MODE_MULTI = 1

# --- Pygame Initialization ---
pygame.init()
pygame.mixer.init() # Initialize mixer for sounds (optional)

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple 2D Arena Survival (Very Not BGMI!)")
CLOCK = pygame.time.Clock()

# --- Fonts ---
FONT_SCORE = pygame.font.SysFont("arial", 30)
FONT_HEALTH = pygame.font.SysFont("arial", 20)
FONT_GAME_OVER = pygame.font.SysFont("arial", 60, bold=True)
FONT_RESTART = pygame.font.SysFont("arial", 30)
FONT_MODE = pygame.font.SysFont("arial", 20)

# --- Sounds (Optional: Replace with your own .wav files) ---
SHOOT_SOUND = None # Placeholder
HIT_SOUND = None # Placeholder
ENEMY_DEATH_SOUND = None # Placeholder
GAME_OVER_SOUND = None # Placeholder

try:
    SHOOT_SOUND = pygame.mixer.Sound("shoot.mp3") # Ensure this file exists
    HIT_SOUND = pygame.mixer.Sound("hit efftect.mp3")     # Ensure this file exists
    ENEMY_DEATH_SOUND = pygame.mixer.Sound("boom enemy death.mp3") # Ensure this file exists
    GAME_OVER_SOUND = pygame.mixer.Sound("game-over-deep-male-voice-clip-352695.mp3")      # Ensure this file exists
    SHOOT_SOUND.set_volume(0.3)
    HIT_SOUND.set_volume(0.5)
    ENEMY_DEATH_SOUND.set_volume(0.7)
    GAME_OVER_SOUND.set_volume(0.8)
except pygame.error:
    print("Warning: Sound files not found. Running without sounds.")
    SHOOT_SOUND = None
    HIT_SOUND = None
    ENEMY_DEATH_SOUND = None
    GAME_OVER_SOUND = None


# --- Game Classes ---

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - PLAYER_SIZE // 2, HEIGHT // 2 - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
        self.health = PLAYER_HEALTH
        self.speed = PLAYER_SPEED
        self.last_shot_time = 0
        self.shooting_mode = SHOOTING_MODE_NORMAL # New: default shooting mode

    def handle_input(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # Normalize diagonal movement speed
        if dx != 0 and dy != 0:
            factor = 1 / math.sqrt(2)
            dx *= factor
            dy *= factor

        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Keep player within screen bounds
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

    def shoot(self, target_pos): # Renamed mouse_pos to target_pos for clarity
        current_time = pygame.time.get_ticks()
        
        # Determine cooldown based on shooting mode
        cooldown = PLAYER_SHOOT_COOLDOWN_NORMAL
        if self.shooting_mode == SHOOTING_MODE_MULTI:
            cooldown = PLAYER_SHOOT_COOLDOWN_MULTI

        if current_time - self.last_shot_time > cooldown:
            self.last_shot_time = current_time
            
            projectiles_to_fire = []
            if self.shooting_mode == SHOOTING_MODE_NORMAL:
                # Calculate direction vector from player to target_pos
                dx = target_pos[0] - self.rect.centerx
                dy = target_pos[1] - self.rect.centery
                angle = math.atan2(dy, dx)
                projectiles_to_fire.append(Projectile(self.rect.centerx, self.rect.centery, angle, PROJECTILE_COLOR))
                if SHOOT_SOUND:
                    SHOOT_SOUND.play()
            elif self.shooting_mode == SHOOTING_MODE_MULTI:
                # Fire 8 projectiles in all cardinal and intercardinal directions
                num_projectiles = 8
                for i in range(num_projectiles):
                    angle = (2 * math.pi / num_projectiles) * i
                    projectiles_to_fire.append(Projectile(self.rect.centerx, self.rect.centery, angle, MULTI_SHOT_PROJECTILE_COLOR))
                if SHOOT_SOUND: # You might want a different sound for multi-shot
                    SHOOT_SOUND.play() # For now, re-use the same sound

            return projectiles_to_fire # Return a list of projectiles
        return [] # Return an empty list if not ready to shoot

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def draw(self, screen):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)
        # Draw health bar above player
        health_bar_width = self.rect.width
        health_bar_height = 5
        health_ratio = self.health / PLAYER_HEALTH
        current_health_width = health_bar_width * health_ratio
        
        health_bar_bg_rect = pygame.Rect(self.rect.x, self.rect.y - 10, health_bar_width, health_bar_height)
        health_bar_fg_rect = pygame.Rect(self.rect.x, self.rect.y - 10, current_health_width, health_bar_height)

        pygame.draw.rect(screen, DARK_GREY, health_bar_bg_rect)
        pygame.draw.rect(screen, GREEN, health_bar_fg_rect)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.health = ENEMY_HEALTH
        self.speed = ENEMY_SPEED

    def move_towards_player(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx_norm = dx / dist
            dy_norm = dy / dist
            self.rect.x += dx_norm * self.speed
            self.rect.y += dy_norm * self.speed

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        if HIT_SOUND:
            HIT_SOUND.play()

    def draw(self, screen):
        pygame.draw.rect(screen, ENEMY_COLOR, self.rect)
        # Draw health bar above enemy
        health_bar_width = self.rect.width
        health_bar_height = 3
        health_ratio = self.health / ENEMY_HEALTH
        current_health_width = health_bar_width * health_ratio
        
        health_bar_bg_rect = pygame.Rect(self.rect.x, self.rect.y - 8, health_bar_width, health_bar_height)
        health_bar_fg_rect = pygame.Rect(self.rect.x, self.rect.y - 8, current_health_width, health_bar_height)

        pygame.draw.rect(screen, DARK_GREY, health_bar_bg_rect)
        pygame.draw.rect(screen, YELLOW, health_bar_fg_rect) # Yellow for enemy health

class Projectile:
    def __init__(self, x, y, angle, color): # Added color parameter
        self.rect = pygame.Rect(x, y, PROJECTILE_SIZE, PROJECTILE_SIZE)
        self.speed = PROJECTILE_SPEED
        self.damage = PROJECTILE_DAMAGE
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.color = color # Store projectile color

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.rect.width // 2)

class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.projectiles = []
        self.score = 0
        self.game_state = GAME_STATE_PLAYING
        self.last_enemy_spawn_time = pygame.time.get_ticks()

    def reset_game(self):
        self.player = Player()
        self.enemies = []
        self.projectiles = []
        self.score = 0
        self.game_state = GAME_STATE_PLAYING
        self.last_enemy_spawn_time = pygame.time.get_ticks()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == GAME_STATE_PLAYING:
                    new_projectiles = self.player.shoot(event.pos) # Now returns a list
                    self.projectiles.extend(new_projectiles) # Add all new projectiles
                elif self.game_state == GAME_STATE_GAME_OVER:
                    # Check for click on restart button (simple click anywhere to restart for now)
                    self.reset_game()
            if event.type == pygame.KEYDOWN:
                if self.game_state == GAME_STATE_GAME_OVER and event.key == pygame.K_r:
                    self.reset_game()
                
                # --- MODIFICATION START ---
                # When space bar is pressed, fire projectiles in every direction (multi-shot)
                if self.game_state == GAME_STATE_PLAYING and event.key == pygame.K_SPACE:
                    # Temporarily change the player's shooting mode to multi-shot
                    original_mode = self.player.shooting_mode # Store current mode
                    self.player.shooting_mode = SHOOTING_MODE_MULTI # Set to multi-shot
                    
                    # Call shoot, target_pos doesn't matter for multi-shot as it's omnidirectional
                    new_projectiles = self.player.shoot((0,0)) # Dummy target for multi-shot
                    self.projectiles.extend(new_projectiles)
                    
                    # Restore the player's original shooting mode
                    self.player.shooting_mode = original_mode
                # --- MODIFICATION END ---
        return True

    def update_game_state(self):
        if self.game_state == GAME_STATE_PLAYING:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)

            # Spawn enemies
            current_time = pygame.time.get_ticks()
            if current_time - self.last_enemy_spawn_time > ENEMY_SPAWN_RATE:
                self.spawn_enemy()
                self.last_enemy_spawn_time = current_time

            # Update projectiles
            for projectile in self.projectiles:
                projectile.update()
            # Remove projectiles that are off-screen
            self.projectiles = [p for p in self.projectiles if 
                                0 <= p.rect.x <= WIDTH and 0 <= p.rect.y <= HEIGHT]

            # Update enemies
            for enemy in self.enemies:
                enemy.move_towards_player(self.player.rect)

            self.check_collisions()

            if self.player.health <= 0:
                self.game_state = GAME_STATE_GAME_OVER
                if GAME_OVER_SOUND:
                    GAME_OVER_SOUND.play()

    def check_collisions(self):
        # Projectile-Enemy collisions
        # Use reversed list for projectiles to safely remove during iteration
        for i in range(len(self.projectiles) - 1, -1, -1):
            projectile = self.projectiles[i]
            for j in range(len(self.enemies) - 1, -1, -1):
                enemy = self.enemies[j]
                if projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(projectile.damage)
                    # Remove projectile after hit
                    self.projectiles.pop(i) 
                    
                    if enemy.health <= 0:
                        self.enemies.pop(j) # Remove enemy if health is zero
                        self.score += 1000
                        if ENEMY_DEATH_SOUND:
                            ENEMY_DEATH_SOUND.play()
                    break # Projectile hit one enemy, so it's gone. Break from inner loop.

        # Enemy-Player collisions
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                self.player.take_damage(1) # Constant minor damage while colliding
                # Push enemy away slightly (very basic pushback)
                dx = enemy.rect.centerx - self.player.rect.centerx
                dy = enemy.rect.centery - self.player.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    push_force = 10
                    enemy.rect.x += (dx / dist) * push_force
                    enemy.rect.y += (dy / dist) * push_force

    def spawn_enemy(self):
        # Spawn enemy at a random edge of the screen
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, WIDTH - ENEMY_SIZE)
            y = -ENEMY_SIZE
        elif side == 'bottom':
            x = random.randint(0, WIDTH - ENEMY_SIZE)
            y = HEIGHT
        elif side == 'left':
            x = -ENEMY_SIZE
            y = random.randint(0, HEIGHT - ENEMY_SIZE)
        else: # 'right'
            x = WIDTH
            y = random.randint(0, HEIGHT - ENEMY_SIZE)
        self.enemies.append(Enemy(x, y))

    def draw_elements(self):
        SCREEN.fill(BLACK) # Background

        self.player.draw(SCREEN)
        for enemy in self.enemies:
            enemy.draw(SCREEN)
        for projectile in self.projectiles:
            projectile.draw(SCREEN)

        # Draw UI
        score_text = FONT_SCORE.render(f"Score: {self.score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        # Display current shooting mode
        mode_text = "Mode: "
        if self.player.shooting_mode == SHOOTING_MODE_NORMAL:
            mode_text += "Normal (Click)"
        else:
            mode_text += "Multi-Shot (Click)"
        
        mode_label = FONT_MODE.render(mode_text, True, WHITE)
        SCREEN.blit(mode_label, (10, 40)) # Position it below the score
        
        # Clarified hint for toggling and firing
        mode_toggle_hint = FONT_MODE.render("Click or Press 'SPACE' for Omni-Fire!", True, YELLOW) # Updated hint
        SCREEN.blit(mode_toggle_hint, (10, 70)) 
        mode_toggle_hint_2 = FONT_MODE.render("(Multi-Shot mode toggled by mouse click)", True, YELLOW) # New hint
        SCREEN.blit(mode_toggle_hint_2, (10, 90))

        if self.game_state == GAME_STATE_GAME_OVER:
            game_over_text = FONT_GAME_OVER.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            SCREEN.blit(game_over_text, game_over_rect)

            final_score_text = FONT_SCORE.render(f"Final Score: {self.score}", True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            SCREEN.blit(final_score_text, final_score_rect)

            restart_text = FONT_RESTART.render("Press 'R' or Click to Restart", True, GREEN)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
            SCREEN.blit(restart_text, restart_rect)


        pygame.display.flip() # Update the full display surface to the screen

    def run(self):
        running = True
        while running:
            running = self.handle_events() # Handle input and quitting

            if self.game_state == GAME_STATE_PLAYING:
                self.update_game_state() # Update game logic

            self.draw_elements() # Draw everything

            CLOCK.tick(FPS) # Cap the frame rate

        pygame.quit()
        sys.exit()

# --- Main Game Execution ---
if __name__ == "__main__":
    game = Game()
    game.run()
    