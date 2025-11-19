class Fish(pygame.sprite.Sprite):
    fish_types = {
        # fishtype: (swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname)
        'salmon': (2, 1, 0.4, 1, 5, 'salmon'),
        'fish': (3, 3, 0.6, 1, 5, 'fish'),
        'carp': (3, 2, 1, 1, 5, 'carp'),
    }

    fish_lists = {} # the only comprehensive list of fish.
    for fish in fish_types.keys():
        fish_lists[fish] = pygame.sprite.Group()

    fish_caught = False # checks if a fish is circling the hook when gravity is added remove this
    fish_took = False # keeps track of if a fish is on the hook

    fish_frames = { # add vector based rotations for fish movemont
            '[0, -1]': load_asset('fishup1.png', 'fish scheiße'),
            '[0, 1]': load_asset('fishdown1.png','fish scheiße' ),
            '[-1, 0]': load_asset('fishleft1.png','fish scheiße' ),
            '[1, 0]': load_asset('fishright1.png', 'fish scheiße' ),
            'spc': load_asset('collide.png', 'fish scheiße' ),
            '1': load_asset('fishcircle1.png', 'fish scheiße' ),
            '2': load_asset('fishcircle2.png', 'fish scheiße' ),
            '3': load_asset('fishcircle3.png', 'fish scheiße' ),
            '4': load_asset('fishcircle4.png', 'fish scheiße' ),
        }

    @classmethod
    def rescale(cls):
        """Rescales fish images to current resolution"""
        for key, value in cls.fish_frames.items():
            cls.fish_frames[key] = pygame.transform.scale(value, (16*map_mod.scale, 16*map_mod.scale))
            for species_list in cls.fish_lists.values(): # 16 represents base side lengths
                for fish in species_list:
                    fish.rect = fish.image.get_rect()
                    fish.rect.height = 16 * map_mod.scale
                    fish.rect.width = 16 * map_mod.scale

    @classmethod
    def create_fish(cls, cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item):
        """creates a new fish instance in the fish_list sprite group"""
        new = Fish(cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item)
        cls.fish_lists[item].add(new)
        spritelist.add(new)
        return new

    @classmethod
    def update_fish(cls):
        """updates each fishes center and returns any hook collisions if applicable"""
        for species_list in cls.fish_lists.values():
            for fish in species_list:
                fish.center = (fish.cords[0]-8, fish.cords[1]-8) # updates center
                if player.hook_cords and not cls.fish_caught:
                    # check for hook collisions
                    fish.rect.topleft = fish.cords # updates the fishes hit-boxes. This only happens when a hook is cast to save resources
                    if fish.rect.collidepoint(player.hook_cords[0], player.hook_cords[1]) and not fish.ignore:
                        cls.fish_caught = fish # returns a class instance if there is a collision
                elif cls.fish_caught:
                    return cls.fish_caught
            # else: cls.fish_caught = False (Seemed to not be needed)
        return False # returns false if no fish is colliding

    @classmethod
    def fish_moving(cls):
        """Handles predictable fish movements"""
        for species_list in cls.fish_lists.values():
            if timer%10 == 0: # handles expensive operations such as swerving and baiting.
                for fish in species_list:
                    if not fish.baited() and timer%60 and fish != cls.fish_caught:
                        # every second active fishes get a chance to swerve
                        fish.fish_swerve()
                    elif fish == cls.fish_caught and not cls.fish_took:
                        # handles deciding when a circling fish grabs onto the hook
                        x = random.randrange(-300, 10)
                        if x > 0:
                            cls.fish_took = fish
                            inventory.inventory.use_bait() # the fish ate the bait
                    elif fish == cls.fish_caught and cls.fish_took:
                        # handles deciding when a fish which grabbed onto the hook will run away
                        y = random.randrange(-490, 15)
                        if y > 0 and game_state != 'minigame':
                            player.hook_cords = False
                            cls.fish_took = False
                            cls.fish_caught = False
            for fish in species_list:
                # moves fish along their current trajectory. This is not a super expensive operation so it is handled every tick.
                if fish != cls.fish_caught:
                    fish.fish_move()

    def __init__(self, cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item):
        super().__init__()
        self.image = load_asset('fishleft1.png','fish scheiße') # change later to relate to a dict that matches fish type to image
        self.rect = self.image.get_rect() # creates rect for sprite class
        self.cords = (cords[0], cords[1]) #topleft cords of the fish
        self.center = (self.cords[0]-8, self.cords[1]-8) #central fish cords
        self.speed = f_speed*map_mod.scale
        self.swerving = swerving # measure of how unpredictable the fish is when it turns
        self.un_decisiveness = un_decisiveness # measure of how often a fish turns
        self.vector = [1, 0]
        self.id = f_id
        self.box = self.rect.center = self.center[0]+self.vector[0]*16*map_mod.scale, self.center[1]+self.vector[1]*16*map_mod.scale
        self.circ_frame = 1
        self.ignore = 4
        self.cautiousness = cautiousness
        self.item = inventory.Item.new(item)
        self.side_length = 16

    def __str__(self):
        return self.cords

    def __repr__(self):
        return F'ID:{self.id}, cords:{self.cords}, vector:{self.vector}'

    def draw(self):
        if Fish.fish_caught == self and player.hook_cords:  # draws the fish circling the hook and handles frame logic
            if game_state == 'minigame':
                win.blit(Fish.fish_frames[str(self.vector)],
                         (player.hook_cords[0] - xp - 6 * map_mod.scale, player.hook_cords[1] - yp - 6 * map_mod.scale))
            else:
                win.blit(Fish.fish_frames[str(self.circ_frame)],
                         (player.hook_cords[0] - xp - 6 * map_mod.scale, player.hook_cords[1] - yp - 6 * map_mod.scale))
                if timer % 12 == 0:
                    self.circ_frame = (self.circ_frame % 4 + 1)
            if Fish.fish_took:
                win.blit(Fish.fish_frames['spc'], (
                    player.hook_cords[0] - xp - 6 * map_mod.scale, player.hook_cords[1] - yp - 6 * map_mod.scale))
        else:
            win.blit(Fish.fish_frames[str(self.vector)],
                     (self.cords[0] - xp, self.cords[1] - yp))  # should be changed to a rotation based on vector


    def fish_swerve(self): # replace with gravity
        """Makes the fish instance change direction based on swerving and un_decisiveness instance properties"""
        new_vector = self.vector
        ranlist = (-1, 1)
        x = random.randrange(-10, self.un_decisiveness)
        if 0 < x:
            new_vector.reverse()
            if new_vector[0] == 0:
                new_vector[1] = ranlist[random.randrange(-1, 1)]
                new_vector[0] = 0
            else:
                new_vector[0] = ranlist[random.randrange(-1, 1)]
                new_vector[1] = 0
            self.vector = new_vector


    def fish_move(self):
        """Makes the fish instance move based on speed and direction instance properties"""
        x = self.cords[0]
        y = self.cords[1]
        new_vector = self.vector
        ranlist = (-1, 1)
        escape = 1
        while True:
            if 'f' == grid_ahead((x+self.vector[0]*self.speed+(10*self.vector[0]*map_mod.scale), y+self.vector[1]*self.speed+(10*self.vector[1]*map_mod.scale)), 16*map_mod.scale, 16*map_mod.scale)[-1]: # plus 20 is to keep the fish off of the sand
                self.cords = x + self.vector[0]*self.speed, y + self.vector[1]*self.speed
                return
            else:
                if 0 in self.vector: # potentially keepable with a little variation for gravity
                    new_vector.reverse()
                    if new_vector[0] == 0:
                        new_vector[1] = ranlist[random.randrange(-1, 1)]
                        new_vector[0] = 0
                    else:
                        new_vector[0] = ranlist[random.randrange(-1, 1)]
                        new_vector[1] = 0
                self.vector = new_vector
            escape += 1
            if escape == 10:
                logging.warning('fish may be trapped')
                break



    def baited(self): # sadly has to be probably changed a bit
        if self.ignore > 0:
            self.ignore -= 1
        elif player.hook_cords:
            dif = abs(player.hook_cords[0] - self.cords[0]) + abs(player.hook_cords[1] - self.cords[1])
            if dif > player.baitlevel * 3 + 64*map_mod.scale:
                return False
            ret = fun_box_check(self.cords, self.vector, True, True, 16*map_mod.scale, 16*map_mod.scale, player.baitlevel/3, player.baitlevel/3)
            if ret:
                self.vector = ret
                return True
            ret = fun_box_check(self.cords, self.vector, True, False, 16*map_mod.scale, 16*map_mod.scale, player.baitlevel/3, player.baitlevel/3)
            if ret:
                self.vector = ret
                return True
            ret = fun_box_check(self.cords, self.vector, False, False, 16*map_mod.scale, 16*map_mod.scale, player.baitlevel, player.baitlevel)
            if ret:
                self.vector = ret
                return True
        return False

    @classmethod
    def scared_check(cls):
        """scares fishes away from the hook when first cast"""
        check_radius = 60*map_mod.scale
        if player.hook_cords:
            for species_list in cls.fish_lists.values():
                for fish in species_list:
                    difx, dify = abs(player.hook_cords[0] - fish.cords[0]), abs(player.hook_cords[1] - fish.cords[1])
                    expx, expy = abs(player.hook_cords[0] - fish.cords[0]+fish.vector[0]), abs(player.hook_cords[1] - fish.cords[1]+fish.vector[1])
                    dif = math.sqrt(difx*difx+dify*dify) # checks absolute distance between fish and your hook
                    e_dif = math.sqrt(expx * expx + expy * expy) # checks if you are moving away or towards the hook
                    if dif <= check_radius and dif < e_dif: # if within a circle within radius 64 and the fish is moving towards you turn it around
                        fish.vector.reverse()
                        fish.ignore = 50 # makes the fish not be tricked by the bait for 500 ticks
