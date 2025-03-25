import yaml
import os


def test_config():
    config_file = os.path.join(os.path.dirname(__file__), 'data', 'config.yml')

    with open(config_file) as f:
        config = yaml.safe_load(f)
    app = config['instruments'][0]
    assert app['name'] == 'instrument1'
    assert app['schedule']['interval']['value'] == 1
    assert app['schedule']['interval']['unit'] == 'minutes'
    assert app['input']['path'] == 'instrument1/data'
    app = config['instruments'][1]
    assert app['name'] == 'instrument2'
    assert app['schedule']['cron'] == '0 0 * * *'
    assert app['input']['path'] == 'instrument2/data'
