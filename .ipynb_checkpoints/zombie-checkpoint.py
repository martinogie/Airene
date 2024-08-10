# INHERITANCE

from enemy import *


class Zombie(Enemy):
    def __init__(self, health_points, attack_damage):
        super().__init__(type_of_enemy='Zombie', health_points=health_points, attack_damage=attack_damage)
        
    def talk(self):
        print('***Grimbling***')              # METHOD OVERRIDING - overrides the default talk method in Enemy class
              
    def spread_disease(self):
        print('The Zombie is trying to spread infection')  # NEW METHOD NOT IN PARENT CLASSS -ZOMBIE ONLY
              