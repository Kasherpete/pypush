# Overview
This branch is a fork of the [original Pypush](https://github.com/beeper/pypush), but this one is optimized to be used
within code and to be used programmatically, unlike the original, which has a minimal CLI.

***NOTE:*** This is under development, an actual readme may not be available for a while. Imports will also be changing
drastically. Here is a simple code sample:

### Login 1 (preferred)
```python
client = Client()
client.load_config_file('config.json')  # you can load a config file, or supply a dict when the obj is first init.
client.send_message('1234567890', 'pypush test')  # supports effects and handles
```

### Login 2
```python
client = Client()
client.login('username', 'password')  # auth code will be sent on this line.
auth_code = input('auth: ')

client.authenticate(auth_code)
client.send_message('1234567890', 'pypush test')
```

### Demo
```python
client = Client()
client.load_config_file('config.json')

client.get_handles()  # returns current handle and all handles
client.set_handle('number')  # will raise error if incorrect handle supplied
client.get_incoming_message()  # returns msg object and info within a dict
client.send_message('to', 'content')  # to param can be str or list. supports effects
```

# Changelog

- ***v0.1.3*** - Add error handling, bug fix