import numpy as np
from numba import njit
import math, time

WORLD_SEED = np.int64(-4172144997902289642) # 2B2T seed

np.seterr(over="ignore")
MULTIPLIER = np.int64(25214903917)
ADDEND = np.int64(11);
MASK = np.int64(math.pow(2, 48)) - 1

@njit(fastmath=True)
def process_cood(seed):
	for _ in range(5000):
		for x in range(-23440, 23441):
			externalSeed = np.int64(seed ^ MULTIPLIER)
			z = ((externalSeed - WORLD_SEED - 10387319 - x * np.int64(341873128712)) * np.int64(211541297333629)) << 16 >> 16
			if -23440 <= z <= 23440:
				return x, z
		seed = (seed * np.int64(246154705703781) + np.int64(107048004364969)) & MASK
	return None, None

def crack_item_drop_coordinate(drop_x, drop_y, drop_z):
	spawn_x = ((drop_x - math.floor(drop_x) - 0.25) * 2)
	spawn_y = ((drop_y - math.floor(drop_y) - 0.25) * 2)
	spawn_z = ((drop_z - math.floor(drop_z) - 0.25) * 2)

	if spawn_x <= 0 or spawn_x >= 1 or spawn_y <= 0 or spawn_y >= 1 or spawn_z <= 0 or spawn_z >= 1:
		print("Skipping this item because its coordinates are out of bounds. This probably means that the item only coincidentally looked like an item that was dropped from mining a block. Other ways to drop items (e.g. dropping from a player's inventory) can sometimes cause false positives like this.")
		return

	measurement1 = int(spawn_x * (1 << 24))
	measurement2 = int(spawn_y * (1 << 24))
	measurement3 = int(spawn_z * (1 << 24))

	cube_center_x = (measurement1 << 24) + np.int64(8388608)
	cube_center_y = (measurement2 << 24) + np.int64(8388597)
	cube_center_z = (measurement3 << 24) - np.int64(277355554490)
	
	basis_coeff0 = 9.555378710501827e-11 * cube_center_x - 2.5481838861196593e-10 * cube_center_y + 1.184083942007419e-10 * cube_center_z
	basis_coeff1 = -1.2602185961441137e-10 * cube_center_x + 6.980727107475104e-11 * cube_center_y + 1.5362999761237006e-10 * cube_center_z
	basis_coeff2 = -1.5485213111787743e-10 * cube_center_x - 1.2997958265259513e-10 * cube_center_y - 5.6285642813236336e-11 * cube_center_z

	seed = round(basis_coeff0) * np.int64(1270789291) + round(basis_coeff1) * np.int64(-2355713969) + round(basis_coeff2) * np.int64(-3756485696) & MASK
	next_seed = seed * MULTIPLIER + ADDEND & MASK
	next_next_seed = next_seed * MULTIPLIER + ADDEND & MASK

	if (seed >> 24 ^ measurement1 | next_seed >> 24 ^ measurement2 | next_next_seed >> 24 ^ measurement3) != 0:
		print("Failed to crack the seed. This probably means that the item only coincidentally looked like an item that was dropped from mining a block. Other ways to drop items (e.g. dropping from a player's inventory) can sometimes cause false positives like this.")
		return

	orig_seed = seed
	coord_x, coord_z = process_cood(seed)
	if(coord_x != None and coord_z != None):
		print(f"Item drop appeared at {drop_x} {drop_y} {drop_z}")
		print(f"RNG measurements are therefore {measurement1} {measurement2} {measurement3}")
		print(f"This indicates the java.util.Random internal seed must have been {orig_seed}")
		print(f"Found a woodland match at woodland region {coord_x} {coord_z} which would have set the seed to {seed}")
		print(f"Located someone between {coord_x * 1280 - 128}, {coord_z * 1280 - 128} and {coord_x * 1280 + 1151}, {coord_z * 1280 + 1151}")
	else:
		print("Failed to crack. This probably means that your world seed is incorrect, or there were no chunk loads recently.")

if __name__ == "__main__":
	time_start = time.perf_counter()
	crack_item_drop_coordinate(0.41882818937301636, 0.6833633482456207, 0.46088552474975586)
	time_duration = time.perf_counter() - time_start
	print(f'Took {time_duration:.3f} seconds')