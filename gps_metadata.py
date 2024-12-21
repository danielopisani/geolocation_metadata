import os
import csv
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_gps_info(image_path):
    """Extract GPSInfo metadata from an image."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if not exif_data:
            return {}

        gps_info = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'GPSInfo':
                for gps_tag_id, gps_value in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag] = gps_value
                break
        return gps_info
    except Exception as e:
        print(f"Error reading GPSInfo data from {image_path}: {e}")
        return {}

def parse_gps_coordinate(coordinate):
    """Split GPS coordinate into degrees, minutes, and seconds."""
    try:
        if coordinate and isinstance(coordinate, (list, tuple)) and len(coordinate) == 3:
            degrees = coordinate[0]
            minutes = coordinate[1]
            seconds = coordinate[2]
            return degrees, minutes, seconds
    except Exception as e:
        print(f"Error parsing GPS coordinate: {e}")
    return '', '', ''

def calculate_decimal(degree, minutes, seconds):
    """Calculate decimal representation of GPS coordinates."""
    try:
        return float(degree) + (float(minutes) / 60) + (float(seconds) / 3600)
    except Exception as e:
        print(f"Error calculating decimal value: {e}")
        return ''

def write_gps_to_csv(directory, output_csv):
    """Read GPSInfo metadata from all .jpg images in a directory and save to a CSV file."""
    try:
        excluded_keys = {'GPSAltitudeRef', 'GPSVersionID'}
        all_gps_keys = set()
        gps_data_list = []

        # Collect all GPS keys and data
        for filename in os.listdir(directory):
            if filename.lower().endswith('.jpg'):
                image_path = os.path.join(directory, filename)
                gps_info = get_gps_info(image_path)
                if gps_info:
                    all_gps_keys.update(gps_info.keys())
                    gps_data_list.append((filename, gps_info))

        all_gps_keys = sorted(all_gps_keys - excluded_keys)
        if 'GPSLatitude' in all_gps_keys:
            all_gps_keys.remove('GPSLatitude')
            all_gps_keys.extend(['GPSLatitudeDegree', 'GPSLatitudeMinutes', 'GPSLatitudeSeconds', 'GPSLatitudeDecimal'])
        if 'GPSLongitude' in all_gps_keys:
            all_gps_keys.remove('GPSLongitude')
            all_gps_keys.extend(['GPSLongDegree', 'GPSLongMinutes', 'GPSLongSeconds', 'GPSLongitudeDecimal'])

        with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header row
            headers = ['Image Name'] + all_gps_keys
            writer.writerow(headers)

            # Write data rows
            for filename, gps_info in gps_data_list:
                row = [filename]
                gps_lat_degree, gps_lat_minutes, gps_lat_seconds = '', '', ''
                gps_long_degree, gps_long_minutes, gps_long_seconds = '', '', ''
                for key in all_gps_keys:
                    if key in ['GPSLatitudeDegree', 'GPSLatitudeMinutes', 'GPSLatitudeSeconds']:
                        degrees, minutes, seconds = parse_gps_coordinate(gps_info.get('GPSLatitude'))
                        if key == 'GPSLatitudeDegree':
                            gps_lat_degree = degrees
                            row.append(degrees)
                        elif key == 'GPSLatitudeMinutes':
                            gps_lat_minutes = minutes
                            row.append(minutes)
                        elif key == 'GPSLatitudeSeconds':
                            gps_lat_seconds = seconds
                            row.append(seconds)
                    elif key == 'GPSLatitudeDecimal':
                        decimal_value = calculate_decimal(gps_lat_degree, gps_lat_minutes, gps_lat_seconds)
                        row.append(decimal_value)
                    elif key in ['GPSLongDegree', 'GPSLongMinutes', 'GPSLongSeconds']:
                        degrees, minutes, seconds = parse_gps_coordinate(gps_info.get('GPSLongitude'))
                        if key == 'GPSLongDegree':
                            gps_long_degree = degrees
                            row.append(degrees)
                        elif key == 'GPSLongMinutes':
                            gps_long_minutes = minutes
                            row.append(minutes)
                        elif key == 'GPSLongSeconds':
                            gps_long_seconds = seconds
                            row.append(seconds)
                    elif key == 'GPSLongitudeDecimal':
                        decimal_value = calculate_decimal(gps_long_degree, gps_long_minutes, gps_long_seconds)
                        row.append(decimal_value)
                    else:
                        row.append(gps_info.get(key, ''))
                writer.writerow(row)

        print(f"GPSInfo metadata saved to {output_csv}")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

if __name__ == "__main__":
    directory = input("Enter the directory containing .jpg images: ").strip()
    output_csv = input("Enter the output CSV file name (e.g., gps_metadata.csv): ").strip()

    if not os.path.isdir(directory):
        print(f"The specified directory does not exist: {directory}")
    else:
        write_gps_to_csv(directory, output_csv)
