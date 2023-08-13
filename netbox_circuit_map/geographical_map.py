from dcim.models import Site
from circuits.models import Circuit

from .settings import plugin_settings
from .helpers import get_connected_sites, LatLon


geomap_settings = plugin_settings['geomap_settings']


def configure_leaflet_map(map_id: str, sites: dict[Site, LatLon], circuits: list[Circuit]) -> dict:
    """Generate Leaflet map of sites and the circuits between them.
    :param map_id: initialize the map on the div with this id
    :param sites: list of target sites to display on the map
    :param circuits: list of circuiits to display on the map
    """
    site_id_to_latlon = {site.id: position for site, position in sites.items()}
    map_config = dict(**geomap_settings, map_id=map_id)
    s = map_config['sites'] = {}
    c = map_config['circuits'] = []
    for site, position in sites.items():
        if site.tenant:
            tenant = site.tenant.name
        else:
            tenant = ""
        s[site.id] = dict(
            position=position,
            icon="", #FIXME
            site=dict(
                id=site.id,
                name=site.name,
                address=site.physical_address,
                url=site.get_absolute_url(),
                tenant=tenant,
                latitude=site.latitude,
                longitude=site.longitude
            )
        )

    for circuit in circuits or []:
        if not circuit.termination_a or not circuit.termination_a.site: continue
        if not circuit.termination_z or not circuit.termination_z.site: continue

        c.append({
            "site_a": circuit.termination_a.site.id,
            "site_z": circuit.termination_z.site.id,
            "provider": circuit.provider.name,
            "id": circuit.cid
        })

    return map_config
