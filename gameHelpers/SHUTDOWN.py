import pygame

def fullShutdown(mapGen = None):
    try:
        if mapGen is not None:
            mapGen.shutdown()
            mapGen = None
    except Exception as e:
        print("shutdown error:", e)
    pygame.quit()
    raise SystemExit