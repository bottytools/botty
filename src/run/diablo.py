from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from dataclasses import dataclass
from utils.custom_mouse import mouse #for sealdance
from screen import Screen #for sealdance
import keyboard

class Diablo:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        pather: Pather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt
    ):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Diablo")
        if not self._char.can_teleport():
            raise ValueError("Diablo requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(4, 2) # use Halls of Pain Waypoint (3rd in A4)
        return Location.A4_DIABLO_WP

    def _river_of_flames(self):
        self._pather.traverse_nodes([600], self._char) # Calibrate postion at wp to ensure success for all river of flames layouts
        Logger.debug("Calibrated at WAYPOINT")
        self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
        Logger.info("Moving to CS ENTRANCE")
        found = False
        templates = ["DIABLO_CS_ENTRANCE_0", "DIABLO_CS_ENTRANCE_2", "DIABLO_CS_ENTRANCE_3"]
        while not found: # Looping in smaller teleport steps to make sure we find the entrance
            found = self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.1, take_ss=False).valid 
            if not found:
                self._pather.traverse_nodes_fixed("diablo_wp_entrance_loop", self._char)
        self._pather.traverse_nodes([601], self._char, threshold=0.8) # Calibrate at entrance to Chaos Sanctuary to ensure success reaching pentagram
        Logger.debug("Calibrated at CS ENTRANCE")

    def _cs_pentagram(self):
        self._pather.traverse_nodes_fixed("diablo_entrance_pentagram", self._char)
        Logger.info("Moving to PENTAGRAM")
        found = False
        templates = ["DIABLO_PENT_0", "DIABLO_PENT_1", "DIABLO_PENT_2", "DIABLO_PENT_3"]
        while not found:
            found = self._template_finder.search_and_wait(templates, threshold=0.82, time_out=0.1).valid
            if not found:
                self._pather.traverse_nodes_fixed("diablo_entrance_pentagram_loop", self._char) # Looping in smaller teleport steps to make sure we find the pentagram
        self._pather.traverse_nodes([602], self._char, threshold=0.82)
        Logger.info("Calibrated at PENTAGRAM")

    def _sealdance(self, seal_opentemplates, seal_closedtemplates, seal_layout, found): # we could add a variable for moveoment_found_close_by, if TRUE, we could call kill_cs_trash
        #KEY LEARNING: MAKE SURE THAT YOU APPROACH ALL SEALS FROM THE LEFT WHEN TRYING TO OPEN THEM!
        i = 0
        while i <=9 and not found: # Looping to click the seal while the open seal is not found
            #keyboard.send(self._skill_hotkeys["redemption"]) # cast redemption to clear template from corpses?
            pos_m = self._screen.convert_abs_to_monitor((0, 0)) #move the mouse away before checking the template
            mouse.move(*pos_m, randomize=[90, 160])
            mouse.click
            wait(0.3)
            found = self._template_finder.search_and_wait(seal_opentemplates, threshold=0.75, time_out=0.5, take_ss=False).valid 
            Logger.info(seal_layout + ": check if open - loop")
            i += 1
            if not found: 
                # do a little random hop & try to click the seal
                """x_m, y_m = self._screen.convert_abs_to_monitor(self._pos_abs)
                self._char.move((x_m -50, y_m -50), force_move=True) # this piece should be a random movement along X-axis - should we add someing like rand(0.2,-0.2) before x_m? We dont want to jump too far
                i = 0
                while True:
                direction = 1 if i % 2 == 0 else -1
                x_m, y_m = self._screen.convert_abs_to_monitor([40 * direction, 40 * direction])
                i += 1
                """
                self._char.select_by_template(seal_closedtemplates, threshold=0.5, time_out=0.5)
                wait(1)
                Logger.info(seal_layout + ": trying to open " + str(i) + " of 10 times")
            Logger.info(seal_layout + ": is open") # this message is also sent if the seal is closed and the sealdance starts again - however should only be sent if the seal is really open.


#    def _clearseal(self, seal_layout, seal_boss, hasfake, killtrash, nodes_approach, nodes_safe_dist, nodes_seal_fake, nodes_seal_boss, nodes_end):
#        Logger.info(seal_layout + " - seal layout found")           
#        self._pather.traverse_nodes_fixed("diablo_" + str(len(seal_layout) -= 2)) + "_approach", self._char) # safe_dist
#        self._pather.traverse_nodes(seal_layout), self._char) # calibrate safe_dist
#        if killtrash: self._char.kill_cs_trash(nodes_safe_dist) #Clear Trash A1Y safe-dist & loot
#            Logger.info(seal_layout + " - traversing to boss seal" )
#            self._pather.traverse_nodes(nodes_seal_boss), self._char) # at seal
#            if killtrash: # clear trash true?
#                Logger.info(seal_layout + " - killing trash at boss seal")
#                self._char.kill_cs_trash(nodes_seal_fake)
#                if loottrash: self._picked_up_items = self._pickit.pick_up_items(self._char)
#                self._pather.traverse_nodes(nodes_seal_boss, self._char) # here we have to take care, we only want to calibrate at the last node
#                seal_type = "BOSS"
#                sealdance(["DIA_" + seal_layout + "_" seal_type + "CLOSED", "DIA_" + seal_layout + "_" + seal_type + "MOUSEOVER"],["DIA_" + seal_layout + "_" + seal_type "ACTIVE"], seal_layout)
#        self._pather.traverse_nodes_fixed("diablo_" + str(len(seal_layout) -= 2)) + "_safe_dist", self._char) # safe_dist
#        kill_sealboss (seal_boss)
#        self._picked_up_items = self._pickit.pick_up_items(self._char)
#        self._pather.traverse_nodes(nodes_end, self._char) # Move to Pentagram
#        Logger.info("Calibrated at PENTAGRAM")        


# === LIST OF ISSUES ===
# SEALDANCE: 
#   - clicks whilst moving the mouse away when checking for ACTIVE seal
#   - add a failsave that after 2 failed tries to activate seal a kill_trashmobs sequence (for redemption) is launched
#   - hop away after you click on the seal to make room for the template check (or make template smaller)
#   - seals should ideally be activated from the left
#   - seal can activate from a slight distance, if we stand ON the seal after activating, the template check fails

# RIVER OF FLAME: 
#   - urdars sometimes stun, therefore 1 tele is skipped, and we get stuck in an infinite "diablo_wp_entrance_loop", never finding CS entrance

# VIZIER A1L: 
#   - stuck on upper seal check (seems a sealdance issue)
#   - vizier sometimes spawns below seal and does not move up to safe_dist for dying there in our hammerwave. Adapted attack sequence to move towards this place
#   - need more templates to calibrate after looting

# VIZIER A2Y: 
#   - template 622 does not work properly
#   - if you enter with too much flying trash, templates will not be recognized & pather gets stuck.

# DE SEIS B1U:
#   - at seal all hammers hit the wall, but position is important, otherwise the seal bugs

# DE SEIS B2F:
#   - too far at the wall during de seis attack sequence (hammering the wall)
#   - relate to above one: safe_dist not found when attack sequence too far left

# INFECTOR C2G:
#   - gets stuck after opening seal - the mobs are too big, masking the sealcheck graphic (maybe smaller graphic?)

# INFECTOR C1F:
#   - works well :) still, might add some templates to calibrate after looting
#   - therefore, trash loot is currently off
#   - fix postion 661 to get rid of _hopleft & _hopright static paths
#   - sometimes does not _hopright after sealclick to move to safe_dist (seems sealdance issue)

    def _seal_A2(self): # WORK IN PROGRESS - 622 seems bugged - also the naming of seals is mess dude!
        seal_layout = "A2Y"
        Logger.info("Seal Layout: " + seal_layout)
        self._pather.traverse_nodes_fixed("dia_a2y_approach", self._char) #bring us from layout check towards the place where we should see our nodes
        self._char.kill_cs_trash() #Clear Trash A1Y safe-dist & loot
        self._pather.traverse_nodes([621, 623], self._char) # Traverse to safe_dist
        self._char.kill_cs_trash() #Clear Trash A1Y safe-dist & loot
        #self._pather.traverse_nodes([626, 625], self._char) # Traverse to other seal
        #self._char.kill_cs_trash() #Clear Trash A1Y boss & loot
        self._pather.traverse_nodes([624], self._char) # Calibrate at upper seal 610
        self._sealdance(["DIA_A2Y_15_OPEN"], ["DIA_A2Y_14_CLOSED","DIA_A2Y_15_MOUSEOVER"], seal_layout + "-Seal1", False)
        self._pather.traverse_nodes([626], self._char) # Calibrate at upper seal 610
        self._sealdance(["DIA_A2Y_24_OPEN"], ["DIA_A2Y_24_CLOSED", "DIA_A2Y_23_MOUSEOVER"], seal_layout + "-Seal2", False)
        self._pather.traverse_nodes([625,621], self._char) # go to safe_dist to fight vizier
        Logger.info("Kill Vizier")
        self._char.kill_vizier() # we could also add seal_layout to the function for differentiating attack patterns.
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([621], self._char) # calibrate at SAFE_DIST after looting, before returning to pentagram
        Logger.info("Calibrated at " + seal_layout + " SAFE_DIST")
        self._pather.traverse_nodes_fixed("dia_a2y_home", self._char) #lets go home
        self._pather.traverse_nodes([602], self._char) # Move to Pentagram
        Logger.info("Calibrated at PENTAGRAM")

    def _seal_A1(self): # DONE
        seal_layout = "A1L"
        Logger.info("Seal Layout: " + seal_layout)           
        self._pather.traverse_nodes_fixed("diablo_a2_safe_dist", self._char) # safe_dist
        self._char.kill_cs_trash()
        self._pather.traverse_nodes([620], self._char) # Calibrate at upper seal 620
        self._sealdance(["DIA_A2L_7"], ["DIA_A2L_2", "DIA_A2L_3", "DIA_A2L_2_621", "DIA_A2L_2_620", "DIA_A2L_2_620_MOUSEOVER"], seal_layout + "1", False)
        self._pather.traverse_nodes([622, 623], self._char) # traverse to lower seal
        self._sealdance(["DIA_A2L_11"], ["DIA_A2L_0", "DIA_A2L_1"], seal_layout + "2", False)
        self._pather.traverse_nodes([622], self._char) # fight vizier at safe_dist -> the idea is to make the merc move away from vizier spawn. if there is a stray monster at the spawn, vizier will only come if this mob is cleared and our attack sequence might miss.
        Logger.info("Kill Vizier")
        self._char.kill_vizier()
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([622], self._char) # calibrate at SAFE_DIST after looting, before returning to pentagram
        Logger.info("Calibrated at " + seal_layout + " SAFE_DIST")
        self._pather.traverse_nodes_fixed("diablo_a2_end_pentagram", self._char) #lets go home
        self._pather.traverse_nodes([602], self._char) # Move to Pentagram
        Logger.info("Calibrated at PENTAGRAM")

    def _seal_B1(self): # DONE
        seal_layout = "B1S"
        Logger.info("Seal Layout: " + seal_layout)
        self._pather.traverse_nodes_fixed("diablo_pentagram_b1_seal", self._char) # to to seal
        self._char.kill_cs_trash() # at seal
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([632], self._char) #clear other side, too
        self._char.kill_cs_trash() # across gap - if they get fana on hell we are doomed
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([630], self._char) #back to seal      
        self._sealdance(["DIA_B1S_1_ACTIVE"], ["DIA_B1S_1", "DIA_B1S_0"], seal_layout, False) #pop
        self._pather.traverse_nodes([630], self._char) #633 is bugged
        self._pather.traverse_nodes_fixed("diablo_b1_safe_dist", self._char)
        Logger.info("Kill De Seis")
        self._char.kill_deseis()
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([632], self._char) # calibrate after looting
        Logger.info("Calibrated at " + seal_layout + " SAFE_DIST")
        self._pather.traverse_nodes_fixed("diablo_b1_end_pentagram", self._char) #lets go home
        self._pather.traverse_nodes([602], self._char) # Move to Pentagram
        Logger.info("Calibrated at PENTAGRAM")

    def _seal_B2(self): # WORK IN PROGRESS - THIS IS THE BROKEN SEAL, IT HAS TO BE ACTIVATED FROM THE TOP
        seal_layout = "B2U"
        Logger.info("Seal Layout: " + seal_layout)           
        self._pather.traverse_nodes([640, 641], self._char) #approach, safe dist
        self._char.kill_cs_trash() # at safe_dist
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([642, 643], self._char) #seal far seal close
        self._sealdance(["DIA_B2U_15_OPEN"], ["DIA_B2U_11_CLOSED", "DIA_B2U_10_MOUSEOVER"], seal_layout, False)
        self._pather.traverse_nodes([642, 641], self._char) #seal far, safe dist
        Logger.info("Kill De Seis")
        self._char.kill_deseis()
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([640], self._char) #approach
        self._pather.traverse_nodes_fixed("dia_b2u_home", self._char) 
        self._pather.traverse_nodes([602], self._char) # Move to Pentagram
        Logger.info("Calibrated at PENTAGRAM")

    def _seal_C2(self): # DONE - COULD RENAME SCREENSHOTS FROM DIABLO_ to DIA_, POS 651 sometimes sends us to the lava on the right until pather gets stuck and exits
        seal_layout = "C2G"
        Logger.info("Seal Layout: " + seal_layout)
        self._pather.traverse_nodes([660], self._char) # approach
        self._pather.traverse_nodes([661], self._char) # approach
        #self._char.kill_cs_trash()
        #self._picked_up_items = self._pickit.pick_up_items(self._char)
        #self._pather.traverse_nodes([661], self._char) # approach
        self._sealdance(["DIA_C2G_4_OPEN"], ["DIA_C2G_4_CLOSED", "DIA_C2G_5_MOUSEOVER"], seal_layout + "1", False)
        self._pather.traverse_nodes([662], self._char) # fight 651
        Logger.info("Kill Infector")
        self._char.kill_infector()
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([663], self._char) # pop seal 651, 
        self._sealdance(["DIA_C2G_13_OPEN"], ["DIA_C2G_13_CLOSED", "DIA_C2G_14_MOUSEOVER"], seal_layout + "2", False)
        self._pather.traverse_nodes([663], self._char) # calibrate at SAFE_DIST after looting, before returning to pentagram
        Logger.info("Calibrated at " + seal_layout + " SAFE_DIST")
        self._pather.traverse_nodes_fixed("dia_c2g_home", self._char)
        self._pather.traverse_nodes([602], self._char) # calibrate pentagram
        Logger.info("Calibrated at PENTAGRAM")

    def _seal_C1(self): # DONE
        seal_layout = "C1F"
        Logger.info("Seal Layout: " + seal_layout)
        self._pather.traverse_nodes_fixed("diablo_pentagram_c2_seal", self._char) # moving close to upper seal
        self._pather.traverse_nodes([660], self._char) # position between seals
        self._char.kill_cs_trash()
        self._sealdance(["DIA_C2F_FAKE_ACTIVE"], ["DIA_C2F_FAKE_MOUSEOVER", "DIA_C2F_FAKE_CLOSED"], seal_layout + "-Seal1", False)
        self._pather.traverse_nodes([660], self._char) # transition to boss seal
        self._pather.traverse_nodes_fixed("diablo_c2f_hopleft", self._char) # moving to lower seal - dirty solution with static path, as the 661 does not work well
        self._char.kill_cs_trash()
        #self._pather.traverse_nodes([661], self._char) # transition to boss seal # we sometimes get stuck here, might need more templates
        self._sealdance(["DIA_C2F_BOSS_ACTIVE"], ["DIA_C2F_BOSS_MOUSEOVER", "DIA_C2F_BOSS_CLOSED"], seal_layout + "-Seal1", False)
        self._pather.traverse_nodes_fixed("diablo_c2f_hopright", self._char) # move to fight position - dirty solution with static path, as the 661 does not work well
        Logger.info("Kill Infector") 
        self._char.kill_infector()
        self.picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([660], self._char) # transition to boss seal
        Logger.info("Calibrated at " + seal_layout + " SAFE_DIST")
        self._pather.traverse_nodes_fixed("diablo_c2_end_pentagram", self._char) #lets go home
        self._pather.traverse_nodes([602], self._char) # Move to Pentagram
        Logger.info("Calibrated at PENTAGRAM")

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if do_pre_buff:
            self._char.pre_buff()
        self._river_of_flames()
        self._cs_pentagram()
        # Seal A: Vizier (to the left)
        self._pather.traverse_nodes_fixed("dia_a_layout", self._char) # we check for layout of A (1=Y or 2=L) L lower seal pops boss, upper does not. Y upper seal pops boss, lower does not
        Logger.info("Checking Layout at A")
        if self._template_finder.search_and_wait(["DIABLO_A_LAYOUTCHECK0", "DIABLO_A_LAYOUTCHECK1", "DIABLO_A_LAYOUTCHECK2"], threshold=0.8, time_out=0.1).valid:
            self._seal_A2() 
        else:
            self._seal_A1() # stable, but sometimes vizier spawns below the boss seal and cannot be killed (he does not come to the fighting spot).
        # Seal B: De Seis (to the top)
        self._pather.traverse_nodes_fixed("dia_b_layout", self._char) # we check for layout of B (1=S or 2=U) - just one seal to pop.
        Logger.debug("Checking Layout at B")
        if self._template_finder.search_and_wait(["DIABLO_B_LAYOUTCHECK0", "DIABLO_B_LAYOUTCHECK1"], threshold=0.8, time_out=0.1).valid:
            self._seal_B1() #seal works stable, except de seis kill
        else:
            self._seal_B2()
        # Seal C: Infector (to the right)    
        self._pather.traverse_nodes_fixed("dia_c_layout", self._char)  # we check for layout of C (1=G or 2=F) G lower seal pops boss, upper does not. F first seal pops boss, second does not
        Logger.debug("Checking Layout at C")
        if self._template_finder.search_and_wait(["DIABLO_C_LAYOUTCHECK0", "DIABLO_C_LAYOUTCHECK1", "DIABLO_C_LAYOUTCHECK2"], threshold=0.8, time_out=0.1).valid:
            self._seal_C2() #stable
        else:
            self._seal_C1() # stable, but sometimes ranged mobs at top seal block the template check for open seal, botty then gets stuck 
        # Diablo
        Logger.debug("Waiting for Diablo to spawn") # we could add a check here, if we take damage: if yes, one of the sealbosses is still alive (otherwise all demons would have died when the last seal was popped)
        wait(9)
        self._char.kill_diablo() 
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A4_DIABLO_END, picked_up_items) #there is an error  ValueError: State 'diablo' is not a registered state.

"""
if __name__ == "__main__":
    from screen import Screen
    import keyboard
    from game_stats import GameStats
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    from bot import Bot
    config = Config()
    screen = Screen(config.general["monitor"])
    game_stats = GameStats()
    bot = Bot(screen, game_stats, False)
    # bot._diablo.battle(True)
    # bot._diablo._traverse_river_of_flames()
    # bot._diablo._cs_pentagram()
    bot._diablo._seal_a()
"""