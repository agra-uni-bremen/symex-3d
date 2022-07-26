CUBE_SIZE = 1
BASE_SIZE = 1
TEXT_SCALE = CUBE_SIZE * 1.0
TEXT_HEIGHT = 0
BLOCK_Z = -6

FRAME_STEP = 4

INSTRUCTION_DISTANCE = CUBE_SIZE * 0.3
RUN_DISTANCE = CUBE_SIZE * 10
CAM_DISTANCE = max(50,min(50,RUN_DISTANCE*4)) #TODO add contraint with num runs
DEPTH_MULT = CUBE_SIZE

GROUND_MAT_WAS_CREATED = False #probably not necessary anymore

MAX_STEPS_TO_GENERATE = 5000 #don't create all steps for very large traces

Y_DIST = 180

COLOR_SPECIAL = (1,1,1,1) #white
COLOR_DESTROY = (0.574076,0,0,1) #red
COLOR_UPDATE = (0,0.037152,0.238367,1) #blue
COLOR_CREATE = (0,0.752314,0.310315,1) #green
COLOR_OVERWRITE = (1,0.28362,0,1) #orange

COLOR_ACTIVE = (0,1,0,1)

COLOR_JUMP_MAIN = (1.0,0.5,0,1)
COLOR_JUMP_SUB = (0,0,0,1)

COLOR_ARITH_MAIN = (0.131212,0.147999,0.256819,1)
COLOR_ARITH_SUB = (0.546881,0.827585,0.952702,1)


COLOR_TEXT = (0.1,0.1,1,1)