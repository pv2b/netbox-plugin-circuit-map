from extras.plugins import PluginConfig


class CircuitMapConfig(PluginConfig):
    name = 'netbox_circuit_map'
    verbose_name = 'Circuit map'
    version = '0.0.1'
    author = 'Per von Zweigbergk'
    author_email = 'pvz@pvz.pp.se'
    base_url = 'device-map'
    default_settings = {
        'device_geolocation_cf': 'geolocation',
        'cpe_device_role': 'CPE',
        'geomap_settings': {
            'attribution': 'Data by &copy; <a href="https://openstreetmap.org">OpenStreetMap</a>',
            'crs': 'EPSG3857',
            'tiles': {
                'url_template': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                'options': {
                    'subdomains': 'abc',
                }
            }
        }
    }


config = CircuitMapConfig
