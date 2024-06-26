import argparse
import structlog

logger = structlog.get_logger()


def get_parser():
    parser = argparse.ArgumentParser(description="SIGPAC Tools")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    # Search command

    search_parser = subparsers.add_parser(
        "search", help="Search for a reference in the SIGPAC database"
    )
    search_parser.add_argument(
        "--community",
        type=int,
        help="Community of the location",
        required=False,
        metavar="INT",
    )
    search_parser.add_argument(
        "--province",
        type=int,
        help="Province of the location",
        required=False,
        metavar="INT",
    )
    search_parser.add_argument(
        "--municipality",
        type=int,
        help="Municipality of the location",
        required=False,
        metavar="INT",
    )
    search_parser.add_argument(
        "--polygon",
        type=int,
        help="Polygon of the location",
        required=False,
        metavar="INT",
    )
    search_parser.add_argument(
        "--parcel",
        type=int,
        help="Parcel of the location",
        required=False,
        metavar="INT",
    )

    # Locate command

    geom_parser = subparsers.add_parser(
        "geometry",
        help="Locate a geometry given the coordinates in the SIGPAC database",
    )
    geom_parser.add_argument(
        "--layer",
        choices=["parcela", "recinto"],
        help="Layer to search from",
        metavar="STRING",
        required=True,
    )
    geom_parser.add_argument(
        "--lat",
        type=float,
        help="Latitude of the location",
        metavar="FLOAT",
        required=True,
    )
    geom_parser.add_argument(
        "--lon",
        type=float,
        help="Longitude of the location",
        metavar="FLOAT",
        required=True,
    )
    geom_parser.add_argument(
        "--reference",
        type=int,
        help="Reference to search for",
        required=False,
        metavar="INT",
    )

    # Get metadata command

    annotate_parser = subparsers.add_parser(
        "get-metadata", help="Get metadata of a location in the SIGPAC database"
    )
    annotate_parser.add_argument(
        "--layer",
        choices=["parcela", "recinto"],
        help="Layer to search from",
        metavar="STRING",
        required=True,
    )
    annotate_parser.add_argument(
        "--province",
        type=int,
        help="Province of the location",
        metavar="INT",
        required=True,
    )
    annotate_parser.add_argument(
        "--aggregate",
        type=int,
        default=0,
        help="Aggregate of the location",
        metavar="INT",
    )
    annotate_parser.add_argument(
        "--zone", type=int, default=0, help="Zone of the location", metavar="INT"
    )
    annotate_parser.add_argument(
        "--municipality",
        type=int,
        help="Municipality of the location",
        metavar="INT",
        required=True,
    )
    annotate_parser.add_argument(
        "--polygon",
        type=int,
        help="Polygon of the location",
        metavar="INT",
        required=True,
    )
    annotate_parser.add_argument(
        "--parcel",
        type=int,
        help="Parcel of the location",
        metavar="INT",
        required=True,
    )
    annotate_parser.add_argument(
        "--enclosure",
        type=int,
        help="Enclosure of the location",
        required=False,
        metavar="INT",
    )

    # Find cadastral registry command

    find_parser = subparsers.add_parser(
        "find", help="Find a cadastral registry in the SIGPAC database"
    )
    find_parser.add_argument(
        "--registry",
        "-r",
        type=str,
        help="Cadastral registry to search for",
        required=True,
        metavar="STRING"
    )

    return parser


def main():
    args, _ = get_parser().parse_known_args()

    match args.command:
        case "search":
            from sigpac_tools.search import search
            import json

            data = {
                "community": args.community,
                "province": args.province,
                "municipality": args.municipality,
                "polygon": args.polygon,
                "parcel": args.parcel,
            }
            search_res = search(data)
            logger.info(f"Search results:\n{json.dumps(search_res, indent=2)}")
            return search_res

        case "geometry":
            from sigpac_tools.locate import geometry_from_coords
            import json

            layer = args.layer
            lat = args.lat
            lon = args.lon
            reference = args.reference
            geom = geometry_from_coords(layer, lat, lon, reference)
            logger.info(
                f"Geometry for coords ({lat}, {lon}):\n{json.dumps(geom, indent=2)}"
            )
            return geom

        case "get-metadata":
            from sigpac_tools.anotate import get_metadata
            import json

            layer = args.layer
            data = {
                "province": args.province,
                "aggregate": args.aggregate,
                "zone": args.zone,
                "municipality": args.municipality,
                "polygon": args.polygon,
                "parcel": args.parcel,
                "enclosure": args.enclosure,
            }
            metadata = get_metadata(layer, data)
            logger.info(f"Metadata:\n{json.dumps(metadata, indent=2)}")
            return metadata
        case "find":
            from sigpac_tools.find import find_from_cadastral_registry
            import json

            registry = args.registry
            geom, metadata = find_from_cadastral_registry(registry)
            logger.info(
                f"Geometry for cadastral registry {registry}:\n{json.dumps(geom, indent=2)}"
            )
            logger.info(
                f"Metadata for cadastral registry {registry}:\n{json.dumps(metadata, indent=2)}"
            )
            return geom, metadata
        case _:
            raise ValueError("Invalid command")


if __name__ == "__main__":
    main()
