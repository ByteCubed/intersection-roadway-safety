import prepare_osm_graph
import prepare_osm_intersections
import prepare_intersection_masks
import load_intersections
import calculate_total_num_legs
import time
import os
import stringcase
import click


@click.command()
@click.argument('area_name')
@click.argument('json_name')
@click.argument('num_intersection_masks')
def main(area_name, json_name, num_intersection_masks):
    prepare_osm_graph.get_osm_graph(area_name)
    prepare_osm_intersections.ingest_intersections(area_name)
    prepare_intersection_masks.download_intersection_masks(json_name, area_name, str(num_intersection_masks))
    # Makes sure the previous procedure has successfully created the necessary directories. Maybe unneeded?
    while not os.path.isdir(f'{os.getcwd()}/data/{stringcase.alphanumcase(area_name)}_masks'):
        print(f'Waiting for {os.getcwd()}/data/{stringcase.alphanumcase(area_name)}_masks to exist.', flush=True)
        time.sleep(5)
    load_intersections.load_intersections(json_name, area_name)
    calculate_total_num_legs.calculate_total_num_legs_with_default_size()


if __name__ == "__main__":
    main()
