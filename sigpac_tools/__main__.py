import argparse
import structlog

logger = structlog.get_logger()


def get_parser():
    parser = argparse.ArgumentParser(description="SIGPAC Tools")

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")
    subparsers.required = True

    # # Search command

    # search_parser = subparsers.add_parser(
    #     "search", help="Search for a reference in the SIGPAC database"
    # )
    # search_parser.add_argument(
    #     "--community",
    #     type=int,
    #     help="Community of the location",
    #     required=False,
    #     metavar="INT",
    # )
    # search_parser.add_argument(
    #     "--province",
    #     type=int,
    #     help="Province of the location",
    #     required=False,
    #     metavar="INT",
    # )
    # search_parser.add_argument(
    #     "--municipality",
    #     type=int,
    #     help="Municipality of the location",
    #     required=False,
    #     metavar="INT",
    # )
    # search_parser.add_argument(
    #     "--polygon",
    #     type=int,
    #     help="Polygon of the location",
    #     required=False,
    #     metavar="INT",
    # )
    # search_parser.add_argument(
    #     "--parcel",
    #     type=int,
    #     help="Parcel of the location",
    #     required=False,
    #     metavar="INT",
    # )

    # Locate command

    find_coords = subparsers.add_parser(
        "find-coords",
        help="Find geometry and metadata in the SIGPAC database from the coordinates.",
    )
    find_coords.add_argument(
        "--layer",
        choices=["parcela", "recinto"],
        help="Layer to search from",
        metavar="STRING",
        required=True,
    )
    find_coords.add_argument(
        "--lat",
        type=float,
        help="Latitude of the location",
        metavar="FLOAT",
        required=True,
    )
    find_coords.add_argument(
        "--lon",
        type=float,
        help="Longitude of the location",
        metavar="FLOAT",
        required=True,
    )
    find_coords.add_argument(
        "--crs",
        type=str,
        help="Coordinate Reference System",
        metavar="STR",
        required=False,
        default="4258"
    )

    # Anotate command

    find_data = subparsers.add_parser(
        "find-data",
        help="Find geometry and metadata in the SIGPAC database from address data."
    )
    find_data.add_argument(
        "--layer",
        choices=["parcela", "recinto"],
        help="Layer to search from",
        metavar="STRING",
        required=True,
    )
    find_data.add_argument(
        "--province",
        type=int,
        help="Province of the location",
        metavar="INT",
        required=True,
    )
    find_data.add_argument(
        "--municipality",
        type=int,
        help="Municipality of the location",
        metavar="INT",
        required=True,
    )
    find_data.add_argument(
        "--polygon",
        type=int,
        help="Polygon of the location",
        metavar="INT",
        required=True,
    )
    find_data.add_argument(
        "--parcel",
        type=int,
        help="Parcel of the location",
        metavar="INT",
        required=True,
    )
    find_data.add_argument(
        "--enclosure",
        type=int,
        help="Enclosure of the location",
        required=False,
        metavar="INT",
    )
    find_data.add_argument(
        "--aggregate",
        type=int,
        default=0,
        help="Aggregate of the location",
        metavar="INT",
    )
    find_data.add_argument(
        "--zone", type=int, default=0, help="Zone of the location", metavar="INT"
    )

    # Find command

    find_cadastral_parser = subparsers.add_parser(
        "find-cadastral",
        help="Find geometry and metadata in the SIGPAC database from cadastral reference."
    )
    find_cadastral_parser.add_argument(
        "--ref",
        type=str,
        help="Parcel's SIGPAC cadastral reference (20 chars).",
        required=True,
        metavar="STR",
    )

    # Generate command

    build_cadastral = subparsers.add_parser(
        "build-cadastral",
        help="Build  synthetic rural SIGPAC cadastral reference from search data."
    )
    build_cadastral.add_argument(
        "--province",
        type=int,
        help="Province of the location",
        metavar="INT",
        required=True,
    )
    build_cadastral.add_argument(
        "--municipality",
        type=int,
        help="Municipality of the location",
        metavar="INT",
        required=True,
    )
    build_cadastral.add_argument(
        "--polygon",
        type=int,
        help="Polygon of the location",
        metavar="INT",
        required=True,
    )
    build_cadastral.add_argument(
        "--parcel",
        type=int,
        help="Parcel of the location",
        metavar="INT",
        required=True,
    )

    return parser


def main():
    args, _ = get_parser().parse_known_args()

    match args.command:
        # case "search":
        #     from sigpac_tools.search import search
        #     import json

        #     data = {
        #         "community": args.community,
        #         "province": args.province,
        #         "municipality": args.municipality,
        #         "polygon": args.polygon,
        #         "parcel": args.parcel,
        #     }
        #     search_res = search(data)
        #     logger.info(f"Search results:\n{json.dumps(search_res, indent=2)}")
        #     return search_res

        case "find-coords":
            from sigpac_tools.locate import get_geometry_and_metadata_coords
            import json

            layer = args.layer
            lat = args.lat
            lon = args.lon
            crs = args.crs
            geometry, metadata = get_geometry_and_metadata_coords(layer, lat, lon, crs)
            logger.info(
                f"Geometry for coords ({lat}, {lon}):\n{str(json.dumps(geometry, indent=2))[:500]}\n..."
            )
            logger.info(
                f"Metadata for coords ({lat}, {lon}):\n{str(json.dumps(metadata, indent=2))[:500]}\n..."
            )
            return geometry, metadata

        case "find-data":
            from sigpac_tools.anotate import get_geometry_and_metadata_cadastral
            import json

            layer = args.layer
            
            province= args.province
            municipality= args.municipality
            polygon= args.polygon
            parcel= args.parcel
            enclosure= args.enclosure
            aggregate= args.aggregate
            zone= args.zone

            geometry, metadata = get_geometry_and_metadata_cadastral(layer, province, municipality, polygon, parcel, enclosure, aggregate, zone)
            logger.info(
                f"Geometry for data:\n{str(json.dumps(geometry, indent=2))[:500]}\n..."
            )
            logger.info(
                f"Metadata for data:\n{str(json.dumps(metadata, indent=2))[:500]}\n..."
            )
            return geometry, metadata
        
        case "find-cadastral":
            from sigpac_tools.find import find_from_cadastral_registry
            import json

            ref = args.ref
            geometry, metadata = find_from_cadastral_registry(ref)
            logger.info(
                f"Geometry for cadastral registry {ref}:\n{str(json.dumps(geometry, indent=2))[:500]}\n..."
            )
            logger.info(
                f"Metadata for cadastral registry {ref}:\n{str(json.dumps(metadata, indent=2))[:500]}\n..."
            )
            return geometry, metadata
        
        case "build-cadastral":
            from sigpac_tools.generate import build_cadastral_reference

            data = {
                "province": args.province,
                "municipality": args.municipality,
                "polygon": args.polygon,
                "parcel": args.parcel,
            }
            cadastral_ref = build_cadastral_reference(layer, data)
            logger.info(
                f"Cadastral reference generated:{cadastral_ref}"
            )
            return cadastral_ref
        case _:
            raise ValueError("Invalid command")


if __name__ == "__main__":
    main()
