#%% md
# **Free Fall Simulation of 20-Peso Coins on Different Planets in Our Solar System**

## Introduction
<div style="text-align: justify;">
 The study of free fall is an essential part of understanding gravitational forces and their effect on objects. Objects of the same mass, such as a coin, will fall at different rates depending on the planet's gravitational pull. Gravitational acceleration is a key factor in determining the speed at which an object falls toward the surface of a celestial body. On Earth, we are accustomed to the acceleration due to gravity being approximately 9.81 m/s². However, this value varies greatly across different planets in our solar system, influencing the rate at which objects fall.
</div>

## Planets in the Simulation:
- **Mercury**: Gravity = 3.7 m/s²
- **Venus**: Gravity = 8.87 m/s²
- **Earth**: Gravity = 9.81 m/s²
- **Mars**: Gravity = 3.71 m/s²
- **Jupiter**: Gravity = 24.79 m/s²
- **Saturn**: Gravity = 10.44 m/s²
- **Uranus**: Gravity = 8.69 m/s²
- **Neptune**: Gravity = 11.15 m/s²
- **Pluto**: Gravity = 0.62 m/s²

## How the Simulation Works:
The simulation uses the following equations to calculate the fall of a 20-Peso coin from a height of 100 meters.

### 1. Equation for Height (\(yf\)):
$$
y_f = y_0 + v_0 t + \frac{1}{2} g t^2
$$

Where:
- \(yf\) is the height of the object at any given time.
- \(y0\) is the initial height (100 meters in this case).
- \(v0\) is the initial velocity (0 m/s, since the coin is initially at rest).
- \(g\) is the gravitational acceleration for the planet.
- \(t\) is the time in seconds.

### 2. Equation for Velocity (\(vf\)):

$$
vf = v0 + g t
$$

Where:
- \(vf\) is the velocity of the object at any given time.
- \(v0\) is the initial velocity (0 m/s, since the coin is initially at rest).
- \(g\) is the gravitational acceleration for the planet.
- \(t\) is the time in seconds.

## Explanation of the Calculation Using Earth as an Example (Coin Reaching the Ground)

In this section, we will walk through the calculation for Earth, where the gravitational acceleration \(g = 9.81 \, \text{m/s}^2\), and the coin has already reached the ground, based on the previously calculated fall time of **4.51 seconds**.

### 1. Time to Reach the Ground

The formula we use to calculate the time it takes for an object to fall to the ground is derived from the equations of motion for uniformly accelerated objects under gravity.

The general equation for the motion of an object in free fall (ignoring air resistance) is:

$$
y_f = y_0 + v_0 t + \frac{1}{2} g t^2
$$

Where:
- \(y_f\) is the final height (which will be 0 when the object hits the ground),
- \(y_0\) is the initial height from which the object is dropped (in our case, 100 meters),
- \(v_0\) is the initial velocity (which is 0 m/s since the coin is dropped and not thrown),
- \(g\) is the gravitational acceleration (9.81 m/s² on Earth),
- \(t\) is the time taken for the object to reach the ground.

Since we are dropping the object from rest (\(v_0 = 0\)), the equation simplifies to:

$$
y_f = y_0 + \frac{1}{2} g t^2
$$

Now, we know that when the object hits the ground, \(y_f = 0\). Therefore, the equation becomes:

$$
0 = y_0 + \frac{1}{2} g t^2
$$

Solving for \(t\), we rearrange the equation:

$$
\frac{1}{2} g t^2 = -y_0
$$

Multiply both sides by 2 to simplify:

$$
g t^2 = -2 y_0
$$

Now, divide both sides by \(g\):

$$
t^2 = \frac{-2 y_0}{g}
$$

Finally, take the square root of both sides:

$$
t = \sqrt{\frac{2 y_0}{g}}
$$

### Why We Use This Formula

We use this formula because it allows us to directly calculate the time it takes for an object to fall from a given height (\(y_0\)) under the influence of gravity (\(g\)), assuming the object starts from rest. In our case, the initial velocity is 0, and we know the height (\(y_0 = 100 \, \text{m}\)) and gravity on Earth (\(g = 9.81 \, \text{m/s}^2\)).

By plugging these values into the formula:

$$
t = \sqrt{\frac{2 \cdot 100}{9.81}} \approx 4.51 \, \text{seconds}
$$

We find that it takes approximately **4.51 seconds** for the coin to fall from 100 meters to the ground on Earth.


###  Final Velocity Just Before Impact:

Using the calculated fall time \(t = 4.51 \, \text{seconds}\), we can now compute the final velocity just before impact using the velocity equation:

$$
v_f = v_0 + g t
$$

Substituting the values:

$$
v_f = 0 + 9.81 \cdot 4.51 = 44.23 \, \text{m/s}
$$

So, the final velocity of the coin just before impact on Earth would be **44.23 m/s**.


    # Control the frame rate
    clock.tick(60)

pygame.quit()
