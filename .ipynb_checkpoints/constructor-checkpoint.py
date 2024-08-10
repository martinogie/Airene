class Enemy:
    
    def __init__(self):    # Default/Empty Constructor
        pass
    
    def __init__(self):    # No argument Constructor
        print('New enemy created with no starting values')
        
    def __init__(self, type_of_enemy, health_points=10, attack_damage=1):    # parameter Constructor
        self.type_of_enemy =  type_of_enemy
        self.health_points =  health_points
        self.attack_damage =  attack_damage
        
    