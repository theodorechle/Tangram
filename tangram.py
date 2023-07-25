import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from shapely.geometry import Polygon, Point
from shapely.affinity import rotate, scale
from os import listdir, mkdir

UTILS_DIR = "utils"
IMAGE_DIR = "images"
FPS = 60
CASE_SIZE = 10
SCREEN_SIZE = 1500, 1000
LIST_LENGTH = 300
SCREENSHOT_PLACE_SIZE = 100
ROTATION_ANGLE = 15
COLORS = {
    "screen": "#eeeeee",
    "lines": "#000000",
    "shape": "#000000",
    "grid": "#0000cc",
}

if IMAGE_DIR not in listdir():
    mkdir(IMAGE_DIR)


def rotate_shape(polygon, angle):
    return [list(i) for i in rotate(Polygon(polygon), angle).exterior.coords]
    
def mirror_shape(polygon):
    return [list(i) for i in scale(Polygon(polygon), yfact=-1, origin=(1, 0)).exterior.coords]
    

def draw_all(clicked, shapes_taken, relative_mouse_pos):
    # vertical line of the list
    pygame.draw.line(screen, COLORS["lines"], (LIST_LENGTH, 0), (LIST_LENGTH, SCREEN_SIZE[1]), 5)
    pygame.draw.line(screen, COLORS["lines"], (LIST_LENGTH, SCREENSHOT_PLACE_SIZE-5), (SCREEN_SIZE[0], SCREENSHOT_PLACE_SIZE-5), 5)

    if grid: #draw the grid
        for x in range(0, SCREEN_SIZE[0], CASE_SIZE):
            pygame.draw.line(screen, COLORS["grid"], (x, 0), (x, SCREEN_SIZE[1]))
        for y in range(0, SCREEN_SIZE[1], CASE_SIZE):
            pygame.draw.line(screen, COLORS["grid"], (0, y), (SCREEN_SIZE[0], y))

    if clicked:
        pos = pygame.mouse.get_pos()

    # draw each shape
    for index_, choosed_shape in enumerate(shapes):
        pygame.draw.polygon(screen, COLORS["shape"], choosed_shape, edge)
        if clicked: # check which shape is potentially clicked
            if Polygon(choosed_shape).contains(Point(pos)):
                shapes_taken = index_
                relative_mouse_pos = pos[0] - choosed_shape[0][0], pos[1] - choosed_shape[0][1]
                clicked = False

    return shapes_taken, relative_mouse_pos

shapes = [
    [[5, 5], [285, 5], [145, 145]],
    [[5, 180], [285, 180], [145, 320]],
    [[0, 360], [140, 360], [140, 500]],
    [[0, 540], [140, 540], [70, 610]],
    [[0, 630], [140, 630], [70, 700]],
    [[0, 800], [70, 730], [140, 800], [70, 870]],
    [[0, 890], [140, 890], [210, 960], [70, 960]]
    ]


grid = False
shapes_taken = None
relative_mouse_pos = None
writing = False
edge = False


pygame.init()

tangram_image = pygame.image.load(f"{UTILS_DIR}/tangram.png")

pygame.display.set_caption("Tangram")
pygame.display.set_icon(tangram_image)

screen = pygame.display.set_mode(SCREEN_SIZE)

manager = pygame_gui.UIManager(SCREEN_SIZE, f"{UTILS_DIR}/theme.json")

file_name = pygame_gui.elements.UITextEntryBox(pygame.Rect(LIST_LENGTH + 10, 5, SCREEN_SIZE[0] - LIST_LENGTH - 15, 40), "tangram", manager)
screenshot_button = pygame_gui.elements.UIButton((LIST_LENGTH // 2 + SCREEN_SIZE[0] // 2 - 70, 50), "Capture d'écran", manager)
toggle_visibility = pygame_gui.elements.UIButton((LIST_LENGTH + 700, 50), "Montrer/Cacher les contours (E)", manager)
error = pygame_gui.elements.UILabel(pygame.Rect(LIST_LENGTH + 5, 40, 400, 50), "", manager, object_id=ObjectID(object_id="#error"))
pygame_gui.elements.UILabel(pygame.Rect(LIST_LENGTH + 890, 40, 400, 50), "R/T : Tourner, M: Miroir, G : Grille", manager, object_id=ObjectID(object_id="#keys"))

pygame.key.set_repeat(200, 200)

clock = pygame.time.Clock()

run = True
while run:
    actual_fps = clock.tick(FPS)
    screen.fill(COLORS["screen"])
    clicked = False
    capture = False
    for event in pygame.event.get():
        time_delta = actual_fps / 1000.0
        manager.process_events(event)
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
            writing = file_name.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if shapes_taken != None:
                choosed_shape = shapes[shapes_taken]
                first_dot = choosed_shape[0] = choosed_shape[0]
                pos_change = first_dot[0] - round(first_dot[0]/CASE_SIZE) * CASE_SIZE, first_dot[1] - round(first_dot[1]/CASE_SIZE) * CASE_SIZE
                for dot in choosed_shape:
                    dot[0] -= pos_change[0]
                    dot[1] -= pos_change[1]

            shapes_taken = None

        elif event.type == pygame.KEYDOWN:
            if not writing:
                if event.key == pygame.K_ESCAPE:
                    run = False
                elif event.key == pygame.K_t:
                    if shapes_taken != None:
                        shapes[shapes_taken] = rotate_shape(shapes[shapes_taken], ROTATION_ANGLE)
                elif event.key == pygame.K_r:
                    if shapes_taken != None:
                        shapes[shapes_taken] = rotate_shape(shapes[shapes_taken], -ROTATION_ANGLE)
                elif event.key == pygame.K_m:
                    if shapes_taken != None:
                        shapes[shapes_taken] = mirror_shape(shapes[shapes_taken])
                elif event.key == pygame.K_g:
                    grid = not grid
                elif event.key == pygame.K_e:
                    edge = not edge
    
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == screenshot_button:
                name = f'{file_name.get_text()}.jpg'
                if name in listdir(IMAGE_DIR):
                    error.set_text("Un fichier porte déjà ce nom.")
                else:
                    name = f'{IMAGE_DIR}/{name}'
                    error.set_text("")
                    capture = True
            elif event.ui_element == toggle_visibility:
                edge = not edge

    if shapes_taken != None:
        mouse_pos = pygame.mouse.get_pos()

        first_dot = shapes[shapes_taken][0]
        dot_minus_mouse_pos = mouse_pos[0] - first_dot[0], mouse_pos[1] - first_dot[1]
        pos_change = dot_minus_mouse_pos[0] - relative_mouse_pos[0], dot_minus_mouse_pos[1] - relative_mouse_pos[1]
        for dot in shapes[shapes_taken]:
            dot[0] += pos_change[0]
            dot[1] += pos_change[1]

    if capture:
        temp_grid = grid
        grid = False

    shapes_taken, relative_mouse_pos = draw_all(clicked, shapes_taken, relative_mouse_pos)
    manager.update(time_delta)
    manager.draw_ui(screen)
    
    pygame.display.update()

    if capture:
        rect = pygame.Rect(LIST_LENGTH+5, 100, SCREEN_SIZE[0]-LIST_LENGTH-5, SCREEN_SIZE[1]-100)
        sub = screen.subsurface(rect)
        pygame.image.save(sub, name)
        grid = temp_grid
        screen.fill(COLORS["screen"])
        pygame.display.update()

pygame.quit()
