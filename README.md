# LED Matrix Wall Sign

## Weather ([OpenWeatherMap](https://openweathermap.org/))

![](previews/weather.png)

## MBTA ([General Transit Feed Specification](https://gtfs.org/documentation/overview/))

![](previews/mbta.png)

## BlueBikes ([General Bikeshare Feed Specification](https://gbfs.org/))

![](previews/bluebikes.png)

## Make a Fish ([makea.fish](http://makea.fish/))

![](previews/fish.png)

# Development

Set up a virtual environment and install the requirements:

```bash
uv sync
# or
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Set up your configuration in matrix.toml

```bash
cp matrix.example.toml matrix.toml
# Edit matrix.toml with your preferred text editor, you'll need to at least add credentials for the services you want to use
```

Run with:

```bash
uv run main.py --simulate
# or
python3 main.py --simulate
```

# Matter pairing

Remove the existing cache with:

```
pi@matrix2:~/matrix2/matter $ sudo rm -rf .matter
```

Run it with something like:

```
pi@matrix2:~/matrix2/matter $ sudo /home/pi/.bun/bin/bun run start
```

It will print the QR code to the terminal that you can use for pairing!
