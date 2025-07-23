def load_coordinates(file_path):
    coordinates = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                x, y = map(float, line.strip().split(','))
                coordinates.append((x, y))
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except ValueError:
        print("Error: Could not convert data to float. Please check the format of the coordinates.")
    return coordinates