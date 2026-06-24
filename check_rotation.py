#!/usr/bin/env python3
import av
import sys

video_path = sys.argv[1]
container = av.open(video_path)
stream = container.streams.video[0]

print(f"Video: {video_path}")
print(f"Dimensions: {stream.width}x{stream.height}")

# Check frames for rotation side data
print("\nChecking frame side data...")
for frame in container.decode(video=0):
    if frame.side_data:
        for side_data in frame.side_data:
            print(f"Side data: {side_data}")
            print(f"  Type: {side_data.type}")
            # Display matrix contains rotation
            if side_data.type == av.sidedata.SideData.Type.DISPLAYMATRIX:
                print(f"  >>> Found DISPLAYMATRIX")
                # Try to extract rotation
                try:
                    rotation = side_data.rotation
                    print(f"  >>> ROTATION: {rotation}°")
                except:
                    print(f"  Raw data: {bytes(side_data)}")
    break

container.close()
