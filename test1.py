import numpy as np
import similaritymeasures
import matplotlib.pyplot as plt

# Generate random experimental data
x = np.random.random(5)
y = np.random.random(5)
z = np.random.random(5)
exp_data = np.zeros((5, 3))

exp_data[:, 0] = x * 10
exp_data[:, 1] = y * 10
exp_data[:, 2] = z * 10

subz = np.array([
		z,
		z,
		z,
		z,
		z,
		z,
		z,
		z,
		z,
		z,
	])
print(subz)
print(exp_data)
# Generate random numerical data
xx = np.random.random(100)
yy = np.random.random(100)
zz = np.random.random(100)
num_data = np.zeros((100, 3))
num_data[:, 0] = xx* 10
num_data[:, 1] = yy* 10
num_data[:, 2] = zz* 10

subzz = np.array([
		zz,
		zz,
		zz,
		zz,
		zz,
		zz,
		zz,
		zz,
		zz,
		zz,
	])

# quantify the difference between the two curves using PCM
pcm = similaritymeasures.pcm(exp_data, num_data)

# quantify the difference between the two curves using
# Discrete Frechet distance
df = similaritymeasures.frechet_dist(exp_data, num_data)

# quantify the difference between the two curves using
# area between two curves
area = similaritymeasures.area_between_two_curves(exp_data, num_data)

# quantify the difference between the two curves using
# Curve Length based similarity measure
cl = similaritymeasures.curve_length_measure(exp_data, num_data)

# quantify the difference between the two curves using
# Dynamic Time Warping distance
dtw, d = similaritymeasures.dtw(exp_data, num_data)

# print the results
print(pcm, df, area, cl, dtw)

# plot the data
fig = plt.figure()
ax1 = fig.add_subplot(111, projection='3d') 

ax1.plot_wireframe(x,y,subz)
ax1.plot_wireframe(xx,yy,subzz,color='deeppink')
ax1.set_xlabel('x')
ax1.set_xlabel('y')
ax1.set_xlabel('z')

# plt.plot(exp_data[:, 0], exp_data[:, 1], exp_data[:, 2])
# plt.plot(num_data[:, 0], num_data[:, 1], num_data[:, 2])
plt.show()