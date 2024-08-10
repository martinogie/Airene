# ABSTRACTION, AND ENCAPSULATON  - Pillars of OOP
class Enemy:
#     type_of_enemy: str = "Zombie"
#     health_points: int = 10
#     attack_damage = 1

    def __init__(self, type_of_enemy, health_points=10, attack_damage=1):    # parameter Constructor
        self.__type_of_enemy =  type_of_enemy  # double underscore to encapsulate object created
        self.health_points =  health_points
        self.attack_damage =  attack_damage
    
    def talk(self):
        print(f'I am a {self.__type_of_enemy}, be prepared to fight.')
        
    def walk_forward(self):
        print(f'{self.__type_of_enemy} moves closer to you.')
        
    def attack(self):
        print(f'{self.__type_of_enemy} attacks for {self.attack_damage} damage.')
        
    def get_type_of_enemy(self):
        return self.__type_of_enemy