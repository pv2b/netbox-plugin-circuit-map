from packaging import version

from dcim.models import Site
from circuits.models import Circuit, CircuitTermination
from django.db.models import QuerySet, Q
from ipam.models import VLAN
from netbox.settings import VERSION
from itertools import chain

from .settings import plugin_settings


NETBOX_VERSION = version.parse(VERSION)
LatLon = tuple[float, float]


def get_site_location(site: Site) -> LatLon | None:
    if site.latitude and site.longitude:
        return (float(site.latitude), float(site.longitude))

def get_connected_circuits(site: Site) -> QuerySet[Circuit]:
    return Circuit.objects.filter(Q(termination_z__site_id=site.id) | Q(termination_a__site_id=site.id))


def get_connected_sites(site: Site) -> QuerySet[Site]:
    """Get list of connected sites to the specified site (through circuits)"""
    
    # First get all circuits where we are the A or Z termination
    circuits = get_connected_circuits(site)

    # Then, get all the terminations of those circuits that isn't ourselves
    remote_terminations = CircuitTermination.objects.filter(circuit__in=circuits)

    # Return the sites of those terminations
    site_ids = remote_terminations.values_list('site')
    return Site.objects.filter(Q(id__in = site_ids) | Q(id = site.id))
