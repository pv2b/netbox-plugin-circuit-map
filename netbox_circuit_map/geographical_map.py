from dcim.models import Site
from circuits.models import Circuit

from .settings import plugin_settings
from .helpers import get_connected_sites, LatLon


geomap_settings = plugin_settings['geomap_settings']


def configure_leaflet_map(map_id: str, sites: dict[Site, LatLon], circuits: list[Circuit]) -> dict:
    """Generate Leaflet map of sites and the circuits between them.
    :param map_id: initialize the map on the div with this id
    :param sites: list of target sites to display on the map
    :param show_circuits: calculate circuits between sites
    """
    site_id_to_latlon = {site.id: position for site, position in sites.items()}
    map_config = dict(**geomap_settings, map_id=map_id)
    markers: list[dict] = []
    circuits2 = []
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
        if circuits:
            for circuit in circuits:
                if not circuit.termination_a or not circuit.termination_a.site: continue
                if not circuit.termination_z or not circuit.termination_z.site: continue

                a_id = circuit.termination_a.site.id
                z_id = circuit.termination_z.site.id

                if a_id not in site_id_to_latlon: continue
                if z_id not in site_id_to_latlon: continue

                a_latlon = site_id_to_latlon[a_id]
                z_latlon = site_id_to_latlon[z_id]
                circuits2.append({
                    "coords": (a_latlon, z_latlon),
                    "provider": circuit.provider.name,
                    "id": circuit.cid
                })

    map_config.update(markers=markers, circuits=circuits2)

    return map_config
