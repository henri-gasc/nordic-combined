import matplotlib.pyplot as plt

# times = {}
expected = {}
simulate = {}

exac = [75.2, 9.03, 17.6, 15.4, 8.17, 4.71, 12.0, 22.2, 20.9, 12.5, 17.5, 11.4, 20.4, 16.3, 13.1, 26.5]
adap = [99.4, 89.6, 91.8, 93.7, 86.7, 88.1, 84.6, 90.5, 89.3, 91.3, 83.0, 85.0, 92.1, 90.0, 89.7, 92.9]

print(sum(exac)/len(exac))
print(sum(adap)/len(adap))

plt.plot(range(1, len(exac) + 1), exac, label="Exact metric")
plt.plot(range(1, len(adap) + 1), adap, label="Adapted metric")

plt.xlabel("Race number")
plt.ylabel("Correctness rate")
plt.legend()
plt.show()

# file = "01 Men Individual Gundersen LH_5.0km Ruka 25112022_5.0"
# file = "07 Men Individual Gundersen NH_10.0km Ramsau am Dachstein 17122022_10.0"
# file = "19 Men Individual Gundersen NH_10.0km Schonach 11022023_10.0"
# file = "24 Men Individual Gundersen LH_10.0km Lahti 26032023_10.0"
# file = "02 Men Individual Gundersen LH_10.0km Ruka 25112023_10.0"
# file = "11 Men Individual Gundersen NH_10.0km Schonach 28012024_10.0"
# file = "21 Men Individual Gundersen LH_10.0km Trondheim 17032024_10.0"

# with open(f"{file}.csv") as f:
#     lines = f.read().split("\n")[:-1]

# for l in lines:
#     s = l.split(", ")
#     n = s[0]
#     # val = (int(s[1]) - 1) % 45
#     val = int(s[1])
#     # if n[:6] == "RIIBER":
#     #     if int(s[1])%45 != 1:
#     #         print(f"Problem: {l}")
#     if n in expected:
#         simulate[n].append(val)
#     else:
#         simulate[n] = [val]
#         # expected[n] = (int(s[2]) - 1) % 45
#         expected[n] = int(s[2])

# expected = {k: v for k, v in sorted(expected.items(), key=lambda item: item[1])}

# for a in expected:
#     r = simulate[a]
#     avg = sum(r) / len(r)
#     plus = max(r) - avg
#     minus = avg - min(r)
#     plt.scatter(a, expected[a])
#     plt.errorbar(a, avg, [[plus], [minus]], marker="x", markersize=10)

# plt.gca().invert_yaxis()
# plt.xticks(rotation=45, ha='right')

# name = list(times.keys())[0]
# plt.hist(times[name], bins=50, label=f"{name}")
# plt.legend()
# plt.show()
