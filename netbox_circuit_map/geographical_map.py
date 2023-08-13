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
        a = circuit.termination_a
        z = circuit.termination_z
        if not a or not a.site or a.site.id not in site_id_to_latlon: continue
        if not z or not z.site or z.site.id not in site_id_to_latlon: continue
        c.append({
            "site_a": a.site.id,
            "site_z": z.site.id,
            "provider": circuit.provider.name,
            "cid": circuit.cid,
            "id": circuit.id
        })

    return map_config
