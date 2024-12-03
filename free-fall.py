import pygame
import matplotlib.pyplot as plt
import pandas as pd

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Free-Fall Simulation: Coin Drops on All Planets")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

# Fonts
font = pygame.font.SysFont(None, 30)

# Coin properties
coin_mass = 11.5 / 1000  # Convert grams to kilograms (11.5g -> 0.0115kg)
coin = {"size": 20, "color": GOLD}

# Planetary gravities (m/s^2)
planetary_gravity = {
    "Mercury": 3.7,
    "Venus": 8.87,
    "Earth": 9.8,
    "Mars": 3.71,
    "Jupiter": 24.79,
    "Saturn": 10.44,
    "Uranus": 8.69,
    "Neptune": 11.15,
}

# Simulation constants
v0 = 0  # Initial velocity (m/s), assuming it starts from rest
y0 = 50  # Initial height (pixels)
dt = 0.1  # Time step (seconds)
scale = 20  # Pixels per meter for the simulation (scaling factor)

# Physics variables for each planet
planets_data = {
    planet: {"t": 0, "y": y0, "v": v0, "times": [], "heights": []}
    for planet in planetary_gravity.keys()
}


def draw_coin(screen, x, y, size, color):
    """Draw a coin with a given size and color."""
    pygame.draw.circle(screen, color, (x, int(y)), size)


def print_table():
    """Print the motion data for all planets in a tabular format."""
    data = []
    for planet in planetary_gravity.keys():
        planet_data = planets_data[planet]

        # If the coin has reached the ground, ensure the final time and height are added
        if planet_data["y"] <= 0:
            planet_data["times"].append(planet_data["t"])  # Final time at ground
            planet_data["heights"].append(0)  # Final height at ground

        # Ensure that we capture all times and heights for the planet
        for t, h in zip(planet_data["times"], planet_data["heights"]):
            data.append([planet, t, h])

    # Create a DataFrame for easy display in tabular format
    df = pd.DataFrame(data, columns=["Planet", "Time (s)", "Height (m)"])

    # Display the entire data directly in the console
    print(df.to_string(index=False))

    return df


def plot_graph(df):
    """Plot height vs. time for all planets."""
    plt.figure(figsize=(10, 6))
    plt.title("Height vs. Time for Different Planets")
    plt.xlabel("Time (s)")
    plt.ylabel("Height (m)")

    for planet in planetary_gravity.keys():
        planet_data = df[df["Planet"] == planet]
        plt.plot(
            planet_data["Time (s)"],
            planet_data["Height (m)"],
            label=planet,
        )

    plt.legend()
    plt.grid()
    plt.show()


def main():
    clock = pygame.time.Clock()
    running = True
    column_count = 2
    row_count = (len(planetary_gravity) + 1) // column_count
    cell_width = WIDTH // column_count
    cell_height = HEIGHT // row_count

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for idx, (planet, gravity) in enumerate(planetary_gravity.items()):
            # Calculate grid position
            row = idx // column_count
            col = idx % column_count
            x_start = col * cell_width
            y_start = row * cell_height

            # Physics update using the free fall formula
            planet_data = planets_data[planet]
            planet_data["v"] = v0 + gravity * planet_data["t"]  # Update velocity based on gravity
            planet_data["y"] = y0 + 0.5 * gravity * planet_data["t"] ** 2  # Update position based on free fall formula

            # Ensure the coin doesn't fall below the ground
            if planet_data["y"] < y_start + cell_height - 200:
                # Append height and time data for graphing
                planet_data["times"].append(planet_data["t"])
                planet_data["heights"].append(planet_data["y"] / scale)
            else:
                planet_data["y"] = y_start + cell_height - 200  # Coin reaches the ground
                planet_data["v"] = 0  # Stop updating velocity when coin reaches the ground

            # Draw the ground for the current planet
            pygame.draw.line(screen, BLACK, (x_start, y_start + cell_height - 200),
                             (x_start + cell_width, y_start + cell_height - 200), 2)

            # Draw the coin in the upper part of the section
            draw_coin(screen, x_start + cell_width // 2, planet_data["y"], coin["size"], coin["color"])

            # Draw the planet label and gravity value
            label = font.render(f"{planet} (g = {gravity:.2f} m/s²)", True, BLACK)
            screen.blit(label, (x_start + 10, y_start + 10))

            # Update time
            planet_data["t"] += dt

        # Update display
        pygame.display.flip()

        # Control frame rate
        clock.tick(30)

    pygame.quit()

    # Print table data and plot graph
    df = print_table()
    plot_graph(df)


# Run the simulation
main()
