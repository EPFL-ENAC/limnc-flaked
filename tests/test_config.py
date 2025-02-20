import yaml
import os

def test_config():
    config_file = os.path.join(os.path.dirname(__file__), 'data', 'config.yml')
    
    with open(config_file) as f:
        config = yaml.safe_load(f)
    app = config['instruments'][0]
    assert app['name'] == 'instrument1'
    assert app['schedule']['cron'] == '0 0 * * *'
    assert app['input']['path'] == 'instrument1/data'