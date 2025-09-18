using Plots   # load plotting library

# Define x values
x = 0:0.1:10    # range from 0 to 10 in steps of 0.1
y = x           # y = x

# Plot
plot(x, y, label="y = x", xlabel="x", ylabel="y", title="Simple Plot")

# Save to PNG
savefig("line.png")

