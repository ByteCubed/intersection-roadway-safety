# import imp
import json
# from turtle import left
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
# import click
import stringcase
import pdb
import matplotlib.pyplot as plt
import PIL
import numpy as np

POSTGRES_DB= os.getenv('POSTGRES_DB')
POSTGRES_PASSWORD= os.getenv('POSTGRES_PASSWORD')
POSTGRES_USER= os.getenv('POSTGRES_USER')
HOST_NAME= os.getenv('HOSTNAME')
CURRENT_DIR= os.getcwd()


def count_legs_in_image_border(border_array):
    """Function to count the number of roads that go out from an intersection through a specific image border.
    The idea is that we can calculate the number of road legs that disperse through a specific intersection as the
    sum of all the image borders.
    """
    # Define a variable that is either dark or white (parity)
    pixel_parity = None
    # We are going to count the number of times the parity changes (twice indicates a single road)
    parity_changes = 0
    for pixel in border_array:
        
        current_parity = (pixel < 127)
        if pixel_parity == None:
            # is pixel dark or black
            pixel_parity = current_parity
            continue
        if pixel_parity != (current_parity):
            parity_changes+=1
            pixel_parity = current_parity
            
    return parity_changes/2


def calculate_total_num_legs(crop_size):

    # Connect to your postgres DB
    conn = psycopg2.connect(f"host={HOST_NAME} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD} port=5432")

    # Open a cursor to perform database operations
    cur = conn.cursor()

    cur.execute("select longitude, latitude, ST_AsText(point),nodehash,maskimage from planet_osm_intersections_alpha;")
    nodes = cur.fetchall()
    print(nodes)
    cur.execute("ALTER TABLE planet_osm_intersections_alpha ADD COLUMN IF NOT EXISTS num_legs_from_borderAlgo text ;")
    conn.commit()

    count = 0
    for node in nodes:
        # x = node[2].split("(")[1][:-1].split(" ")[0]
        # y = node[2].split("(")[1][:-1].split(" ")[1]
        try:
            image_path = node[4]
            image = PIL.Image.open(image_path)
            image_array = np.array(image)

            # We are going to draw a box centered at 126 with width 'crop_size'
            left_pixel_edge = int(126 - (crop_size/2))
            right_pixel_edge = int(126 + (crop_size/2))
            cropped_array = image_array[left_pixel_edge:right_pixel_edge][:,left_pixel_edge:right_pixel_edge]

            # Extract the R component of the border around the cropped image
            bottom_border = cropped_array[cropped_array.shape[0]-1,:][:,0]
            top_border = cropped_array[0,:][:,0]
            right_border = cropped_array[:,cropped_array.shape[0]-1][:,0]
            left_border = cropped_array[:,0][:,0]

            left_count = count_legs_in_image_border(left_border)
            right_count = count_legs_in_image_border(right_border)
            top_count = count_legs_in_image_border(top_border)
            bottom_count = count_legs_in_image_border(bottom_border)

            num_legs = left_count + right_count + top_count + bottom_count
            print(image_path)
            print("num legs = " + str(num_legs))
            cur.execute(f""" UPDATE planet_osm_intersections_alpha
                    SET num_legs_from_borderAlgo = {num_legs}
                    WHERE nodehash = '{node[3]}'""")

        except Exception as e:
            pass
            # print(e)

        # if count > 12000:
        #     break
        # else:
        #     count +=1

    conn.commit()
    return 0


def calculate_total_num_legs_with_default_size():
    calculate_total_num_legs(40)


if __name__ == "__main__":
    # The argument is the radius of the intersection
    calculate_total_num_legs_with_default_size()



 

