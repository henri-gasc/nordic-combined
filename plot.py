import matplotlib.pyplot as plt

# times = {}
expected = {}
simulate = {}

exac = [71.529, 9.375, 14.5, 22.0, 10.0, 8.5217, 9.8222, 21.333, 23.282, 14.1, 13.0, 11.632, 18.082, 12.348, 12.298, 22.133]
adap = [99.035, 89.801, 89.941, 93.778, 85.866, 87.84, 83.024, 90.444, 88.271, 90.721, 83.428, 84.395, 92.07, 89.82, 89.22, 92.099]

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
# file = "01 Ruka 30112024 S24_25_10.0"
# file = "02 Lillehammer 06122024 S24_25_10.0"
# file = "03 Ramsau 19202024 S24_25_10.0"
# file = "04 Schonach 18012025 S24_25_10.0"
# file = "07 Otepää 07022025 S24_25_10.0"
# file = "08 Oslo 15032025 S24_25_10.0"
# file = "09 Lahti 21032025 S24_25_10.0"
# file = "00 Japan 01112024_10.0"

with open(f"races/{file}.csv") as f:
    lines = f.read().split("\n")[:-1]

for l in lines:
    s = l.split(", ")
    n = s[0]
    # val = (int(s[1]) - 1) % 45
    val = int(s[1])
    # if n[:6] == "RIIBER":
    #     if int(s[1])%45 != 1:
    #         print(f"Problem: {l}")
    if n in expected:
        simulate[n].append(val)
    else:
        simulate[n] = [val]
        # expected[n] = (int(s[2]) - 1) % 45
        expected[n] = int(s[2])

expected = {k: v for k, v in sorted(expected.items(), key=lambda item: item[1])}

for a in expected:
    r = simulate[a]
    avg = sum(r) / len(r)
    plus = max(r) - avg
    minus = avg - min(r)
    # plt.scatter(a, expected[a])
    plt.errorbar(a, avg, [[plus], [minus]], marker="x", markersize=10)

plt.gca().invert_yaxis()
plt.xticks(rotation=45, ha="right")

# name = list(times.keys())[0]
# plt.hist(times[name], bins=50, label=f"{name}")
# plt.legend()
plt.show()
