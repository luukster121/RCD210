import asyncio
import time
import winsdk.windows.media.control as wmc

async def get_now_playing():
    manager = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
    session = manager.get_current_session()
    if not session:
        return None
    info = await session.try_get_media_properties_async()
    return info.title, info.artist, info.album_title

last = None

while True:
    data = asyncio.run(get_now_playing())
    if data and data != last:
        title, artist, album = data
        print("Now Playing:")
        print("  Titel:", title)
        print("  Artiest:", artist)
        print("  Album:", album)
        print()
        last = data

    time.sleep(1)
