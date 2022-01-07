import os
from dotenv import load_dotenv
from dot.mapbox import satellite

load_dotenv()

if __name__ == "__main__":
    print(os.getenv('MAPBOX_TOKEN'))
    satellite.get_tile(38.9757, -76.9944, token=os.getenv('MAPBOX_TOKEN'))
    print('done')
