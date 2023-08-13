from dcim.models import Site

from .settings import plugin_settings
from .helpers import get_connected_sites, LatLon


geomap_settings = plugin_settings['geomap_settings']


def configure_leaflet_map(map_id: str, sites: dict[Site, LatLon], show_circuits=True) -> dict:
    """Generate Leaflet map of sites and the circuits between them.
    :param map_id: initialize the map on the div with this id
    :param sites: list of target sites to display on the map
    :param show_circuits: calculate circuits between sites
    """
    site_id_to_latlon = {device.id: position for device, position in sites.items()}
    map_config = dict(**geomap_settings, map_id=map_id)
    markers: list[dict] = []
    circuits: set[frozenset[LatLon, LatLon]] = set()
    for site, position in sites.items():
        if site.tenant:
            tenant = site.tenant.name
        else:
            tenant = ""
        markers.append(dict(
            position=position,
            icon="", #FIXME
            site=dict(
                id=site.id,
                name=site.name,
                address=site.physical_address,
                url=site.get_absolute_url(),
                tenant=tenant
            )
        ))
        if show_circuits:
            for peer_site_id in get_connected_sites(site).values_list('id', flat=True).order_by():
                if peer_position := site_id_to_latlon.get(peer_site_id):
                    circuits.add(frozenset((position, peer_position)))

    map_config.update(markers=markers, circuits=[tuple(c) for c in circuits])

    return map_config
