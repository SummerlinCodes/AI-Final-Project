import os
import json
import matplotlib.pyplot as plt

# Load chord dictionary
with open("guitar_chord_dictionary.json", "r") as f:
    chords = json.load(f)

# Create diagrams folder
diagram_dir = "diagrams"
os.makedirs(diagram_dir, exist_ok=True)

def draw_chord(name, fingering, save_path):
    fig, ax = plt.subplots(figsize=(2, 3))
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # Vertical strings
    for i in range(6):
        ax.plot([i + 0.5, i + 0.5], [0.5, 4.5], color='black', linewidth=2)

    # Horizontal frets
    for i in range(5):
        ax.plot([0.5, 5.5], [i + 0.5, i + 0.5], color='black', linewidth=2)

    # String indicators (X, O, or dots)
    for i, fret in enumerate(fingering):
        if fret.lower() == "x":
            ax.text(i + 0.5, 4.8, 'X', ha='center', va='center', fontsize=10, color='red')
        elif fret == "0":
            ax.text(i + 0.5, 4.8, 'O', ha='center', va='center', fontsize=10, color='green')
        else:
            y = 4.5 - int(fret)
            ax.plot(i + 0.5, y + 0.5, 'o', color='black', markersize=10)

    ax.set_title(name, fontsize=12)
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()

# Generate diagrams and update JSON
for name, data in chords.items():
    fingering = data["fingering"]
    img_name = f"{name.replace(' ', '_')}.png"
    save_path = os.path.join(diagram_dir, img_name)
    draw_chord(name, fingering, save_path)
    chords[name]["diagram"] = os.path.join(diagram_dir, img_name).replace("\\", "/")

# Save updated JSON
with open("guitar_chord_dictionary_with_diagrams.json", "w") as f:
    json.dump(chords, f, indent=2)

print("✅ Diagrams generated and JSON updated.")
