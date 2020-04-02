from abc import ABC, abstractmethod
import pygame
import random
import Service

def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


class Interactive(ABC):

    @abstractmethod
    def interact(self, engine, hero):
        pass

class AbstractObject(ABC):

    def __init__(self):
        pass
    def draw(self, display):
        min_x, min_y = 0, 0 
        min_x, min_y = display.calculate(min_x, min_y)
        display.blit(self.sprite, ((self.position[0] - min_x) * display.game_engine.sprite_size,
                                   (self.position[1] - min_y) * display.game_engine.sprite_size))


class Ally(AbstractObject, Interactive):

    def __init__(self, icon, action, position):
        self.sprite = icon
        self.action = action
        self.position = position

    def interact(self, engine, hero):
        self.action(engine, hero)



class Creature(AbstractObject):

    def __init__(self, icon, stats, position):
        self.sprite = icon
        self.stats = stats
        self.position = position
        self.calc_max_HP()
        self.hp = self.max_hp

    def calc_max_HP(self):
        self.max_hp = 5 + self.stats["endurance"] * 2


class Enemy(Creature, Interactive):
    
    def __init__(self, icon, stats, xp, position):
        self.xp = xp
        super().__init__(icon, stats, position)

    def interact(self, engine, hero):
        hero.exp += self.stats["experience"] // 3
        hero.level_up()
        damage = ((self.stats["strength"] // 5) * (self.stats["endurance"] // 10)) + (self.stats["intelligence"] // 3)
        chance = random.randint(0, 100 - hero.stats["luck"])
        hero.hp -=  damage if chance > 0 else 0
        
        if hero.hp <= 0:
            engine.level -= 1 
            hero.hp = hero.max_hp
            Service.reload_game(engine,hero)
        
 

class Hero(Creature):

    def __init__(self, stats, icon):
        pos = [1, 1]
        self.level = 1
        self.exp = 0
        self.gold = 0
        super().__init__(icon, stats, pos)

    def level_up(self):
        while self.exp >= (100 * (2 ** (self.level - 1))):
         #   yield "level up!"
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.calc_max_HP()
            self.hp = self.max_hp


class Effect(Hero):

    def __init__(self, base):
        self.base = base
        self.stats = self.base.stats.copy()
        self.apply_effect()

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @abstractmethod
    def apply_effect(self):
        pass

class Berserk(Effect):
    def apply_effect(self):
        self.stats["endurance"] += 3
        self.stats["strength"] += 3
        self.stats["luck"] += 3
        self.hp += 6

class Blessing(Effect):
    def apply_effect(self):
        self.stats["luck"] += 4
        self.hp += 4
        self.stats["intelligence"] += 2

class Weakness(Effect):
    def apply_effect(self):
        self.stats["intelligence"] -= 3
        self.stats["luck"] -= 4
        self.hp -= 1

class Poison(Effect):
    def apply_effect(self):
        self.stats["endurance"] -= 2
        self.stats["strength"] -= 2
        self.stats["luck"] -= 2
        self.hp -= 2

