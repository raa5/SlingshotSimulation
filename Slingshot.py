import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravitational Slingshot Effect")

DEFAULT_PLANET_MASS = 100
DEFAULT_PLANET_RADIUS = 50
DEFAULT_SHIP_MASS = 5
G = 5
FPS = 60
OBJ_SIZE = 5
VEL_SCALE = 100

BG = pygame.transform.scale(pygame.image.load("background.jpg"), (WIDTH, HEIGHT))
PLANET_IMAGE = pygame.transform.scale(pygame.image.load("jupiter.png"), (DEFAULT_PLANET_RADIUS * 2, DEFAULT_PLANET_RADIUS * 2))

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

FONT = pygame.font.SysFont("Arial", 18)

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = BLUE if self.active else WHITE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, win):
        # Blit the text.
        win.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(win, self.color, self.rect, 2)

    def get_value(self):
        try:
            return float(self.text)
        except ValueError:
            return None

class Planet:
    def __init__(self, x, y, mass, radius):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = radius
        self.image = pygame.transform.scale(PLANET_IMAGE, (radius * 2, radius * 2))
    
    def draw(self):
        win.blit(self.image, (self.x - self.radius, self.y - self.radius))

class Spacecraft:
    def __init__(self, x, y, vel_x, vel_y, mass):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.mass = mass
        self.trail = [(self.x, self.y)]

    def move(self, planet=None):
        distance = math.sqrt((self.x - planet.x)**2 + (self.y - planet.y)**2)
        force = (G * self.mass * planet.mass) / distance ** 2
        
        acceleration = force / self.mass
        angle = math.atan2(planet.y - self.y, planet.x - self.x)

        acceleration_x = acceleration * math.cos(angle)
        acceleration_y = acceleration * math.sin(angle)

        self.vel_x += acceleration_x 
        self.vel_y += acceleration_y

        self.x += self.vel_x
        self.y += self.vel_y

        self.trail.append((self.x, self.y))
    
    def draw(self):
        pygame.draw.circle(win, RED, (int(self.x), int(self.y)), OBJ_SIZE)
        if len(self.trail) > 1:
            pygame.draw.lines(win, WHITE, False, [(int(x), int(y)) for x, y in self.trail], 1)

    def get_info(self, planet):
        distance = math.sqrt((self.x - planet.x)**2 + (self.y - planet.y)**2)
        escape_velocity = math.sqrt((2 * G * planet.mass) / distance)
        return f"Position: ({int(self.x)}, {int(self.y)})\nVelocity: ({self.vel_x:.2f}, {self.vel_y:.2f})\nEscape Velocity: {escape_velocity:.2f}"

def create_ship(location, mouse, ship_mass):
    t_x, t_y = location
    m_x, m_y = mouse
    vel_x = (m_x - t_x) / VEL_SCALE
    vel_y = (m_y - t_y) / VEL_SCALE
    obj = Spacecraft(t_x, t_y, vel_x, vel_y, ship_mass)
    return obj

def draw_info(text, x, y):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        info_surf = FONT.render(line, True, WHITE)
        win.blit(info_surf, (x, y + i * 20))

def main():
    running = True
    clock = pygame.time.Clock()

    # Input boxes for user-defined values
    planet_mass_box = InputBox(50, 50, 200, 30, str(DEFAULT_PLANET_MASS))
    planet_radius_box = InputBox(50, 100, 200, 30, str(DEFAULT_PLANET_RADIUS))
    ship_mass_box = InputBox(50, 150, 200, 30, str(DEFAULT_SHIP_MASS))
    input_boxes = [planet_mass_box, planet_radius_box, ship_mass_box]

    planet_mass = DEFAULT_PLANET_MASS
    planet_radius = DEFAULT_PLANET_RADIUS
    ship_mass = DEFAULT_SHIP_MASS

    planet = None
    objects = []
    trails = []
    temp_obj_pos = None
    simulation_started = False

    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not simulation_started:
                for box in input_boxes:
                    box.handle_event(event)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        planet_mass = planet_mass_box.get_value() or DEFAULT_PLANET_MASS
                        planet_radius = planet_radius_box.get_value() or DEFAULT_PLANET_RADIUS
                        ship_mass = ship_mass_box.get_value() or DEFAULT_SHIP_MASS
                        planet = Planet(WIDTH // 2, HEIGHT // 2, planet_mass, planet_radius)
                        simulation_started = True
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if temp_obj_pos:
                        obj = create_ship(temp_obj_pos, mouse_pos, ship_mass)
                        objects.append(obj)
                        temp_obj_pos = None
                    else:
                        temp_obj_pos = mouse_pos

        if not simulation_started:
            win.fill(BLACK)
            for box in input_boxes:
                box.update()
                box.draw(win)
            info_text = "Press Enter to start the simulation"
            info_surf = FONT.render(info_text, True, WHITE)
            win.blit(info_surf, (50, 200))
        else:
            win.blit(BG, (0, 0))

            if temp_obj_pos:
                pygame.draw.line(win, WHITE, temp_obj_pos, mouse_pos, 2)
                pygame.draw.circle(win, RED, temp_obj_pos, OBJ_SIZE)
            
            for obj in objects[:]:
                obj.draw()
                obj.move(planet)
                off_screen = obj.x < 0 or obj.x > WIDTH or obj.y < 0 or obj.y > HEIGHT
                collided = math.sqrt((obj.x - planet.x)**2 + (obj.y - planet.y)**2) <= planet.radius
                if off_screen or collided:
                    trails.append(obj.trail)
                    objects.remove(obj)

            for trail in trails:
                if len(trail) > 1:
                    pygame.draw.lines(win, WHITE, False, [(int(x), int(y)) for x, y in trail], 1)

            planet.draw()

            if objects:
                info_text = objects[0].get_info(planet)
                draw_info(info_text, WIDTH - 200, 10)

            user_defined_values = f"Planet Mass: {planet_mass}\nPlanet Radius: {planet_radius}\nShip Mass: {ship_mass}"
            draw_info(user_defined_values, WIDTH - 200, 80)

        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    main()
