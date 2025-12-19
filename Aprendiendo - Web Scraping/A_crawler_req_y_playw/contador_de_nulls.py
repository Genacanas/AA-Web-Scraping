import json



with open("input.json", "r", encoding="utf-8") as f:
    data = json.load(f)

null_counts = 0

for item in data:
    if item.get("website") is None:
        null_counts +=1


print(f"Cantidad de nulls en 'website': {null_counts}")

efectividad = (1 -  null_counts / len(data)) * 100
print(f"Efectividad: {efectividad:.2f}%")