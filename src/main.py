from __future__ import annotations
import asyncio
import pygame
from typing import Literal

## pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

## predraw setup
screen.fill("purple")
pygame.display.flip()

## Mouse class
class Mouse:
    pos: tuple[int, int] = (0, 0)

    @staticmethod
    def update() -> None:
        """Updates the mouse state. Call this once per frame."""
        Mouse.pos = pygame.mouse.get_pos()

    @staticmethod
    def move_to(x: int, y: int) -> None:
        """Moves the mouse to the specified position."""
        pygame.mouse.set_pos((x, y))
        Mouse.pos = (x, y)

    @staticmethod
    def button(button: int) -> bool:
        """Returns True if the specified mouse button is pressed."""
        return pygame.mouse.get_pressed()[button]

    @staticmethod
    def draw() -> None:
        """Draws the mouse cursor on the specified surface."""
        pygame.draw.circle(screen, "white", Mouse.pos, 5)


## Viewport class
class Viewport:
    rect = screen.get_rect()
    surface = pygame.Surface(rect.size)
    offset: tuple[int, int] = (100, 50)

    dragging = False
    drag_start: tuple[int, int] = (0, 0)
    offset_start: tuple[int, int] = (0, 0)

    @classmethod
    def world_to_screen(cls, x: int, y: int) -> tuple[int, int]:
        """Converts world coordinates to screen coordinates."""
        return (
            x + cls.offset[0],
            y + cls.offset[1]
        )

    @classmethod
    def screen_to_world(cls, x: int, y: int) -> tuple[int, int]:
        """Converts screen coordinates to world coordinates."""
        return (
            x - cls.offset[0],
            y - cls.offset[1]
        )

    @classmethod
    def update(cls) -> None:
        """Updates viewport dragging."""
        mouse_x, mouse_y = Mouse.pos

        if Mouse.button(2):
            if not cls.dragging:
                cls.dragging = True
                cls.drag_start = Mouse.pos
                cls.offset_start = cls.offset

            cls.offset = (
                cls.offset_start[0] + mouse_x - cls.drag_start[0],
                cls.offset_start[1] + mouse_y - cls.drag_start[1]
            )
        else:
            cls.dragging = False

    @classmethod
    def draw(cls) -> None:
        """Draws the viewport to the screen."""
        screen.blit(cls.surface, cls.rect.topleft)

    @classmethod
    def fill(cls, color: str | tuple[int, int, int]) -> None:
        """Fills the viewport surface."""
        cls.surface.fill(color)

## classes for game logic and display
class Game:

    class Lamp:
        SIZE: int = 18
        SPACING: int = 14
        CELL_SIZE: int = SIZE + SPACING

        OFF: Literal[0] = 0
        ON: Literal[1] = 1

        COLOR_OFF = (100, 80, 80)
        COLOR_ON = (80, 240, 240)
        COLOR_LINE = (255, 255, 255)

        @classmethod
        def color(cls, state: int) -> tuple[int, int, int]:
            """returns the appropriate color for a lamp with the given state"""
            match state:
                case cls.OFF: return cls.COLOR_OFF
                case cls.ON: return cls.COLOR_ON
                case _: return (255, 0, 0)  ## error color

        def __init__(self, ix: int, iy: int, state: int = 0):
            self.ix = ix  ## index x
            self.iy = iy  ## index y
            self.state = state

        def hovering(self) -> bool:
            """Returns True if the mouse is hovering over the lamp."""
            x, y = Viewport.world_to_screen(
                self.ix * Game.Lamp.CELL_SIZE,
                self.iy * Game.Lamp.CELL_SIZE
            )

            return (
                (Mouse.pos[0] - x) ** 2 +
                (Mouse.pos[1] - y) ** 2
            ) <= (Game.Lamp.SIZE // 2) ** 2
        
        def on_click(self) -> None:
            self.state = 1 - self.state

        def __str__(self) -> str: return f"Lamp<ix={self.ix},iy={self.iy},state={self.state}>"


    class Lampgrid:
        def __init__(self, width: int, height: int):
            self.width = width
            self.height = height
            self.lamps = [[Game.Lamp(ix, iy) for ix in range(width)] for iy in range(height)]
            self.world_width = (width - 1) * Game.Lamp.CELL_SIZE  ## ensure updates to this when width changes
            self.world_height = (height - 1) * Game.Lamp.CELL_SIZE  ## ensure updates to this when width changes

        def __iter__(self):
            for row in self.lamps:
                for lamp in row: yield lamp
        
        def __getitem__(self, index: int) -> list[Game.Lamp]:
            return self.lamps[index]
        
        def set_lamp_state(self, ix: int, iy: int, state: int):
            self.lamps[iy][ix] = state
        
        def get_lamp_state(self, ix: int, iy: int) -> int:
            return self.lamps[iy][ix].state

        def draw_to_port(self) -> None:
            """Draws every lamp to the viewport with the current camera offset."""
            ## draw connector lines
            for yi in range(self.height): 
                yf = yi * Game.Lamp.CELL_SIZE
                pygame.draw.line(
                    Viewport.surface,
                    Game.Lamp.COLOR_LINE,
                    Viewport.world_to_screen(0, yf),
                    Viewport.world_to_screen(self.world_width, yf)
                )
            for xi in range(self.width):
                xf = xi * Game.Lamp.CELL_SIZE
                pygame.draw.line(
                    Viewport.surface,
                    Game.Lamp.COLOR_LINE,
                    Viewport.world_to_screen(xf, 0),
                    Viewport.world_to_screen(xf, self.world_height)
                )
            ## draw the lamps themselves
            for row in self.lamps:
                for lamp in row:
                    x, y = Viewport.world_to_screen(
                        lamp.ix * Game.Lamp.CELL_SIZE,
                        lamp.iy * Game.Lamp.CELL_SIZE
                    )
                    pygame.draw.circle(
                        Viewport.surface,
                        "white",
                        (x - Viewport.rect.x, y - Viewport.rect.y),
                        Game.Lamp.SIZE // 2
                    )
                    pygame.draw.circle(
                        Viewport.surface,
                        Game.Lamp.COLOR_ON if lamp.state == Game.Lamp.ON else "gray",
                        (x - Viewport.rect.x, y - Viewport.rect.y),
                        Game.Lamp.SIZE // 2 - 1
                    )

## global scope for pygbag compiler
lampgrid = Game.Lampgrid(0, 0)


## definitely not overcomplicated keypress handler
def on_keypress(key: int) -> None:
    print(f'[{pygame.key.name(key)}] was pressed')

## definitely not overcomplicated mousepress handler
def on_mousepress(button: int) -> None:
    if button == 1:
        for lamp in lampgrid:
            if lamp.hovering():
                print("clicked a " + str(lamp))
                lamp.on_click()

## good 'ol ~~async~~ main()
async def main():
    global lampgrid
    
    ## testing purposes
    lampgrid = Game.Lampgrid(20, 20)

    while True:
        ## poll for events
        Mouse.update()

        ## event iterater
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN: on_keypress(event.key)
            if event.type == pygame.MOUSEBUTTONDOWN: on_mousepress(event.button)

        ## Per-Frame Updates
        Viewport.update()

        ## Per-Frame Renders
        screen.fill((150, 0, 150))

        Viewport.fill((30, 30, 30))
        lampgrid.draw_to_port()

        Viewport.draw()

        Mouse.draw()

        ## update the full display every frame for ease of use
        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())